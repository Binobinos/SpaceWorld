from PySide6.QtCore import QSize
from PySide6.QtGui import QMouseEvent, QIcon
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QHBoxLayout,
    QListWidget, QListWidgetItem, QStackedWidget,
    QScrollArea, QGraphicsDropShadowEffect
)

from Console import *
from CustomTitleBar import CustomTitleBar
from SettingsDialog import *
from config import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.is_maximized = False  # Флаг для отслеживания состояния окна
        self.init_ui()
        self.apply_theme(self.config["window"]["theme"])
        self.dragging = True
        self.offset = None


    def toggle_maximize(self):
        """
        Переключает между полноэкранным и обычным режимом окна.
        """
        if not self.is_maximized:
            self.showNormal()  # Вызываем метод из MainWindow
            self.is_maximized = True
        else:
            self.showMaximized()  # Вызываем метод из MainWindow
            self.is_maximized = False

    def showMaximized(self):
        """
        Разворачивает окно на весь экран.
        """
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen_geometry)

    def showNormal(self):
        """
        Возвращает окно в нормальный режим.
        """
        self.setGeometry(
            QApplication.primaryScreen().availableGeometry().center().x() - self.config["window"]["width"] // 2,
            QApplication.primaryScreen().availableGeometry().center().y() - self.config["window"]["height"] // 2,
            self.config["window"]["width"],
            self.config["window"]["height"]
        )

    def init_ui(self):
        """
        Инициализирует пользовательский интерфейс.
        """
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window | Qt.WindowMaximizeButtonHint)
        self.setWindowIcon(QIcon(self.config["window"]["default_icon"]))

        # Тень вокруг окна
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(float(self.config["window"]["shadow"]["blur_radius"]))
        self.shadow.setColor(QColor(*self.config["window"]["shadow"]["color"]))
        self.shadow.setOffset(*self.config["window"]["shadow"]["offset"])
        self.setGraphicsEffect(self.shadow)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)

        # Стек виджетов для переключения между экранами
        self.stacked_widget = QStackedWidget()

        # Главный экран с утилитами
        self.main_screen = QScrollArea()
        self.main_screen.setWidgetResizable(True)

        utilities_widget = QWidget()
        self.utilities_layout = QVBoxLayout(utilities_widget)
        self.utilities_layout.setAlignment(Qt.AlignTop)

        # Список утилит
        self.utilities_list = QListWidget()
        self.utilities_list.setIconSize(QSize(64, 64))
        self.utilities_list.setSpacing(10)
        self.utilities_list.itemClicked.connect(self.show_utility)

        self.utilities_layout.addWidget(self.utilities_list)
        self.main_screen.setWidget(utilities_widget)
        self.stacked_widget.addWidget(self.main_screen)

        # Экран консоли
        self.console_screen = CustomConsole(self.config, self)
        self.stacked_widget.addWidget(self.console_screen)

        # Кнопки управления
        control_buttons = QWidget()
        buttons_layout = QHBoxLayout(control_buttons)

        self.btn_settings = QPushButton("Settings")
        self.btn_console = QPushButton("Console")
        self.btn_back = QPushButton("Back")

        self.btn_settings.clicked.connect(self.show_settings)
        self.btn_console.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.console_screen))
        self.btn_back.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.main_screen))

        buttons_layout.addWidget(self.btn_settings)
        buttons_layout.addWidget(self.btn_console)
        buttons_layout.addWidget(self.btn_back)

        # Сборка интерфейса
        main_layout.addWidget(CustomTitleBar(self, self.config))
        main_layout.addWidget(self.stacked_widget, 1)
        main_layout.addWidget(control_buttons)

        self.load_utilities()
        self.setGeometry(
            QApplication.primaryScreen().availableGeometry().center().x() - self.config["window"]["width"] // 2,
            QApplication.primaryScreen().availableGeometry().center().y() - self.config["window"]["height"] // 2,
            self.config["window"]["width"],
            self.config["window"]["height"]
        )

    def mousePressEvent(self, event: QMouseEvent):
        """
        Обрабатывает нажатие мыши для перемещения окна.
        """
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Обрабатывает перемещение мыши для перемещения окна.
        """
        if self.dragging and self.offset:
            self.move(event.globalPosition().toPoint() - self.offset)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Обрабатывает отпускание мыши.
        """
        self.dragging = False
        self.offset = None

    def load_utilities(self):
        """
        Загружает утилиты из конфигурации.
        """
        self.utilities_list.clear()
        for utility in self.config["utilities"]:
            item = QListWidgetItem(utility["name"])
            try:
                icon = QIcon(utility["icon"])
                if icon.isNull():
                    raise Exception()
            except:
                icon = QIcon(self.config["window"]["default_icon"])
            item.setIcon(icon)
            self.utilities_list.addItem(item)

    def show_utility(self, item):
        """
        Открывает окно утилиты.
        """
        utility_window = QMainWindow(self)
        utility_window.setWindowTitle(item.text())
        utility_window.setCentralWidget(QTextEdit(f"Settings for {item.text()}"))
        utility_window.show()

    def show_settings(self):
        """
        Открывает диалог настроек.
        """
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec()

    def apply_theme(self, theme):
        """
        Применяет выбранную тему.
        """
        self.config["window"]["theme"] = theme
        save_config(self.config)
        theme_data = self.config["themes"][theme]

        style = f"""
            QMainWindow {{
                background-color: {theme_data['main_bg']};
                border-radius: {self.config["window"]["border_radius"]};
            }}
            QWidget {{
                background-color: {theme_data['main_bg']};
                color: {theme_data['text_color']};
            }}
            QListWidget {{
                background-color: {theme_data['main_bg']};
                border: 1px solid {theme_data['border_color']};
                border-radius: 5px;
                padding: 10px;
            }}
            QListWidget::item {{
                padding: 15px;
                border-bottom: 1px solid {theme_data['border_color']};
                font-size: 14px;
            }}
            QListWidget::item:hover {{
                background-color: {theme_data['button_bg']};
            }}
            QListWidget::item:selected {{
                background-color: {theme_data['button_bg']};
            }}
            QPushButton {{
                background-color: {theme_data['button_bg']};
                color: {theme_data['text_color']};
                border: 1px solid {theme_data['border_color']};
                border-radius: 5px;
                padding: 10px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {theme_data['button_bg']}dd;
            }}
            #window_button {{
                font-size: 16px;
                font-weight: bold;
            }}
        """
        self.setStyleSheet(style)
        self.console_screen.set_theme(theme_data)
