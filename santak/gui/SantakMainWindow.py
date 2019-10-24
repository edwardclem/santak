# TODO: update documentation

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QProgressDialog,
    QRadioButton,
)
from santak.vision import reduce_contours
import cv2
import numpy as np
import pickle
from .SantakDrawArea import SantakDrawArea
from .SantakResults import SantakResults
from tqdm import tqdm


class SantakMainWindow(QMainWindow):
    def __init__(self, protos, num_max=5):
        super(SantakMainWindow, self).__init__()

        self.saveAsActs = []
        self.num_max = num_max

        self.drawArea = SantakDrawArea()
        self.setCentralWidget(self.drawArea)
        self.setWindowTitle("santak")
        # need to implement resize event handler
        self.resize(300, 300)
        # TODO: avoid call to resize at all
        self.setFixedSize(300, 300)

        # TODO: separate button area from draw area
        clear_button = QPushButton("Clear", self)
        clear_button.move(0, 270)
        clear_button.clicked.connect(self.clear_drawing)

        search_button = QPushButton("Search", self)
        search_button.move(100, 270)
        search_button.clicked.connect(self.lookup)

        # create drawing symbol switching
        # TODO: replace this with enum
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

        # loading prototype data from pickle
        with open(protos, "rb") as f:
            proto_data = pickle.load(f)
            self.id2img = proto_data["id2img"]
            self.id2allcontour = proto_data["id2contour"]
            # subsampling contours once, could in theory do this differently every time?
            # add multiple samples of the same character?
            # merging together contour here as well
            self.id2contour = {
                key: np.concatenate(reduce_contours(contour))
                for key, contour in self.id2allcontour.items()
            }

            print(
                "loaded {} prototype contours from {}".format(
                    len(self.id2img.keys()), protos
                )
            )

        self.sc_extractor = cv2.createShapeContextDistanceExtractor()

    def clear_drawing(self):
        self.drawArea.clearImage()

    def switch_symbol(self):
        """
        Switches the symbol currently being drawn.
        """
        self.current_sym = self.sender().objectName()

    def getimg(self):
        """
        Image extraction from
        https://stackoverflow.com/questions/11360009/how-can-access-to-pixel-data-with-pyqt-qimage-scanline/11399959#11399959
        """
        # extract image from drawArea
        # create pointer to bits
        ptr = self.drawArea.image.bits()
        ptr.setsize(self.drawArea.image.byteCount())
        # get as array
        arr = np.asarray(ptr).reshape(
            self.drawArea.image.height(), self.drawArea.image.width(), 4
        )

        return arr

    def lookup(self):
        """
        Shape context character matching.
        TODO: move this?
        """
        # TODO: analyze what this is doing
        # TODO: abstraction
        img = self.getimg()[0:300, 0:300]  # crop to 300x300
        # perform Canny edge detection
        edges = cv2.Canny(img, 300, 300)
        # get contour of image
        _, cnt_target, _ = cv2.findContours(
            edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        # concatenate contours
        subsampled = reduce_contours(cnt_target)

        if len(cnt_target) > 0:
            # open pop-up window
            progress = QProgressDialog(
                "Searching...", "Cancel", 0, len(self.id2contour.keys()), self
            )
            progress.setWindowModality(Qt.WindowModal)
            progress.setAutoClose(True)
            QApplication.processEvents()
            all_contours_target = np.concatenate(subsampled)
            distances = {}

            # self.progress.setVisible(True)
            # TODO: abstract this part out along with the progress bar(s)
            for i, dat in enumerate(tqdm(self.id2contour.items())):
                char_id, contour = dat

                try:
                    dist = self.sc_extractor.computeDistance(
                        all_contours_target, contour
                    )
                except cv2.error as e:
                    print("WARNING: character ID {} suffered error".format(char_id))
                    dist = 1

                distances[char_id] = dist

                if progress.wasCanceled():
                    print("CANCELED")
                    break

                progress.setValue(i + 1)
                QApplication.processEvents()

            if not progress.wasCanceled():
                ranked_shapes = sorted(distances, key=distances.get)
                closest = ranked_shapes[: self.num_max]
                # create results dialog
                results = SantakResults(
                    [self.id2img[num] for num in closest], closest, self
                )
                results.setWindowModality(Qt.WindowModal)  # block until dismissed
                results.exec()

            else:
                print("No target contours found.")
