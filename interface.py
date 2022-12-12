# importing required libraries
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import twophase.solver  as sv # Good for Python /Raspberry (hhttps://github.com/hkociemba/RubiksCube-TwophaseSolver

from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *


# To send information to arduino
import serial
import time
import sys
import os

#from PySide6.QtGui import QtMultimedia
from PySide6.QtMultimediaWidgets import QGraphicsVideoItem
from PySide6.QtCore import QDate, QDir, QStandardPaths, Qt, QUrl, Slot
from PySide6.QtGui import QAction, QGuiApplication, QDesktopServices, QIcon
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel,
	QMainWindow, QPushButton, QTabWidget, QToolBar, QVBoxLayout, QWidget)
from PySide6.QtMultimedia import (QCamera, QImageCapture,
								  QCameraDevice, QMediaCaptureSession,
								  QMediaDevices)
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import Qt, Signal, QBuffer, QRectF


class ImageView(QWidget):
	def __init__(self, previewImage, fileName):
		super().__init__()

		self._file_name = fileName

		main_layout = QVBoxLayout(self)
		self._image_label = QLabel()
		self._image_label.setPixmap(QPixmap.fromImage(previewImage))
		main_layout.addWidget(self._image_label)

		top_layout = QHBoxLayout()
		self._file_name_label = QLabel(QDir.toNativeSeparators(fileName))
		self._file_name_label.setTextInteractionFlags(Qt.TextBrowserInteraction)

		top_layout.addWidget(self._file_name_label)
		top_layout.addStretch()
		copy_button = QPushButton("Copy")
		copy_button.setToolTip("Copy file name to clipboard")
		top_layout.addWidget(copy_button)
		copy_button.clicked.connect(self.copy)
		launch_button = QPushButton("Launch")
		launch_button.setToolTip("Launch image viewer")
		top_layout.addWidget(launch_button)
		launch_button.clicked.connect(self.launch)
		main_layout.addLayout(top_layout)

	@Slot()
	def copy(self):
		QGuiApplication.clipboard().setText(self._file_name_label.text())

	@Slot()
	def launch(self):
		QDesktopServices.openUrl(QUrl.fromLocalFile(self._file_name))


