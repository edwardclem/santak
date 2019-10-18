#TODO: update documentation and fix import block

from PyQt5.QtCore import QDir, QPoint, QRect, QSize, Qt
from PyQt5.QtGui import QImage, QImageWriter, QPainter, QPen, qRgb, qRgba, QPolygon, QColor, QBrush,QPixmap, QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QMainWindow, QDialog, QWidget, QPushButton, QProgressDialog, QLabel, QTableWidget,QTableWidgetItem, QAbstractItemView, QRadioButton)
import sys
import unicodedata
import glob
import os
import cv2
import math
import numpy as np
import pickle

class SantakDrawArea(QWidget):
    def __init__(self, parent=None):
        super(SantakDrawArea, self).__init__(parent)

        self.setAttribute(Qt.WA_StaticContents)
        self.drawing = False
        self.myPenWidth = 1
        self.charColor = Qt.black
        self.image = QImage()
        self.tempImage = QImage() #for storing wedge mid-draw
        self.wedgeStart = QPoint()


    def clearImage(self):
        self.image.fill(qRgba(255, 255, 255, 255))
        self.update()

    def clearTemp(self):
        '''
        Clears the (transparent) temporary image.
        '''
        self.tempImage.fill(qRgba(0, 0, 0, 0))
        self.update()

    def drawWinkelhaken(self, loc, temp=False):
        '''
        draws a winkelhaken at the provided location.
        '''
        painter = QPainter(self.image) if not temp else QPainter(self.tempImage)
        #TODO this thingy

    def drawWedgeTo(self, endLoc, temp=False, width=10, offset=30):
        '''
        Draws a wedge at the provided location.
        TODO: make size params better.
        '''

        # print(self.image.isNull())

        painter = QPainter(self.image) if not temp else QPainter(self.tempImage)

        painter.setPen(QPen(QColor(0,0,0, 255), width))
        painter.setBrush(QBrush(QColor(255,255,255,255)))

        point1 = QPoint(-offset, - offset)
        point2 = QPoint(offset,  - offset)
        point3 = QPoint(0, offset/2)

        poly = QPolygon([point1, point2, point3])
        #compute vector from points
        vec = endLoc - self.wedgeStart
        length = math.hypot(vec.x(), vec.y())
        angle = math.degrees(math.atan2(vec.x(), vec.y()))
        #transform painter
        painter.translate(self.wedgeStart)
        painter.rotate(-angle)
        painter.drawPolygon(poly)

        if length > 10:
            painter.drawLine(point3, QPoint(0, length))

        #global update for now?

        self.update()

    def paintEvent(self, event):
        #dunno exactly what this does but ok
        painter = QPainter(self)
        dirtyRect = event.rect()
        painter.drawImage(dirtyRect, self.image, dirtyRect)
        painter.drawImage(dirtyRect, self.tempImage, dirtyRect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.wedgeStart = event.pos()
            self.drawing = True

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.drawing:
            self.clearTemp()
            if self.parent().current_sym == "BW":
                self.drawWedgeTo(event.pos(), temp=True)
            elif self.parent().current_sym == "SW":
                self.drawWedgeTo(event.pos(), temp=True, width=5, offset=15)
        #TODO: if not drawing, add a grey temporary indicator of what kind/size
        #of wedge is being drawn

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.clearTemp()
            if self.parent().current_sym == "BW":
                self.drawWedgeTo(event.pos())
            elif self.parent().current_sym == "SW":
                self.drawWedgeTo(event.pos(), width=5, offset=15)
            self.drawing = False

    def resizeImage(self, image, newSize):
        if image.size() == newSize:
            return

        newImage = QImage(newSize, QImage.Format_ARGB32)
        newImage.fill(qRgba(255, 255, 255, 255))
        painter = QPainter(newImage)
        painter.drawImage(QPoint(0, 0), image)
        self.image = newImage
        self.tempImage = QImage(newSize, QImage.Format_ARGB32)
        self.tempImage.fill(qRgba(255, 255, 255, 0))

    def resizeEvent(self, event):
        if self.width() > self.image.width() or self.height() > self.image.height():
            #TODO: prevent size difference here?
            newWidth = max(self.width() + 128, self.image.width())
            newHeight = max(self.height() + 128, self.image.height())
            self.resizeImage(self.image, QSize(newWidth, newHeight))
            self.update()

        super(SantakDrawArea, self).resizeEvent(event)
