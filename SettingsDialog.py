from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout, QPushButton, QLabel, QDialog, QSlider, QComboBox
)


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
        self.theme_label = QLabel("Select Theme:")
        self.theme_combobox = QComboBox()
        self.theme_combobox.addItems(["dark", "light", "blue"])
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