class MainCameraWindow(QWidget):
	QR_SIZE = 0.35   # Size of rectangle for QR capture
	next_ready = Signal(bool)

	def __init__(self):
		super().__init__()

		self._capture_session = None
		self._camera = None
		self._camera_info = None
		self._image_capture = None
		self.rectangle = None

		available_cameras = QMediaDevices.videoInputs()
		if available_cameras:


			self._camera_info = available_cameras[0]
			self._camera = QCamera(self._camera_info)
			self._camera.errorOccurred.connect(self._camera_error)
			self._image_capture = QImageCapture(self._camera)
			self._image_capture.imageCaptured.connect(self.image_captured)


			self.layout = QVBoxLayout()
			self._camera_viewfinder = QGraphicsVideoItem()
			self.scene = QGraphicsScene()
			self.view = QGraphicsView(self.scene)
			self.view.setMinimumSize(720, 405)
			self.view.setFrameStyle(0)
			self.scene.addItem(self._camera_viewfinder)
			self.layout.addWidget(self.view)
			self._camera_viewfinder.nativeSizeChanged.connect(self.video_size_changed)

			#self._tab_widget = QTabWidget()
			#self._tab_widget.setLayout(self.layout)
			#self.setCentralWidget(self._tab_widget)
			#self._camera_viewfinder = QVideoWidget()
			#self._tab_widget.addTab(self._camera_viewfinder, "Viewfinder")

			self.wnd = QWidget(self)
			self.wnd.setLayout(self.layout)
			self.setCentralWidget(self.wnd)


			self._image_capture.imageSaved.connect(self.image_saved)
			self._image_capture.errorOccurred.connect(self._capture_error)
			self._capture_session = QMediaCaptureSession()
			self._capture_session.setCamera(self._camera)
			self._capture_session.setImageCapture(self._image_capture)

		self._current_preview = QImage()

		tool_bar = QToolBar()
		self.addToolBar(tool_bar)

		file_menu = self.menuBar().addMenu("&File")
		shutter_icon = QIcon(os.path.join(os.path.dirname(__file__),
							"shutter.svg"))

		# Add Take Picture Actionn and Placement
		self._take_picture_action = QAction(shutter_icon, "&Take Picture", self,
											shortcut="Ctrl+T",
											triggered=self.take_picture)
		self._take_picture_action.setToolTip("Take Picture")
		file_menu.addAction(self._take_picture_action)
		tool_bar.addAction(self._take_picture_action)

		# Add EXIT Action
		exit_action = QAction(QIcon.fromTheme("application-exit"), "E&xit",
							  self, shortcut="Ctrl+Q", triggered=self.close)
		file_menu.addAction(exit_action)

		# Add Solve Cube Action and Placement
		self.solve_cube = QAction(shutter_icon, "&Solve Cube", self,
											shortcut="Ctrl+K",
											triggered=self.solve_cube_action)
		self.solve_cube.setToolTip("Solve Cube")
		file_menu.addAction(self.solve_cube)
		tool_bar.addAction(self.solve_cube)



		#self._tab_widget = QTabWidget()
		#self.setCentralWidget(self._tab_widget)

		#self._camera_viewfinder = QVideoWidget()
		#self._tab_widget.addTab(self._camera_viewfinder, "Viewfinder")

		if self._camera and self._camera.error() == QCamera.NoError:
			name = self._camera_info.description()
			self.setWindowTitle(f"Rubiks Solver Auto Detector ({name})")
			self.show_status_message(f"Starting: '{name}'")
			self._capture_session.setVideoOutput(self._camera_viewfinder)
			self._take_picture_action.setEnabled(self._image_capture.isReadyForCapture())
			self._image_capture.readyForCaptureChanged.connect(self._take_picture_action.setEnabled)
			self._camera.start()
		else:
			self.setWindowTitle("Rubiks Solver Auto Detector")
			self._take_picture_action.setEnabled(False)
			self.show_status_message("Camera unavailable")


	# ====================================================================================================
	def video_size_changed(self, _size):
		self.resizeEvent(None)

	# Take QImage or QRect (object with 'width' and 'height' properties and calculate position and size
	# of the square with side of self.QR_SIZE from minimum of height or width
	def calculate_center_square(self, img_rect) -> QRectF:
		a = self.QR_SIZE * min(img_rect.height(), img_rect.width())   # Size of square side
		x = (img_rect.width() - a) / 2         # Postion of the square inside rectangle
		y = (img_rect.height() - a) / 2
		if type(img_rect) != QImage:   # if we have a bounding rectangle, not an image
			x += img_rect.left()       # then we need to shift our square inside this rectangle
			y += img_rect.top()
		return QRectF(x, y, a, a)

	def resizeEvent(self, event):
		bounds = self.scene.itemsBoundingRect()
		self.view.fitInView(bounds, Qt.KeepAspectRatio)
		if self.rectangle is not None:
			self.scene.removeItem(self.rectangle)
		pen = QPen(Qt.green)
		pen.setWidth(0)
		pen.setStyle(Qt.DotLine)
		self.rectangle = self.scene.addRect(self.calculate_center_square(bounds), pen)
		self.view.centerOn(0, 0)
		self.view.raise_()

	# ====================================================================================================

	def show_status_message(self, message):
		self.statusBar().showMessage(message, 5000)

	def closeEvent(self, event):
		if self._camera and self._camera.isActive():
			self._camera.stop()
		event.accept()

	def next_image_file_name(self):
		#pictures_location = QStandardPaths.writableLocation(QStandardPaths.PicturesLocation)
		pictures_location = os.path.join(os.getcwd(),"Photos/")
		date_string = QDate.currentDate().toString("yyyyMMdd")
		pattern = f"{pictures_location}/pyside6_camera_{date_string}_{{:03d}}.jpg"
		print(pictures_location)
		n = 1
		while True:
			result = pattern.format(n)
			if not os.path.exists(result):
				return result
			n = n + 1
		return None

	def solve_cube_action(self):
		self.cube_window = Window()
		#self.hide()
		self.cube_window.show()


	@Slot()
	def take_picture(self):
		self._current_preview = QImage()
		self._image_capture.captureToFile(self.next_image_file_name())

	@Slot(int, QImage)
	def image_captured(self, id, previewImage):
		self._current_preview = previewImage

	@Slot(int, str)
	def image_saved(self, id, fileName):
		print("Tabs Undocked")
		#index = self._tab_widget.count()
		#image_view = ImageView(self._current_preview, fileName)
		#self._tab_widget.addTab(image_view, f"Capture #{index}")
		#self._tab_widget.setCurrentIndex(index)

	@Slot(int, QImageCapture.Error, str)
	def _capture_error(self, id, error, error_string):
		print(error_string, file=sys.stderr)
		self.show_status_message(error_string)

	@Slot(QCamera.Error, str)
	def _camera_error(self, error, error_string):
		print(error_string, file=sys.stderr)
		self.show_status_message(error_string)


