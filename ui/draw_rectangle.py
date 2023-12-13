from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPainter, QPen

class SelectableImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_point = None
        self.end_point = None

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.start_point and self.end_point:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            rect = QRectF(self.start_point, self.end_point)
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        self.start_point = event.pos()
        self.end_point = None
        self.update()

    def mouseMoveEvent(self, event):
        self.end_point = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end_point = event.pos()
        self.update()