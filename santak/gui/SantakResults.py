# TODO: update documentation and fix import block

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtWidgets import (
    QDialog,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
)
import unicodedata


class SantakResults(QDialog):
    """
    Modified QDialog containing results.
    TODO: Redo this whole results display once I figure out data format.
    """

    def __init__(self, img_list, char_list, parent=None):
        super(SantakResults, self).__init__(parent)

        self.resize(260, len(img_list) * 100 + 50)
        self.setFixedSize(260, len(img_list) * 100 + 50)

        # add button
        self.button = QPushButton("OK", self)
        self.button.clicked.connect(self.accept)
        self.button.move(0, len(img_list) * 100 + 20)

        # table for results
        self.table = QTableWidget(self)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setRowCount(len(img_list))
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Character", "Name"])
        self.table.verticalHeader().setDefaultSectionSize(100)

        for i, img in enumerate(img_list):
            # TODO: render the unicode character instead! or something else.
            # TODO: add sign values
            # this is all pretty much a gross placeholder
            height, width, channel = img.shape
            bytesPerLine = 3 * width
            qimg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888)
            # item.setIconSize(100, 100)
            self.table.setItem(i, 0, QTableWidgetItem(QIcon(QPixmap(qimg)), ""))
            self.table.setItem(
                i, 1, QTableWidgetItem(unicodedata.name(chr(int(char_list[i]))))
            )

        self.table.setIconSize(QSize(100, 100))
        self.table.resize(250, len(img_list) * 100 + 25)
