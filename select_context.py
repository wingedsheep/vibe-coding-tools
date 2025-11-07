import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QListWidget, QFileDialog,
                             QMessageBox, QLabel, QCheckBox)
from PyQt6.QtCore import Qt, QEvent, QMimeData, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut, QDragEnterEvent, QDropEvent
import pyperclip


class DragDropListWidget(QListWidget):
    filesDropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = str(url.toLocalFile())
                    if os.path.isdir(file_path):
                        for root, _, files in os.walk(file_path):
                            for file in files:
                                links.append(os.path.join(root, file))
                    else:
                        links.append(file_path)
            self.filesDropped.emit(links)
        else:
            event.ignore()


class ContextFileCreator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Context File Creator")
        self.setGeometry(100, 100, 600, 400)

        self.selected_files = []
        self.root_folder = ""
        self.ignore_build_folders = True
        self.ignore_jars = True
        self.ignore_git = True

        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.root_label = QLabel("Root: Not set")
        layout.addWidget(self.root_label)

        filter_layout = QHBoxLayout()
        self.ignore_build_checkbox = QCheckBox("Ignore build folders")
        self.ignore_build_checkbox.setChecked(True)
        self.ignore_build_checkbox.stateChanged.connect(self.update_ignore_build)
        filter_layout.addWidget(self.ignore_build_checkbox)

        self.ignore_jars_checkbox = QCheckBox("Ignore JAR files")
        self.ignore_jars_checkbox.setChecked(True)
        self.ignore_jars_checkbox.stateChanged.connect(self.update_ignore_jars)
        filter_layout.addWidget(self.ignore_jars_checkbox)

        self.ignore_git_checkbox = QCheckBox("Ignore .git/.idea folders")
        self.ignore_git_checkbox.setChecked(True)
        self.ignore_git_checkbox.stateChanged.connect(self.update_ignore_git)
        filter_layout.addWidget(self.ignore_git_checkbox)

        layout.addLayout(filter_layout)

        self.file_list = DragDropListWidget()
        self.file_list.filesDropped.connect(self.add_dropped_files)
        layout.addWidget(self.file_list)

        self.delete_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Delete), self.file_list)
        self.delete_shortcut.activated.connect(self.remove_selected_file)

        button_layout = QHBoxLayout()

        add_files_btn = QPushButton("Add Files")
        add_files_btn.clicked.connect(self.add_files)
        button_layout.addWidget(add_files_btn)

        add_folder_btn = QPushButton("Add Folder")
        add_folder_btn.clicked.connect(self.add_folder)
        button_layout.addWidget(add_folder_btn)

        select_root_btn = QPushButton("Select Root")
        select_root_btn.clicked.connect(self.select_root)
        button_layout.addWidget(select_root_btn)

        remove_file_btn = QPushButton("Remove File")
        remove_file_btn.clicked.connect(self.remove_selected_file)
        button_layout.addWidget(remove_file_btn)

        clear_files_btn = QPushButton("Clear Files")
        clear_files_btn.clicked.connect(self.clear_files)
        button_layout.addWidget(clear_files_btn)

        create_markdown_btn = QPushButton("Create Markdown")
        create_markdown_btn.clicked.connect(self.create_markdown)
        button_layout.addWidget(create_markdown_btn)

        layout.addLayout(button_layout)

    def should_ignore(self, path):
        path_parts = path.split(os.sep)

        if self.ignore_build_folders:
            build_folder_names = ['build', 'target', 'out', '.gradle']
            if any(folder in path_parts for folder in build_folder_names):
                return True

        if self.ignore_git:
            git_folders = ['.git', '.idea']
            if any(folder in path_parts for folder in git_folders):
                return True

        if self.ignore_jars and path.lower().endswith('.jar'):
            return True

        return False

    def update_ignore_build(self, state):
        self.ignore_build_folders = state == Qt.CheckState.Checked.value

    def update_ignore_jars(self, state):
        self.ignore_jars = state == Qt.CheckState.Checked.value

    def update_ignore_git(self, state):
        self.ignore_git = state == Qt.CheckState.Checked.value

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        filtered_files = [f for f in files if not self.should_ignore(f)]
        self.add_files_without_duplicates(filtered_files)
        self.update_root_folder()

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            files_to_add = []
            for root, _, files in os.walk(folder):
                if self.should_ignore(root):
                    continue
                for file in files:
                    file_path = os.path.join(root, file)
                    if not self.should_ignore(file_path):
                        files_to_add.append(file_path)
            self.add_files_without_duplicates(files_to_add)
            self.update_root_folder()

    def add_dropped_files(self, file_paths):
        filtered_files = [f for f in file_paths if not self.should_ignore(f)]
        self.add_files_without_duplicates(filtered_files)
        self.update_root_folder()

    def add_files_without_duplicates(self, files):
        added = 0
        skipped = 0
        for file in files:
            if file not in self.selected_files:
                self.selected_files.append(file)
                added += 1
            else:
                skipped += 1

        self.update_file_list()

        if skipped > 0:
            QMessageBox.information(
                self,
                "Files Added",
                f"Added {added} files. Skipped {skipped} duplicate files."
            )

    def select_root(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Root Folder")
        if folder:
            self.root_folder = folder
            self.update_root_folder()
            QMessageBox.information(self, "Root Folder", f"Root folder set to: {self.root_folder}")

    def remove_selected_file(self):
        current_item = self.file_list.currentItem()
        if current_item:
            file_path = current_item.text()
            self.selected_files.remove(file_path)
            self.update_file_list()
            self.update_root_folder()

    def clear_files(self):
        self.selected_files.clear()
        self.update_file_list()
        self.update_root_folder()

    def update_file_list(self):
        self.file_list.clear()
        for file in self.selected_files:
            self.file_list.addItem(file)

    def update_root_folder(self):
        if self.selected_files:
            self.root_folder = os.path.commonpath(self.selected_files)
        else:
            self.root_folder = ""
        self.root_label.setText(f"Root: {self.root_folder}")

    def get_file_structure(self):
        if not self.selected_files:
            return "No files selected."

        tree = {}
        for file in self.selected_files:
            rel_path = os.path.relpath(file, self.root_folder)
            parts = rel_path.split(os.sep)
            current = tree
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = None

        def build_tree(structure, prefix=""):
            lines = []
            items = list(structure.items())
            for i, (name, subtree) in enumerate(items):
                if i == len(items) - 1:
                    lines.append(f"{prefix}└───{name}")
                    if subtree is not None:
                        lines.extend(build_tree(subtree, prefix + "    "))
                else:
                    lines.append(f"{prefix}├───{name}")
                    if subtree is not None:
                        lines.extend(build_tree(subtree, prefix + "│   "))
            return lines

        return "\n".join(build_tree(tree))

    def create_markdown(self):
        if not self.selected_files:
            QMessageBox.warning(self, "No Files", "No files selected.")
            return

        markdown = "# File Structure\n\n\n"
        markdown += "```\n" + self.get_file_structure() + "\n```"
        markdown += "\n\n\n# File Contents\n\n"

        for file in self.selected_files:
            rel_path = os.path.relpath(file, self.root_folder)
            markdown += f"## {rel_path}\n\n"

            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    file_ext = os.path.splitext(file)[1]
                    markdown += f"```{file_ext[1:]}\n{content}\n```\n\n"
            except Exception as e:
                markdown += f"Error reading file: {str(e)}\n\n"

        pyperclip.copy(markdown)
        QMessageBox.information(self, "Markdown Created", "Markdown has been copied to clipboard.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ContextFileCreator()
    ex.show()
    sys.exit(app.exec())
