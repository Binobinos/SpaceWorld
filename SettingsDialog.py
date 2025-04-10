import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QComboBox, QLabel,
                              QSlider, QPushButton, QFileDialog, QHBoxLayout,
                              QLineEdit, QToolButton)

from config import load_config


class SettingsDialog(QDialog):
    """
    Диалоговое окно настроек.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 300)
        self.layout = QVBoxLayout(self)

        # Выбор темы
        self.config = load_config()
        self.theme_label = QLabel("Select Theme:")
        self.theme_combobox = QComboBox()
        self.theme_combobox.addItems(self.config["themes"])
        self.theme_combobox.setCurrentText(parent.config["window"]["theme"])
        self.layout.addWidget(self.theme_label)
        self.layout.addWidget(self.theme_combobox)

        # Слайдер для изменения размера окна
        self.size_label = QLabel("Window Size:")
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setMinimum(400)
        self.size_slider.setMaximum(1200)
        self.size_slider.setValue(parent.config["window"]["width"])
        self.layout.addWidget(self.size_label)
        self.layout.addWidget(self.size_slider)

        # Кнопка сохранения
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        self.layout.addWidget(self.save_button)

    def save_settings(self):
        """
        Сохраняет настройки и применяет их.
        """
        theme = self.theme_combobox.currentText()
        size = self.size_slider.value()
        self.parent().apply_theme(theme)
        self.parent().resize(int(size), int(size * 0.75))
        self.close()


class UtilityWindow(QDialog):
    """
    Диалоговое окно утилит с настройками и выбором директории.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Utility")
        self.setFixedSize(400, 300)
        self.layout = QVBoxLayout(self)

        self.config = load_config()
        self.parent = parent

        self.dir_layout = QHBoxLayout()

        self.dir_label = QLabel("Рабочая директория:")
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Выберите папку сортировки")
        self.dir_input.setText(self.config.get("work_dir", ""))

        self.dir_button = QToolButton()
        self.dir_button.setText("...")
        self.dir_button.clicked.connect(self.select_directory)

        self.dir_layout.addWidget(self.dir_label)
        self.dir_layout.addWidget(self.dir_input)
        self.dir_layout.addWidget(self.dir_button)

        self.layout.addLayout(self.dir_layout)

        self.theme_label = QLabel("Выберите тип сортировки:")
        self.theme_combobox = QComboBox()
        self.theme_combobox.addItems(["Формат"])
        self.layout.addWidget(self.theme_label)
        self.layout.addWidget(self.theme_combobox)

        self.save_button = QPushButton("Сортировать")
        self.save_button.clicked.connect(self.prints)
        self.layout.addWidget(self.save_button)


    def prints(self):
        print(self.dir_path)

    def select_directory(self):
        """Открывает диалог выбора директории"""
        self.dir_path = QFileDialog.getExistingDirectory(
            self,
            "Выберите рабочую директорию",
            self.dir_input.text() or os.path.expanduser("~"),
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )

        if self.dir_path:
            self.dir_input.setText(self.dir_path)
