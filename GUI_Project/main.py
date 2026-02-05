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

        self.slider = None
        self.SharpenValueLabel = None

        self.initSharpenSlider()
        self.setLayout(self.layout)

    #initialize the slider that handles the sharpening of our image, will be a function with the range 0-1
    def initSharpenSlider(self):

        label = QLabel("Image Sharpening",self)
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label)

        self.slider = QSlider(self) #define slider, will reside in the function widget in our viewer
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.valueChanged.connect(self.sharpenSliderChange)
        self.layout.addWidget(self.slider) #add the slider to the function widget in viewer

        self.SharpenValueLabel = QLabel("0")
        self.SharpenValueLabel.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.SharpenValueLabel)

    #apply the changes of the slider to sharpen or unsharpen the image
    def sharpenSliderChange(self, val):
        outerValues = -(val/100) #outer will be at most -1 and at 0 we want a normal image
        innerValue = 4*(val/100) + 1 #we want a max value of 5 and a minimum value of 1 (going with 5 for now as this is what I found to be used most often online)
        kernel = np.array([[0, outerValues, 0], [outerValues, innerValue, outerValues], [0, outerValues, 0]]) #create the kernel to be applied to each pixel to sharpen
        self.SharpenValueLabel.setText(f"{val}")

        #if there is image data, we apply the tranformation to its data and update the viewer
        if self.viewingWid.hasImage:
            self.viewingWid.applySharpen(kernel)



if __name__ == "__main__" :

    app = QApplication(sys.argv)
    win = mainWindowWidget()
    win.show()

    sys.exit(app.exec())


