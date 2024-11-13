from PyQt5.QtWidgets import QWidget

# Modern dark theme styling
button_style = """
    QPushButton {
        background-color: #2b2b2b;
        color: #ffffff;
        border: 1px solid #3d3d3d;
        padding: 5px;
        border-radius: 3px;
    }
    QPushButton:hover {
        background-color: #3d3d3d;
    }
    QPushButton:pressed {
        background-color: #454545;
    }
"""

text_edit_style = """
    QTextEdit {
        background-color: #1e1e1e;
        color: #ffffff;
        border: 1px solid #3d3d3d;
        border-radius: 3px;
        padding: 5px;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 12pt;
        line-height: 1.5;
    }
"""

combo_box_style = """
    QComboBox {
        background-color: #2b2b2b;
        color: #ffffff;
        border: 1px solid #3d3d3d;
        padding: 5px;
        border-radius: 3px;
    }
    QComboBox::drop-down {
        border: none;
    }
    QComboBox::down-arrow {
        image: none;
        border-width: 0px;
    }
    QComboBox QAbstractItemView {
        background-color: #2b2b2b;
        color: #ffffff;
        selection-background-color: #3d3d3d;
    }
"""

class ModernWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QCheckBox {
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QCheckBox::indicator {
                width: 13px;
                height: 13px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #3d3d3d;
                background: #2b2b2b;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #3d3d3d;
                background: #007acc;
            }
        """)
