## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$

from PyQt5.QtCore import QDir, QPoint, QRect, QSize, Qt
from PyQt5.QtGui import QImage, QImageWriter, QPainter, QPen, qRgb, qRgba, QPolygon, QColor, QBrush
from PyQt5.QtWidgets import (QAction, QApplication, QColorDialog, QFileDialog,
        QInputDialog, QMainWindow, QMenu, QMessageBox, QWidget, QPushButton, QProgressBar, QLabel)
import sys
import glob
import os
import cv2
import math
import numpy as np
from tqdm import tqdm
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import pickle
import time

NUM_MAX = 5 #number of highest scoring characters

def subsample_contours(contours, pct=0.3, min_threshold=10):
    '''
    Samples subset of contour points.
    '''
    subsampled_contours  = []
    for contour in contours:
        total_points = contour.shape[0]
        num_to_sample = int(pct*total_points) if total_points > min_threshold else total_points
        sample_idx = np.sort(np.random.choice(total_points, num_to_sample, replace=False))
        subsampled_contours.append(contour[sample_idx,:,:])

    return subsampled_contours

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

    def drawWedgeTo(self, endLoc, temp=False):
        '''
        Draws a wedge at the provided location.
        '''

        # print(self.image.isNull())

        painter = QPainter(self.image) if not temp else QPainter(self.tempImage)

        painter.setPen(QPen(QColor(0,0,0, 255), 10))
        painter.setBrush(QBrush(QColor(255,255,255,255)))

        point1 = QPoint(-30, - 30)
        point2 = QPoint(30,  - 30)
        point3 = QPoint(0, 15)

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
            self.drawWedgeTo(event.pos(), temp=True)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.clearTemp()
            self.drawWedgeTo(event.pos())
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

class SantakMainWindow(QMainWindow):
    def __init__(self, protos):
        super(SantakMainWindow, self).__init__()

        self.saveAsActs = []

        self.drawArea = SantakDrawArea()
        self.setCentralWidget(self.drawArea)
        self.setWindowTitle("santak")
        #need to implement resize event handler
        self.resize(300, 300)
        #TODO: avoid call to resize at all
        self.setFixedSize(300, 300)

        #TODO: separate button area from draw area
        clear_button = QPushButton("Clear", self)
        clear_button.move(0, 270)
        clear_button.clicked.connect(self.clear_drawing)

        search_button = QPushButton("Search", self)
        search_button.move(100, 270)
        search_button.clicked.connect(self.lookup)

        #loading prototype data from pickle
        with open(protos, 'rb') as f:
            proto_data = pickle.load(f)
            self.id2img = proto_data['id2img']
            self.id2allcontour = proto_data['id2contour']
            #subsampling contours once, could in theory do this differently every time?
            #add multiple samples of the same character?
            #merging together contour here as well
            self.id2contour = {key:np.concatenate(subsample_contours(contour)) for key, contour in self.id2allcontour.items()}


            print("loaded {} prototype contours from {}".format(len(self.id2img.keys()), protos))


        self.sc_extractor = cv2.createShapeContextDistanceExtractor()

        #create progress bar + label
        self.progress = QProgressBar(self)
        self.progress.move(75, 250)
        self.progress.setRange(0, len(self.id2contour.items()))

        self.searchLabel = QLabel("Matching: ", self)
        self.searchLabel.move(0, 250)
        # self.progress.setValue(0)
        # self.progress.setVisible(False)
        # self.searchLabel.setVisible(False)

    def clear_drawing(self):
        self.drawArea.clearImage()

    def getimg(self):
        '''
        Image extraction from
        https://stackoverflow.com/questions/11360009/how-can-access-to-pixel-data-with-pyqt-qimage-scanline/11399959#11399959
        '''
        #extract image from drawArea
        #create pointer to bits
        ptr = self.drawArea.image.bits()
        ptr.setsize(self.drawArea.image.byteCount())
        #get as array
        arr = np.asarray(ptr).reshape(self.drawArea.image.height(), self.drawArea.image.width(), 4)

        return arr


    def lookup(self):
        '''
        Shape context character matching.
        '''
        img = self.getimg()[0:300, 0:300] #crop to 300x300
        #perform Canny edge detection
        edges = cv2.Canny(img, 300, 300)
        #get contour of image
        _, cnt_target, _  = cv2.findContours(edges, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        #concatenate contours
        subsampled = subsample_contours(cnt_target)


        if len(cnt_target) > 0:
            # self.progress.setVisible(True)
            # self.searchLabel.setVisible(True)
            QApplication.processEvents()
            all_contours_target = np.concatenate(subsampled)

            distances = {}

            # self.progress.setVisible(True)
            for i, dat in enumerate(self.id2contour.items()):
                char_id, contour = dat
                dist = self.sc_extractor.computeDistance(all_contours_target, contour)
                distances[char_id] = dist
                self.progress.setValue(i + 1)
                QApplication.processEvents()


            # self.progress.setVisible(False)
            # self.searchLabel.setVisible(False)
            self.progress.reset()

            print(distances)
            # sorting by distance, displaying top 3
            ranked_shapes = sorted(distances, key=distances.get)

            print(ranked_shapes)

            closest = ranked_shapes[:NUM_MAX]

            for i, char_num in enumerate(closest):
                cv2.imshow("{} - {}".format(i + 1, char_num), self.id2img[char_num])

            cv2.waitKey(0)
            cv2.destroyAllWindows()





if __name__ == '__main__':

    app = QApplication(sys.argv)
    proto = "data/prototypes/proto_20"
    window = SantakMainWindow(proto)
    window.show()
    sys.exit(app.exec_())
