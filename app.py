import sys

from PyQt5.QtWidgets import QApplication
from guiqt           import *
from style_config    import STYLE_APP


if __name__ == "__main__":
    app = QApplication(sys.argv)

    DarkTheme.apply(app)

    app.setStyleSheet(STYLE_APP)

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
