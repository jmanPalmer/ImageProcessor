import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QLabel, QPushButton, QFileDialog
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

#The main application window, will display everything
class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__() #subclass of QMainWindow, allow it to handle its own initializations
        self.setWindowTitle("PyQt image processor") #Sets the title of the window for our application
        self.setMinimumSize(600, 600) #The minimum size it opens up to, it will open up with these dimensions
        
        #Create viewing widget and initialize UI
        self.viewer = viewingWidget() #Set our viewer varriable to an instance of our viewing widget class
        self.viewer.init_ui() #Get the viewer to initialize its user interface
        self.setCentralWidget(self.viewer) #Set our viewing widget to be the central widget since its the main attraction of our current application
        
        #Add menu bar with load button
        self.create_menu_bar()#call the defined function below to create a menu

    #Function that creates the menu bar for our main window
    def create_menu_bar(self):
        menubar = self.menuBar() #uses built in function for creation of menu bar by QMainWindow. It either returns the existing menu bar if it already exists or creates a new one
        file_menu = menubar.addMenu("File") #.addMenu() is a menuBar function that adds an option to your existing menu bar
        load_action = file_menu.addAction("Load Image") #addAction(), adds a drop down option or action to our menuBar option
        load_action.triggered.connect(self.load_image_dialog) #.triggered is a signal that executes if we press on something (Our menu options action) and .connect() links a signal to a function
    
    #simple function for loading in a selected file from explorer by getting the file path and using the .load_image function (More on this below)
    def load_image_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)") #uses the QFileDialog class and its function getOpenFileName() where we pass its parent widget(in our case the main window), caption, directory and then the filter for which files we wish to see (Of course image types only)
        if file_path: #if we successfully get a file path use our viewer widgets built in load_image function to display the image
            self.viewer.load_image(file_path)

#widget that will display an image once its read in, subclass of QWidget
class viewingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.image_label = None #Place holder label for when the image isnt loaded in

    #initialize the user interface
    def init_ui(self):
        layout = QVBoxLayout() #could pick any layout really but with this one we can vertically arrange widgets vertically (the v in QV.. is vertical)
        self.image_label = QLabel() #We use QLabel here as it is a class that can display non editable content like text and an image. NOTE this is a widget not just text or an image
        self.image_label.setAlignment(Qt.AlignCenter) #use QLabels built in function to align our label to the center of our QLabel Widget
        self.image_label.setStyleSheet("background-color: #f0f0f0;") #styling for text
        self.set_placeholder() #call our set_placeholder function, this basically gives us the text ("No Image loaded")
        layout.addWidget(self.image_label) #now we finally add the image viewing widget to our layout
        self.setLayout(layout) #.setLayout() applies a layout to a widget
    
    def set_placeholder(self):
        """Display placeholder text when no image is loaded"""
        font = QFont() #QFont() represents a font object, not necessarily a widget, used to customize how text appears
        font.setPointSize(14) #settings for our text to be displayed
        self.image_label.setFont(font)
        self.image_label.setText("No image loaded")
    
    #Function in charge of actually displaying the image
    def load_image(self, image_path):
        """Load and display an image from file path"""
        pixmap = QPixmap(image_path) #create a QPixmap instance, QPixmap represents an image. It essentially loads image file from file path into memory, stores image data in an optimized format for display and can be manipulated before displaying
        self.image_label.setPixmap(pixmap.scaledToWidth(400, Qt.SmoothTransformation)) #setPixmap is a QPixmap helper function that loads our image in

if __name__ == "__main__":
    app = QApplication([])
    win = mainWindow()
    win.show()
    sys.exit(app.exec())


'''
THE BASIC IDEA (SUMMARY OF WHAT NEEDS TO BE DONE WHEN I MAKE MY VERSION (Probably tomorrow so I can properly test myself))

- Needs a QApplication to build off of, this is pretty much what 'runs' the application (not visible or a widget)
- Need a main window that actually displays
    -will have a menu bar to preform operations and a viewing widget
-Need a viewing widget that will either display the text ("No image loaded") or the loaded image itself, use QPixmap
- We can create subclasses of existing widget classes to add our own functions and properties onto them
  (ie viewingWidget being a subclass of QWidget)

**SOMETHING TO NOTE FOR THE FUTURE:
- since eventually we will be manipulating the images we can actually manipulate the pixel data loaded in from QPixmap
    -Convert QPixmap to QImage for easier pixel access (ie: image = pixmapObject.toImage() will give us a QImage instance)
    -or we can convert to NumPy array for better image processing (Convert to RGBA format via converting to QImage object and getting its properties stored in NumPy varriables)

'''