# create a Window class
class Window(QMainWindow):
	# constructor
	def __init__(self):
		super().__init__()

		self.windows = []

		# setting up the style of border
		#self.setStyleSheet("border : 3px dashed blue;")
		#self.setStyleSheet("border : 1px solid black;")

		# Arduino Serial
		self.arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=.1) #Port name in Linux Format


		# setting title
		self.setWindowTitle("Rubiks Cube Solver - Robotics UEF")

		# setting geometry
		self.setGeometry(100, 100,
						1200, 700)	

		# calling method
		self.UiComponents()

		# showing all the widgets
		self.show()

	# method for components
	def UiComponents(self):

		
		#self._tab_widget.addTab(self._camera_viewfinder, "Viewfinder")

		# Cubestring
		self.cubestring = ""

		# Dictionary of Faces
		self.faces = {key: None for key in ["U","R","F","D","L","B"]}

		# Create Color Selector
		self.selColor = "#000000" # default color is black

		# Faces Configuration
		for k in self.faces.keys():
			tmp_list = []
			for _ in range(3):
				temp = []
				for _ in range(3):
					temp.append((QPushButton(self)))
				# adding 3 push button in single row
				tmp_list.append(temp)
			self.faces[k] = tmp_list

		# Selector Options in a 2X3 Array
		self.selectors = []
		for _ in range(6):
			self.selectors.append((QPushButton(self)))

		# x and y co-ordinate
		x = 50
		y = 50

		# Offset for Plotting on GUI
		self.offset_gui = {'U': [(x*3),0], 'R': [2*(x*3),(y*3)],'F': [(x*3),(y*3)],'D': [(x*3),2*(y*3)],'L': [0,(y*3)],'B': [3*(x*3),(y*3)]}
		
		# Default Colors
		self.bgColors = {'U': "QPushButton {background-color: yellow; color: black;border :1px solid black;}", 'R': "QPushButton {background-color: green; color: black;border :1px solid black;}",'F': "QPushButton {background-color: red; color: black;border :1px solid black;}", 'D': "QPushButton {background-color: white; color: black;border :1px solid black;}",'L': "QPushButton {background-color: blue; color: black;border :1px solid black;}",'B': "QPushButton {background-color: orange; color: black;border :1px solid black;}"}

		# Reset Color
		self.rst_color = "QPushButton {background-color: gray; border :1px solid black; font-size: 12px;}"
		# ===============================
		# Traversing through Faces
		# ===============================
		for cnt, k in enumerate(self.faces.keys()):
			for i in range(3):
				for j in range(3):

					# setting geometry to the button
					self.faces[k][i][j].setGeometry(x*i + 20 + self.offset_gui[k][0],
													y*j + 20 + self.offset_gui[k][1],
													x, y)

					# setting font to the button
					#self.faces[k][i][j].setFont(QFont(QFont('Times', 17)))
					#self.faces[k][i][j].setFont(17)

					# adding action
					self.faces[k][i][j].clicked.connect(self.face_click)

					# Setting Color and Blocking Middle Button
					if (j==1) and (i==1):
						# making button disabled
						self.faces[k][i][j].setEnabled(False)
						# Changing Color
						self.faces[k][i][j].setStyleSheet(self.bgColors[k])
						self.faces[k][i][j].setText(k)
					else:
						self.faces[k][i][j].setStyleSheet(self.rst_color)


		# ===============================
		# Traversing through Color Selectors
		# ===============================
		keys_faces = list(self.faces.keys())
		# Button 1
		self.selectors[0].setGeometry(x*7 + 20,y*7 + 20, x, y)
		# Button 2
		self.selectors[1].setGeometry(x*8 + 20,y*7 + 20, x, y)
		# Button 3
		self.selectors[2].setGeometry(x*9 + 20,y*7 + 20, x, y)
		# Button 4
		self.selectors[3].setGeometry(x*7 + 20,y*8 + 20, x, y)
		# Button 5
		self.selectors[4].setGeometry(x*8 + 20,y*8 + 20, x, y)
		# Button 6
		self.selectors[5].setGeometry(x*9 + 20,y*8 + 20, x, y)
		
		for idx, b in enumerate(self.selectors):
			b.setStyleSheet(self.bgColors[keys_faces[idx]])
			b.clicked.connect(self.selector_click)

		# ===============================
		# Label for Comments
		# ===============================

		# creating label to tel the score
		self.label = QLabel(self)

		# setting geometry to the label
		self.label.setGeometry(380, 50, 520, 60)

		# setting style sheet to the label
		self.label.setStyleSheet("QLabel"
								"{"
								"border : 3px solid black;"
								"background : white;"
								"color: black;"
								"font-size: 12px;"
								"}")

		# setting font to the label
		#self.label.setFont(QFont('Times', 13))

		# Setting Word Wrap
		self.label.setWordWrap(True)

		# setting label alignment
		self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

		

		

		# ===============================
		# Solve Button
		# ===============================

		# creating push button to restart the score
		self.solve_button = QPushButton("Solve Cube", self)
		self.solve_button.setStyleSheet("QPushButton {black;border :1px solid black;}")
		# setting geometry
		self.solve_button.setGeometry(750, 380, 200, 50)
		# adding action action to the reset push button
		self.solve_button.clicked.connect(self.solve_btn_click)
