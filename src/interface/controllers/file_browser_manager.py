
from pathlib import Path

from PySide6.QtWidgets import QTreeView,QWidget, QFileSystemModel
from PySide6.QtCore import Signal, QObject, Qt, QSortFilterProxyModel

class DirectoryFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Using a set for efficient lookup
        self.allowed_dirs = {"0", "system", "constant"}

    def filterAcceptsRow(self, source_row: int, source_parent) -> bool:
        """
        Determines whether a row from the source model should be included.
        """
        # Get the index for the row from the source QFileSystemModel
        source_index = self.sourceModel().index(source_row, 0, source_parent)

        if not source_index.isValid():
            return False

        # We only want to filter the top-level directories in the case folder.
        # We can identify them because their parent will be the root index.
        is_top_level = not source_parent.isValid() or source_parent == self.sourceModel().rootIndex()

        # Check if the item is a directory
        if self.sourceModel().isDir(source_index) and is_top_level:
            dir_name = self.sourceModel().fileName(source_index)
            return dir_name in self.allowed_dirs

        # For all files, and for directories inside the allowed ones (0, system, etc.),
        # always return True to show them. The file name filter is handled by the source model.
        return True

class FileBrowserManager(QObject):
    file_clicked = Signal(Path)

    def __init__(self, parent_widget: QWidget, file_handler):
        super().__init__()
        self.parent_widget = parent_widget
        self.file_handler = file_handler
        self.tree_view = QTreeView()
        self._setup_tree_view()

    def _setup_tree_view(self):
        # The QFileSystemModel will be the source model
        file_system_model = QFileSystemModel()
        root_path = self.file_handler.get_case_path()

        # Get the list of editable filenames from the file_handler
        editable_files = list(self.file_handler.files.keys())
        
        # Apply the filename filter to the source model
        file_system_model.setNameFilters(editable_files)
        file_system_model.setNameFilterDisables(False)  # Ensures the filter hides non-matching files

        # Set the root path on the source model
        file_system_model.setRootPath(str(root_path))

        # Create our custom proxy model to filter directories
        proxy_model = DirectoryFilterProxyModel()
        proxy_model.setSourceModel(file_system_model)

        # Set the proxy model on the tree view
        self.tree_view.setModel(proxy_model)

        # Map the root path from the source model to the proxy model
        source_root_index = file_system_model.index(str(root_path))
        proxy_root_index = proxy_model.mapFromSource(source_root_index)
        self.tree_view.setRootIndex(proxy_root_index)

        # We can set header data on the proxy model
        proxy_model.setHeaderData(0, Qt.Horizontal, "")
        
        # Hide the columns for size, type, date modified
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
        proxy_model = self.tree_view.model()
        if not isinstance(proxy_model, QSortFilterProxyModel):
            # Fallback for safety, though it shouldn't be needed
            return

        source_model = proxy_model.sourceModel()

        root_path = self.file_handler.get_case_path()
        source_model.setRootPath(str(root_path))

        source_root_index = source_model.index(str(root_path))
        proxy_root_index = proxy_model.mapFromSource(source_root_index)
        self.tree_view.setRootIndex(proxy_root_index)
