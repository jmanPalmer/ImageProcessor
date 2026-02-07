import sys
from PyQt5.QtWidgets import (QWidget, QApplication, QMainWindow, QMenu,
                              QAction, QFileDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider) 
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap, QImage
import numpy as np
import cv2

#Controls everything, will house all of the 'global' variables
class mainWindowWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt Image Processor")
        self.viewer = viewingWidget(parent=self) #this is going to be the widget that actually displays the image
        self.createMenu()
        self.setCentralWidget(self.viewer) #set the image as our central widget
        self.setMinimumSize(800,600)

    def createMenu(self):
        menuBar = self.menuBar()
        fileMenuOption = QMenu("File", self) #file option with the mainwindow being the parent
        openImageAction = QAction("Open Image", self)
        openImageAction.triggered.connect(self.openImage) #Will cause it to open file explorer to get the user to select an image        
        fileMenuOption.addAction(openImageAction)
        menuBar.addMenu(fileMenuOption)

    def openImage(self):
        #Before simply doing QFileDialog.getOpenFileName(self) did not work because it just returns a tuple which cant be used by QPixmap, expects a string for file path or QImage
        #so we must pass the arguments or we get a tuple (I dont know why but copilot was just not able to explain why specifically but just pass these arguments)
        filePath, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.bmp);;All Files (*)") 
        if filePath:
            self.viewer.loadImage(filePath) #load the image in our image viewing widget
            
#definition of a widget that will display an image
class viewingWidget(QWidget):
    def __init__(self, parent= None):
        super().__init__(parent)
        self.layout = QHBoxLayout()
        self.imData = None #the pixel data we are going to use with opencv2
        self.mainWin = parent #reference to the main window and its variables
        self.hasImage = False

        #the widget that will hold most if not all of the functions to apply to our image
        self.funWid = functionWidget(parent=self)
        self.funWid.setFixedWidth(200)
        self.layout.addWidget(self.funWid)

        #intialize a default state for our UI (display no image loaded yet)
        self.imgLabel = QLabel("No Image loaded",self)
        self.imgLabel.setAlignment(Qt.AlignCenter)
        self.imgLabel.setScaledContents(True) #scales to show the entirety of larger images
        self.layout.addWidget(self.imgLabel)
        
        self.setLayout(self.layout) #apply the layout to our viewing widget

    #using QPixmap to load in our image and display it by updating our label varriable
    def loadImage(self,imgPath):
        pixMap = QPixmap(imgPath)
        if pixMap:

            #want to first convert to a format that opencv2 can use and save it
            qimage = pixMap.toImage() #get a QImage from pixMap. Need to do this because it becomes memory accessible
            qimage = qimage.convertToFormat(QImage.Format_RGB888) #force a known pixel format, qimage could be any format, RGB888 means 3 bytes per pixel and RGB format
            width = qimage.width() #get the dimensions/shape of the image. Need this to construct the numpy array (numOfPix = height*width duh)
            height = qimage.height() 
            ptr = qimage.constBits() #pointer to the raw pixel buffer, like a void *pointer
            ptr.setsize(height * width * 3) #tells us how big the buffer is, since python does not know how much memory the pointer refers to. each pixel has 3 values and there are w*h pixels so total memory is w*h*3
            arr= np.array(ptr).reshape(height, width, 3) #create our RGB array
            self.imData =  cv2.cvtColor(arr, cv2.COLOR_RGB2BGR) #convert from RGB to BGR(this is whats used in opencv)

            #display the image and toggle our hasImage flag
            self.imgLabel.setPixmap(pixMap)
            self.hasImage = True

    #sharpen with opencv2 function and then create a QImage of the resulting change and then QPixmap to update
    def applySharpen(self, ker):
        sharpened_image = cv2.filter2D(self.imData, -1, ker) #apply the image sharpen with our newly adjusted kernel
        rgb = cv2.cvtColor(sharpened_image, cv2.COLOR_BGR2RGB) #convert from BGR (opencv) to RGB (pyqt QImage)
        h,w,ch = rgb.shape #get the dimensions of our Numpy Array (heigh, width, channel)
        qimg = QImage(rgb.data, w,h,ch*w, QImage.Format_RGB888) #create a QImage by using our numpy array as data with our width and heigh values, how many bytes per line (channel * width since we have 3 values in each pixel and width number of pixels per line)
        pix = QPixmap.fromImage(qimg) #create a new QPixmap with our new data
        self.imgLabel.setPixmap(pix) #update our image label with this new pixmap
        
