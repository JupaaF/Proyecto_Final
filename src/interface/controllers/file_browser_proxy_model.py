from PySide6.QtCore import QSortFilterProxyModel, QModelIndex
from PySide6.QtGui import QFileSystemModel

class FileBrowserProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSortCaseSensitivity(False)

    def lessThan(self, source_left: QModelIndex, source_right: QModelIndex) -> bool:
        model = self.sourceModel()

        left_is_dir = model.isDir(source_left)
        right_is_dir = model.isDir(source_right)

        if left_is_dir and not right_is_dir:
            return True
        if not left_is_dir and right_is_dir:
            return False

        left_name = model.fileName(source_left)
        right_name = model.fileName(source_right)

        priority_order = ["0", "constant", "system"]

        if left_name in priority_order and right_name in priority_order:
            return priority_order.index(left_name) < priority_order.index(right_name)

        if left_name in priority_order:
            return True

        if right_name in priority_order:
            return False

        return super().lessThan(source_left, source_right)