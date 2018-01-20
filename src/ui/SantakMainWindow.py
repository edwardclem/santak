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
from ui.SantakDrawArea import SantakDrawArea
from ui.SantakResults import SantakResults
import multiprocessing as mp
from ui.sc_inference.compute_dist import *

NUM_MAX = 5 #number of highest scoring characters

#TODO: move this stuff somewhere else too
def subsample_contours(contours, pct=0.2, min_threshold=10):
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

def reduce_contours(contours, step=10):
    '''
    keeps every step points, removes the rest. Alternative to probabilistic subsampling.
    TODO: do this on data processing instead of after loading.
    TODO: add min threshold?
    '''
    reduced_contours = []
    for contour in contours:
        total_points = contour.shape[0]
        kept_idx = np.arange(0, total_points, step)
        reduced_contours.append(contour[kept_idx, :, :])

    return reduced_contours

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
        search_button.clicked.connect(self.lookup_parallel)

        #create drawing symbol switching
        #TODO: replace this with enum
        self.current_sym = "BW"

        big_wedge_button = QRadioButton("big wedge", self)
        big_wedge_button.move(200, 220)
        big_wedge_button.setChecked(True)
        big_wedge_button.setObjectName("BW")
        big_wedge_button.clicked.connect(self.switch_symbol)


        small_wedge_button = QRadioButton("small wedge", self)
        small_wedge_button.setObjectName("SW")
        small_wedge_button.move(200, 240)
        small_wedge_button.clicked.connect(self.switch_symbol)


        winkelbutton = QRadioButton("winkelhaken", self)
        winkelbutton.setObjectName("WK")
        winkelbutton.clicked.connect(self.switch_symbol)
        winkelbutton.move(200, 260)

        #loading prototype data from pickle
        with open(protos, 'rb') as f:
            proto_data = pickle.load(f)
            self.id2img = proto_data['id2img']
            self.id2allcontour = proto_data['id2contour']
            #add multiple samples of the same character?
            #merging together contour here as well
            #not subsampling or reducing, already done by data processing
            self.id2contour = {key:np.concatenate(contour) for key, contour in self.id2allcontour.items()}

            print("loaded {} prototype contours from {}".format(len(self.id2img.keys()), protos))


        self.sc_extractor = cv2.createShapeContextDistanceExtractor()


    def clear_drawing(self):
        self.drawArea.clearImage()


    def switch_symbol(self):
        '''
        Switches the symbol currently being drawn.
        '''
        self.current_sym = self.sender().objectName()

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

    def get_contour(self):
        '''
        Gets the current contour on the screen. concatenates all contours together.
        '''

        img = self.getimg()[0:300, 0:300] #crop to 300x300
        #perform Canny edge detection
        edges = cv2.Canny(img, 300, 300)
        #get contour of image
        _, cnt_target, _  = cv2.findContours(edges, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        #concatenate contours
        subsampled = reduce_contours(cnt_target)

        return np.concatenate(subsampled)

    def lookup_parallel(self):
        '''
        shape context character matching parallelized.
        TODO: refactor this.
        '''

        target = self.get_contour()

        if len(target) > 0:
            progress = QProgressDialog("Searching...", "Cancel", 0, len(self.id2contour.keys()), self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setAutoClose(True)
            QApplication.processEvents()

            #create batches.

            batches = create_batches(self.id2contour)

            #create output queue
            outq = mp.Queue()

            #create processes
            procs = [mp.Process(target=process_batch, args=(target, batch, outq)) for batch in batches]

            for proc in procs:
                proc.start()
            print("started processes")
            results = {}

            #wait for all data to come in from queue, update progress bar
            for i, _ in enumerate(self.id2contour.items()):
                char_id, dist = outq.get(True) #block until something apppears
                results[char_id] = dist
                if progress.wasCanceled():
                    break;

                progress.setValue(i + 1)
                QApplication.processEvents()

            if progress.wasCanceled():
                #kill all threads
                print("terminating processes")
                for proc in procs:
                    proc.terminate()
            else:
                print("waiting for join to complete")
                for proc in procs:
                    proc.join()
                #display results
                ranked_shapes = sorted(results, key=results.get)
                closest = ranked_shapes[:NUM_MAX]
                #create results dialog
                results = SantakResults([self.id2img[num] for num in closest], closest, self)
                results.setWindowModality(Qt.WindowModal) #block until dismissed
                results.exec()

    def lookup(self):
        '''
        Shape context character matching.
        TODO: move this to inference package
        '''
        img = self.getimg()[0:300, 0:300] #crop to 300x300
        #perform Canny edge detection
        edges = cv2.Canny(img, 300, 300)
        #get contour of image
        _, cnt_target, _  = cv2.findContours(edges, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        #concatenate contours
        subsampled = reduce_contours(cnt_target)

        if len(cnt_target) > 0:
            #open pop-up window
            progress = QProgressDialog("Searching...", "Cancel", 0, len(self.id2contour.keys()), self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setAutoClose(True)
            QApplication.processEvents()
            all_contours_target = np.concatenate(subsampled)
            distances = {}

            # self.progress.setVisible(True)
            for i, dat in enumerate(self.id2contour.items()):
                char_id, contour = dat
                # print("comparing to {}, number of contours: {}".format(char_id, len(contour)))
                distances[char_id] = self.sc_extractor.computeDistance(all_contours_target, contour)

                if progress.wasCanceled():
                    break;

                progress.setValue(i + 1)
                QApplication.processEvents()

            if not progress.wasCanceled():
                ranked_shapes = sorted(distances, key=distances.get)
                closest = ranked_shapes[:NUM_MAX]
                #create results dialog
                results = SantakResults([self.id2img[num] for num in closest], closest, self)
                results.setWindowModality(Qt.WindowModal) #block until dismissed
                results.exec()

            else:
                print("empty")
