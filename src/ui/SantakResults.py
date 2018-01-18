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

class SantakResults(QDialog):
    '''
    Modified QDialog containing results.
    TODO: Redo this whole results display once I figure out data format.
    '''

    def __init__(self, img_list, char_list, parent=None):
        super(SantakResults, self).__init__(parent)

        self.resize(260, len(img_list)*100 + 50)
        self.setFixedSize(260, len(img_list)*100+ 50)

        #add button
        self.button = QPushButton("OK", self)
        self.button.clicked.connect(self.accept)
        self.button.move(0, len(img_list)*100 + 20)

        #table for results
        self.table = QTableWidget(self)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setRowCount(len(img_list))
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Character", "Name"])
        self.table.verticalHeader().setDefaultSectionSize(100)

        for i, img in enumerate(img_list):
            # TODO: render the unicode character instead! or something else.
            #TODO: add sign values
            # this is all pretty much a gross placeholder
            height, width, channel = img.shape
            bytesPerLine = 3 * width
            qimg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888)
            # item.setIconSize(100, 100)
            self.table.setItem(i, 0, QTableWidgetItem(QIcon(QPixmap(qimg)), ""))
            self.table.setItem(i, 1, QTableWidgetItem(unicodedata.name(chr(int(char_list[i])))))

        self.table.setIconSize(QSize(100, 100))
        self.table.resize(250, len(img_list)*100 + 25)
