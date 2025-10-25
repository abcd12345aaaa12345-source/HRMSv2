STYLE_APP = """
        QMainWindow {
            background-color: #2b2b2b;
        }
        QWidget {
            color: #ffffff;
        }
        QTableWidget {
            background-color: #353535;
            color: white;
            gridline-color: #555;
            alternate-background-color: #3a3a3a;
        }
        QTableWidget::item {
            padding: 5px;
            border-bottom: 1px solid #555;
        }
        QTableWidget::item:selected {
            background-color: #2a82da;
        }
        QHeaderView::section {
            background-color: #404040;
            color: white;
            padding: 5px;
            border: 1px solid #555;
            font-weight: bold;
        }
        QListWidget {
            background-color: #353535;
            color: white;
            border: 1px solid #555;
            outline: none;
        }
        QListWidget::item {
            padding: 8px;
            border-bottom: 1px solid #555;
        }
        QListWidget::item:selected {
            background-color: #2a82da;
            color: white;
        }
        QTextEdit {
            background-color: #353535;
            color: white;
            border: 1px solid #555;
            padding: 5px;
        }
        QLineEdit {
            background-color: #353535;
            color: white;
            border: 1px solid #555;
            padding: 5px;
            border-radius: 3px;
        }
        QLineEdit:focus {
            border: 1px solid #2a82da;
        }
        QComboBox {
            background-color: #353535;
            color: white;
            border: 1px solid #555;
            padding: 5px;
            border-radius: 3px;
        }
        QComboBox:focus {
            border: 1px solid #2a82da;
        }
        QComboBox QAbstractItemView {
            background-color: #353535;
            color: white;
            border: 1px solid #555;
            selection-background-color: #2a82da;
        }
        QCalendarWidget {
            background-color: #353535;
            color: white;
        }
        QCalendarWidget QWidget {
            alternate-background-color: #353535;
        }
        QCalendarWidget QToolButton {
            color: white;
            background-color: #404040;
            font-weight: bold;
        }
        QCalendarWidget QMenu {
            background-color: #404040;
            color: white;
        }
        QCalendarWidget QSpinBox {
            background-color: #353535;
            color: white;
            border: 1px solid #555;
        }
        QDialog {
            background-color: #2b2b2b;
            color: white;
        }
        QLabel {
            color: white;
            background-color: transparent;
        }
        QGroupBox {
            color: white;
            font-weight: bold;
            border: 1px solid #555;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QPushButton {
            background-color: #404040;
            color: white;
            border: 1px solid #555;
            padding: 8px 15px;
            border-radius: 3px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #505050;
            border: 1px solid #666;
        }
        QPushButton:pressed {
            background-color: #606060;
        }
        QPushButton:disabled {
            background-color: #303030;
            color: #777;
        }
        QTabWidget::pane {
            border: 1px solid #555;
            background-color: #353535;
        }
        QTabBar::tab {
            background-color: #404040;
            color: white;
            padding: 8px 15px;
            border: 1px solid #555;
            border-bottom: none;
            border-top-left-radius: 3px;
            border-top-right-radius: 3px;
        }
        QTabBar::tab:selected {
            background-color: #2a82da;
            color: white;
        }
        QTabBar::tab:!selected {
            margin-top: 2px;
        }
        QMenuBar {
            background-color: #404040;
            color: white;
            border-bottom: 1px solid #555;
        }
        QMenuBar::item {
            background-color: transparent;
            padding: 5px 10px;
        }
        QMenuBar::item:selected {
            background-color: #505050;
        }
        QMenu {
            background-color: #404040;
            color: white;
            border: 1px solid #555;
        }
        QMenu::item {
            padding: 5px 20px;
        }
        QMenu::item:selected {
            background-color: #2a82da;
        }
        QToolBar {
            background-color: #404040;
            border: 1px solid #555;
            spacing: 3px;
            padding: 3px;
        }
        QStatusBar {
            background-color: #404040;
            color: white;
            border-top: 1px solid #555;
        }
        QSplitter::handle {
            background-color: #555;
            width: 1px;
        }
        QSplitter::handle:hover {
            background-color: #2a82da;
        }
        QScrollBar:vertical {
            background-color: #353535;
            width: 15px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background-color: #555;
            min-height: 20px;
            border-radius: 7px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #666;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
    """