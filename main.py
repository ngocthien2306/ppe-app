from ui.home import HomeWindow
from PyQt5.QtWidgets import QApplication
import sys
from ui.background import show_background

if __name__ == "__main__":

    show_background()
    app = QApplication(sys.argv)
    window = HomeWindow()
    window.show()
    sys.exit(app.exec_())
