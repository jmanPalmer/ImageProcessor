import sys
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QMenu, QAction, QFileDialog, QVBoxLayout, QLabel 
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap, QImage



class mainWindowWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt Image Processor")
        self.viewer = viewingWidget() #this is going to be the widget that actually displays the image
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
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        #intialize a default state for our UI (display no image loaded yet)
        self.label = QLabel("No Image loaded",self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        self.setLayout(layout) #apply the layout to our viewing widget

    #using QPixmap to load in our image and display it by updating our label varriable
    def loadImage(self,imgPath):
        pixMap = QPixmap(imgPath)
        if pixMap:
            self.label.setPixmap(pixMap)


if __name__ == "__main__" :

    app = QApplication(sys.argv)
    win = mainWindowWidget()
    win.show()

    sys.exit(app.exec())