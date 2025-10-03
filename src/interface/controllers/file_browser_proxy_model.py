from PySide6.QtCore import QSortFilterProxyModel, QModelIndex
from PySide6.QtWidgets import QFileSystemModel

class FileBrowserProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSortCaseSensitivity(False)

    def lessThan(self, source_left: QModelIndex, source_right: QModelIndex) -> bool:
        model = self.sourceModel()

        left_is_dir = model.isDir(source_left)
        right_is_dir = model.isDir(source_right)

        # Rule 1: Directories always come before files
        if left_is_dir and not right_is_dir:
            return True
        if not left_is_dir and right_is_dir:
            return False

        left_name = model.fileName(source_left)
        right_name = model.fileName(source_right)

        # Rule 2: If both are directories, apply priority sorting
        if left_is_dir and right_is_dir:
            priority_order = ["0", "constant", "system"]

            left_is_priority = left_name in priority_order
            right_is_priority = right_name in priority_order

            if left_is_priority and right_is_priority:
                return priority_order.index(left_name) < priority_order.index(right_name)

            if left_is_priority:
                return True

            if right_is_priority:
                return False

        # Rule 3: For everything else (files, or non-priority dirs), sort alphabetically
        return super().lessThan(source_left, source_right)