#the widget that the user will to use to use all or most of our image altering functions
#main window handles the creation of its functions so that the functions can update the variables kept in 
#main window
class functionWidget(QWidget):
    def __init__(self, parent= None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.setSpacing(6)
        self.layout.setAlignment(Qt.AlignTop)
        self.viewingWid = parent 
        self.mainWin = parent.mainWin

        #initialize image sharpening tool
        self.currentSharpenVal = 0 #need this for when we call sharpenSliderChance in the strength changing function
        self.currentSharpenStrengthVal = 1 #need this to know how large our kernel matrix should be when sharpenSliderChange is called
        self.sharpenSlider, self.SharpenValueLabel = self.createSlider("Image Sharpening", self.sharpenSliderChange, 0, 100)
        self.sharpenStrengthSlider, self.sharpenStrengthLabel = self.createSlider("Sharpening Strength", self.sharpenStrengthChange, 1, 5)

        self.setLayout(self.layout)

    #function to initialize a slider, default values for min and max will be 0 and 100 unless specified otherwise
    def createSlider(self, name, actionFunc, min=0, max=100):
        label = QLabel(name,self)
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label)

        slider = QSlider(self) #define slider, will reside in the function widget in our viewer
        slider.setOrientation(Qt.Horizontal)
        slider.setMinimum(min)
        slider.setMaximum(max)
        slider.valueChanged.connect(actionFunc)
        self.layout.addWidget(slider) #add the slider to the function widget in viewer

        valueLabel = QLabel(f"{min}")
        valueLabel.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(valueLabel)

        return slider, valueLabel

    #apply the changes of the slider to sharpen or unsharpen the image
    def sharpenSliderChange(self, val):
        n = (self.currentSharpenStrengthVal*2) + 1 #for nxn kernel matrix, n must always be odd, for me I'm using a range of 3,5,7,9,11
        self.currentSharpenVal = val #will need to this so we can update the image when the strength is changed as well
        outerValues = -(val/100)     #outer will be at most -1 and at 0 we want a normal image

        #initialize kernel along with helper variables
        kernel = np.zeros((n, n))
        center = (n-1)//2
        counter = 0

        #utilize manhattan distance to determine if the entry should be -outerValue or 0 because with the laplacian kernel
        #entries that are (n-1)/2 manhattan distance away from the center should be -outerValue
        #in the end we want the weight of all the outervalues + inner value to equal 1
        for i in range(n):
            verticalDisp = abs(center-i) #center row value subtracted by the current row value
            for j in range(n):
                horizontalDisp = abs(center-j)
                mannHattanDist = verticalDisp + horizontalDisp
                if mannHattanDist<=center:
                    kernel[i,j] = outerValues
                    counter+= 1

        #want our center to make it so that everything sums up to 1 (weight wise), initial formula doesnt work as if the kernels weights dont sum up to 1, it becomes pitch black
        kernel[center,center] = 1+ (-1 * (counter * outerValues))

        #kernel = np.array([[0, outerValues, 0], [outerValues, innerValue, outerValues], [0, outerValues, 0]]) 
        self.SharpenValueLabel.setText(f"{val}")

        #if there is image data, we apply the tranformation to its data and update the viewer
        if self.viewingWid.hasImage:
            self.viewingWid.applySharpen(kernel)

    #simple function that handles the changing of the sharpen strength (radius of the kernel)
    def sharpenStrengthChange(self,val):

        self.currentSharpenStrengthVal = val
        self.sharpenStrengthLabel.setText(f"{val}")
        self.sharpenSliderChange(self.currentSharpenVal) #call the sharpen applying function to apply whenever strength is changed as well



if __name__ == "__main__" :

    app = QApplication(sys.argv)
    win = mainWindowWidget()
    win.show()

    sys.exit(app.exec())


