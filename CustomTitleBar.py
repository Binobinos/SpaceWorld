from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout,
    QPushButton, QLabel
)


class CustomTitleBar(QWidget):
    """
    Кастомный заголовок окна с кнопками управления и иконкой приложения.
    """
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.setFixedHeight(40)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(15)

        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon(self.config["window"]["default_icon"]).pixmap(24, 24))
        self.icon_label.setStyleSheet("border: 1px solid #555; border-radius: 5px; padding: 2px;")
        layout.addWidget(self.icon_label)

        self.title = QLabel(self.config["window"]["title"])
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title, 1)

        self.minimize_btn = QPushButton("-")
        self.maximize_btn = QPushButton("□")
        self.close_btn = QPushButton("×")

        for btn in [self.minimize_btn, self.maximize_btn, self.close_btn]:
            btn.setFixedSize(40, 40)
            btn.setObjectName("window_button")

        self.minimize_btn.clicked.connect(parent.showMinimized)
        self.maximize_btn.clicked.connect(parent.toggle_maximize)
        self.close_btn.clicked.connect(parent.close)

        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(self.close_btn)
        self.parent = parent

    def toggle_maximize(self):
        """
        Переключает между полноэкранным и обычным режимом окна.
        """
        parent = self.parent  # Получаем ссылку на MainWindow
        if parent.isMaximized:
            parent.showNormal()  # Вызываем метод из MainWindow
            parent.is_maximized = False
        else:
            parent.showMaximized()  # Вызываем метод из MainWindow
            parent.is_maximized = True

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """
        Обрабатывает двойной клик по заголовку окна для разворачивания.
        """
        parent = self.parent
        if event.button() == Qt.LeftButton:
            parent.toggle_maximize()