#		solve_button.setStyleSheet("QPushButton {background-color: yellow; color: black;border :1px solid black;}")
		

		# ===============================
		# Clear Button
		# ===============================

		# creating push button to restart the score
		clr_button = QPushButton("Clear All", self)
		# setting geometry
		clr_button.setGeometry(750, 480, 200, 50)
		# adding action action to the reset push button
		clr_button.clicked.connect(self.clr_btn_click)

		# ===============================
		# Full Button
		# ===============================

		# creating push button to restart the score
		full_button = QPushButton("Fill Faces", self)
		# setting geometry
		full_button.setGeometry(750, 580, 200, 50)
		# adding action action to the reset push button
		full_button.clicked.connect(self.full_btn_click)

		# ===============================
		# Camera Button
		# ===============================

		# creating push button to restart the score
		camera_button = QPushButton("Open Camera", self)
		# setting geometry
		camera_button.setGeometry(20, 600, 200, 50)
		# adding action action to the reset push button
		camera_button.clicked.connect(self.connect_camera)

	def connect_camera(self):
		self.secondWindow = MainCameraWindow()
		#available_geometry = self.secondWindow.screen().availableGeometry()
		#self.secondWindow.resize(available_geometry.width() / 3, available_geometry.height() / 2)
		#self.windows.append(secondWindow)
		#self.hide()
		self.secondWindow.show()
		#self.secondWindow.show()

	def get_cubestring(self, faces):
		print("Getting Cube String")
		cubestring_tmp = ''

		# Iterate through all faces
		for cnt, k in enumerate(self.faces.keys()):
			for i in range(3):
				for j in range(3):
					btn_color = self.faces[k][j][i].palette().button().color().name() # TODO: i and j were inverted
					print(btn_color)
					btn_color_digit = self.get_color(btn_color)
					cubestring_tmp += btn_color_digit

		return cubestring_tmp

	def selector_click(self):
		current_button = self.sender()
		self.selColor = current_button.palette().button().color().name()
		#self.label.setText(self.selColor.name())


	def face_click(self):
		# Button Clicked
		button_tmp = self.sender()
		print(self.selColor)
		# Set Current State of color and update accordingly
		if self.selColor == "#ffff00": # yellow or U
			button_tmp.setStyleSheet(self.bgColors['U'])

		elif self.selColor == "#008000": # green or R
			button_tmp.setStyleSheet(self.bgColors['R'])
		
		elif self.selColor == "#ff0000": # red or F
			button_tmp.setStyleSheet(self.bgColors['F'])

		elif self.selColor == "#ffffff": # white or D
			button_tmp.setStyleSheet(self.bgColors['D'])

		elif self.selColor == "#0000ff": # blue or L
			button_tmp.setStyleSheet(self.bgColors['L'])

		elif self.selColor == "#ffa500": # orange or B
			button_tmp.setStyleSheet(self.bgColors['B'])
	
	def get_color(self, color_hex):
		print(color_hex)
		if color_hex == "#ffff00": # yellow or U
			return 'U'

		elif color_hex == "#008000": # green or R
			return 'R'
		
		elif color_hex == "#ff0000": # red or F
			return 'F'

		elif color_hex == "#ffffff": # white or D
			return 'D'

		elif color_hex == "#0000ff": # blue or L
			return 'L'

		elif color_hex == "#ffa500": # orange or B
			return 'B'
		else:
			return 'X' # Gray face, error

	def full_btn_click(self):
		for cnt, k in enumerate(self.faces.keys()):
			for i in range(3):
				for j in range(3):
					self.faces[k][i][j].setStyleSheet(self.bgColors[k])

	def solve_btn_click(self):
		# Get Current State of the faces
		self.cubestring  = self.get_cubestring(self.faces)


		#self.cubestring = 'UUUUUUUUUFFFRRRRRRLLLFFFFFFDDDDDDDDDBBBLLLLLLRRRBBBBBB' # Solution U1 (1f)

		#self.cubestring = 'UUUUUUUUUFFFRRRRRRLLLFFFFFFDDDDDDDDDBBBLLLLLLRRRBBBBBX' # Wrong on purpose to see that nothing happens

		# solves the cube described by the definition string with a desired maximum length of 19 moves and a timeout of 2 seconds
		rubiks_solution = sv.solve(self.cubestring,10,2)

		# Writes Result on label
		self.label.setText(rubiks_solution)

		if 'Error' not in rubiks_solution:
			# Separate by Spaces
			rubiks_solution = rubiks_solution.split(sep=' ')

			# Keep the movements of the result string
			rubiks_solution = ''.join(rubiks_solution[:-1])

			# Append Start < and End > elements to result
			to_send_str = '<' + rubiks_solution + '>'

			# Send serial to Arduino for movements
			print(to_send_str)
			self.arduino.write(to_send_str.encode())
		

	def clr_btn_click(self):
		for cnt, k in enumerate(self.faces.keys()):
			for i in range(3):
				for j in range(3):

					# Setting Color and Blocking Middle Button
					if (j==1) and (i==1):
						pass
					else:
						# Changing Color To Default
						self.faces[k][i][j].setStyleSheet(self.rst_color)



# Driver code
if __name__ == "__main__" :
	# create pyqt5 app
	App = QApplication(sys.argv)

	# create the instance of our Window
	window = Window()

	# start the app
	sys.exit(App.exec())
