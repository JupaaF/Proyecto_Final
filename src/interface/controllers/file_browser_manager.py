
from pathlib import Path

from PySide6.QtWidgets import QTreeView, QWidget, QFileSystemModel
from PySide6.QtCore import Signal, QObject, Qt, QSortFilterProxyModel

from .file_browser_proxy_model import FileBrowserProxyModel

class FileBrowserManager(QObject):
    file_clicked = Signal(Path)

    def __init__(self, parent_widget: QWidget, file_handler):
        super().__init__()
        self.parent_widget = parent_widget
        self.file_handler = file_handler
        self.tree_view = QTreeView()
        self.proxy_model = FileBrowserProxyModel()
        self._setup_tree_view()

    def _setup_tree_view(self):
        source_model = QFileSystemModel()
        root_path = self.file_handler.get_case_path()

        editable_files = list(self.file_handler.files.keys())
        
        source_model.setNameFilters(editable_files)
        source_model.setNameFilterDisables(False)
        source_model.setRootPath(str(root_path))

        self.proxy_model.setSourceModel(source_model)

        self.tree_view.setModel(self.proxy_model)

        root_index = source_model.index(str(root_path))
        proxy_root_index = self.proxy_model.mapFromSource(root_index)
        self.tree_view.setRootIndex(proxy_root_index)

        self.tree_view.setSortingEnabled(True)
        self.proxy_model.sort(0, Qt.AscendingOrder)

        source_model.setHeaderData(0, Qt.Horizontal, "")
        
        self.tree_view.hideColumn(1) 
        self.tree_view.hideColumn(2) 
        self.tree_view.hideColumn(3) 

        self.tree_view.clicked.connect(self._handle_file_click)

    def _handle_file_click(self, proxy_index):
        source_index = self.proxy_model.mapToSource(proxy_index)
        source_model = self.proxy_model.sourceModel()
        file_path = Path(source_model.filePath(source_index))

        if not file_path.is_dir():
            self.file_clicked.emit(file_path)

    def get_widget(self) -> QTreeView:
        return self.tree_view

    def update_root_path(self):
        source_model = self.proxy_model.sourceModel()
        root_path = self.file_handler.get_case_path()

        source_model.setRootPath(str(root_path))
        root_index = source_model.index(str(root_path))
        proxy_root_index = self.proxy_model.mapFromSource(root_index)
        self.tree_view.setRootIndex(proxy_root_index)
