
from pathlib import Path

from PySide6.QtWidgets import QTreeView,QWidget, QFileSystemModel
from PySide6.QtCore import Signal, QObject, Qt

class FileBrowserManager(QObject):
    file_clicked = Signal(Path)

    def __init__(self, parent_widget: QWidget, file_handler):
        super().__init__()
        self.parent_widget = parent_widget
        self.file_handler = file_handler
        self.tree_view = QTreeView()
        self._setup_tree_view()

    def _setup_tree_view(self):
        model = QFileSystemModel()
        root_path = self.file_handler.get_case_path()
        model.setRootPath(str(root_path))

        self.tree_view.setModel(model)
        self.tree_view.setRootIndex(model.index(str(root_path)))
        model.setHeaderData(0, Qt.Horizontal, "")
        
        self.tree_view.hideColumn(1) 
        self.tree_view.hideColumn(2) 
        self.tree_view.hideColumn(3) 

        self.tree_view.clicked.connect(self._handle_file_click)

    def _handle_file_click(self, index):
        model = index.model()
        file_path = Path(model.filePath(index))

        if not file_path.is_dir():
            self.file_clicked.emit(file_path)

    def get_widget(self) -> QTreeView:
        return self.tree_view

    def update_root_path(self):
        model = self.tree_view.model()
        root_path = self.file_handler.get_case_path()
        model.setRootPath(str(root_path))
        self.tree_view.setRootIndex(model.index(str(root_path)))
