
import functools
import random
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *


fN = None


class ScribbleArea(QWidget):
	
	def __init__(self, parent=None):
		
		super(ScribbleArea, self).__init__(parent)
		
		self.setAttribute(Qt.WA_StaticContents)
		
		self.modified = False
		self.scribbling = False
		
		self.myPenWidth = 5
		self.myPenColor = Qt.black
		
		imageSize = QSize(500, 500)
		self.image = QImage(imageSize, QImage.Format_RGB32)
		
		self.lastPoint = QPoint()
		

	def openImage(self, fileName):
		
		loadedImage = QImage()
		if not loadedImage.load(fileName):
			return False

		w = loadedImage.width()
		h = loadedImage.height()    
		self.mainWindow.resize(w, h)

		self.image = loadedImage
		self.modified = False
		self.update()
		return True
		
	def saveImage(self, fileName, fileFormat):
		
		fN = fileName
		visibleImage = self.image
		self.resizeImage(visibleImage, self.size())

		if visibleImage.save(fileName, fileFormat):
			self.modified = False
			return True
		else:
			return False
			
			
	def setPenColor(self, newColor):
		self.myPenColor = newColor
		
	def setPenWidth(self, newWidth):
		self.myPenWidth = newWidth
		
	def clearImage(self):
		self.image.fill(qRgb(255,255,255))
		self.modified = True
		self.update()
		
	def isModified(self):
		return self.modified
		
	def penColor(self):
		return self.myPenColor
		
	def penWidth(self):
		return self.myPenWidth
		
		
	def paintEvent(self, event):
		
		painter = QPainter(self)
		painter.drawImage(event.rect(), self.image)
	
	
	def drawLineTo(self, endPoint):
		
		painter = QPainter(self.image)
		painter.setPen(QPen(self.myPenColor, self.myPenWidth, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
		painter.drawLine(self.lastPoint, endPoint)
		self.modified = True
		
		rad = self.myPenWidth / 2 + 2
		self.update(QRect(self.lastPoint, endPoint).normalized().adjusted(-rad, -rad, +rad, +rad))
		
		self.update()
		self.lastPoint = QPoint(endPoint)
			
		
	def mousePressEvent(self, event):
		
		if event.button() == Qt.LeftButton:
			self.lastPoint = event.pos()
			self.scribbling = True
			
	
	def mouseReleaseEvent(self, event):
		
		if event.button() == Qt.LeftButton and self.scribbling:
			self.drawLineTo(event.pos())
			self.scribbling = False
		
			
	def mouseMoveEvent(self, event):
		
		if (event.buttons() & Qt.LeftButton) and self.scribbling:
			self.drawLineTo(event.pos())
			
	
	def resizeEvent(self, event):
		
		self.resizeImage(self.image, event.size())
		super(ScribbleArea, self).resizeEvent(event)
	
		
	def resizeImage(self, image, newSize):
		
		if image.size() == newSize:
			return
			
		newImage = QImage(newSize, QImage.Format_RGB32)
		newImage.fill(qRgb(255,255,255))
		painter = QPainter(newImage)
		painter.drawImage(QPoint(0,0), image)
		
		self.image = newImage
		

class MainForm(QDialog):
	
	def __init__(self, parent=None):
		
		super(MainForm, self).__init__(parent)
		self.fileName = None
		
		self.scribbleArea = ScribbleArea(self)
		self.scribbleArea.clearImage()
		self.scribbleArea.mainWindow = self
		self.copyrightBanner = QLabel("Scrib-to-String, Copyright "+u'\u00A9'+" 2015 <br>Rocky <a href=\"mailto:riverdale1109@gmail.com\">riverdale1109@gmail.com </a>")
		self.copyrightBanner.setAlignment(Qt.AlignCenter)
		
		self.bottomLayout = QHBoxLayout()
		
		self.openButton = QPushButton("&Open")
		self.saveButton = QPushButton("&Save")
		self.findButton = QPushButton("&Find")
		self.clearButton = QPushButton("&Clear")
		self.quitButton = QPushButton("&Quit")
		
		self.openButton.clicked.connect(self.open_)
		self.saveButton.clicked.connect(self.save_)
		self.findButton.clicked.connect(self.find_)
		self.clearButton.clicked.connect(self.clear_)
		self.quitButton.clicked.connect(self.quit_)
		
		self.bottomLayout.addWidget(self.openButton)
		self.bottomLayout.addWidget(self.saveButton)
		self.bottomLayout.addWidget(self.findButton)
		self.bottomLayout.addWidget(self.clearButton)
		self.bottomLayout.addWidget(self.quitButton)
						
		lay = QVBoxLayout()
		lay.addWidget(self.scribbleArea)
		lay.addWidget(self.HLine())
		lay.addLayout(self.bottomLayout)
		lay.addWidget(self.HLine())
		lay.addWidget(self.copyrightBanner)
		
		self.setLayout(lay)
		self.setWindowTitle("Scrib-to-String")
		self.resize(500, 500)
	
	
	def HLine(self):
		t = QFrame()
		t.setFrameShape(QFrame.HLine)
		t.setFrameShadow(QFrame.Sunken)
		return t
		
	
	def open_(self):
		if self.maybeSave():
			self.fileName = QFileDialog.getOpenFileName(self, "Open File", QDir.currentPath())
			if self.fileName:
				self.scribbleArea.openImage(self.fileName)


	def find_(self):
		
		print str(self.fileName)
		import os
		if self.fileName:
			os.system("gocr -i "+str(self.fileName)+" -o out.txt")
			f = open('out.txt','r')
			output = ""
			for i in f.readlines():
				output += i
			QMessageBox.information(self, "Scrib-to-String",
				"Output of the Scribbled image is:<br><font color=red><h3>"+str(output)+"</h3></font>",
				QMessageBox.Ok )
		else:
			QMessageBox.warning(self, "Scrib-to-String",
				'First save the file!',
				QMessageBox.Ok )
			
		
	def clear_(self):
		self.fileName = None
		self.fileFormat = None
		self.scribbleArea.clearImage()	
	
	
	def maybeSave(self):
		if self.scribbleArea.isModified():
			ret = QMessageBox.warning(self, "Scrib-to-String",
				"The image has been modified.\n"
				"Do you want to save your changes?",
				QMessageBox.Save | QMessageBox.Discard |
				QMessageBox.Cancel)
			if ret == QMessageBox.Save:
				return self.saveFile('png')
			elif ret == QMessageBox.Cancel:
				return False

		return True


	def save_(self, fileFormat):
		fileFormat="jpg"
		initialPath = QDir.currentPath() + str('/untitled.') + fileFormat
		#initialPath = "/home/royrocky/Desktop" + str('/untitled.') + "jpg"
		self.fileFormat = fileFormat
		
		self.fileName = QFileDialog.getSaveFileName(self, "Save As", initialPath,
			"%s Files (*.%s);;All Files (*)" % (self.fileFormat.upper(), self.fileFormat))
		if self.fileName:
			print str(self.fileName)+str(self.fileFormat)
			return self.scribbleArea.saveImage(self.fileName, self.fileFormat)

		return False
	
		
	def quit_(self, event):
		if self.maybeSave():
			event.accept()
		else:
			event.ignore()
		
		
def main():
	
	import sys
	
	app = QApplication(sys.argv)
	form = MainForm()
	form.show()
	sys.exit(app.exec_())
	

if __name__ == "__main__":
	main()
