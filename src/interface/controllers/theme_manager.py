
from pathlib import Path

from PySide6.QtCore import QFile, QTextStream
from PySide6.QtWidgets import QWidget

class ThemeManager:
    def __init__(self, parent_widget: QWidget):
        self.parent_widget = parent_widget
        self.light_theme = ""
        self.dark_theme = ""
        self._load_styles()

    def _load_styles(self):
        resources_path = Path(__file__).parent.parent / "resources"
        
        light_theme_file = QFile(str(resources_path / "light_theme.qss"))
        light_theme_file.open(QFile.ReadOnly | QFile.Text)
        self.light_theme = QTextStream(light_theme_file).readAll()
        light_theme_file.close()

        dark_theme_file = QFile(str(resources_path / "dark_theme.qss"))
        dark_theme_file.open(QFile.ReadOnly | QFile.Text)
        self.dark_theme = QTextStream(dark_theme_file).readAll()
        dark_theme_file.close()

    def set_theme(self, dark_mode: bool):
        if dark_mode:
            self.parent_widget.setStyleSheet(self.dark_theme)
        else:
            self.parent_widget.setStyleSheet(self.light_theme)

