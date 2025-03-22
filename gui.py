import datetime
import sys
import re
import json
import logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QListWidgetItem, QStackedWidget,
    QTextEdit, QLineEdit, QScrollArea, QDialog, QGraphicsDropShadowEffect, QSlider, QComboBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QMouseEvent, QIcon, QColor, QTextCharFormat, QSyntaxHighlighter, QFont
from PySide6.QtCore import QEvent  # Добавьте этот импорт

def setup_logging(config):
    """
    Настраивает логирование на основе конфигурации.
    """
    logging.basicConfig(
        level=getattr(logging, config["logging"]["level"]),
        filename=config["logging"]["file"],
        format=config["logging"]["format"]
    )
    logging.info("Логирование настроено.")


def load_config():
    """
    Загружает конфигурацию из файла config.json.
    Если файл отсутствует, используется конфигурация по умолчанию.
    """
    try:
        with open("config.json", "r") as file:
            config = json.load(file)
            logging.info("Конфигурация загружена.")
            return config
    except FileNotFoundError:
        logging.warning("Файл config.json не найден. Используется конфигурация по умолчанию.")
        return {
            "window": {
                "width": 800,
                "height": 600,
                "theme": "dark",
                "border_radius": "10px",
                "default_icon": "default_icon.png",
                "title": "Space World",
                "shadow": {
                    "blur_radius": 15,
                    "color": [0, 0, 0, 150],
                    "offset": [0, 0]
                }
            },
            "themes": {
                "dark": {
                    "main_bg": "#2d2d2d",
                    "title_bg": "#1a1a1a",
                    "text_color": "#ffffff",
                    "button_bg": "#444",
                    "console_bg": "#1e1e1e",
                    "input_bg": "#252526",
                    "border_color": "#555"
                },
                "light": {
                    "main_bg": "#f0f0f0",
                    "title_bg": "#d0d0d0",
                    "text_color": "#000000",
                    "button_bg": "#ddd",
                    "console_bg": "#ffffff",
                    "input_bg": "#f0f0f0",
                    "border_color": "#ccc"
                },
                "blue": {
                    "main_bg": "#001f3f",
                    "title_bg": "#003366",
                    "text_color": "#ffffff",
                    "button_bg": "#004080",
                    "console_bg": "#002b4d",
                    "input_bg": "#003366",
                    "border_color": "#0059b3"
                }
            },
            "utilities": [
                {"name": "Utility 1", "icon": "icon1.png"},
                {"name": "Utility 2", "icon": "icon2.png"},
                {"name": "Utility 3", "icon": "icon3.png"}
            ],
            "logging": {
                "level": "INFO",
                "file": "app.log",
                "format": "%(asctime)s - %(levelname)s - %(message)s"
            }
        }


def save_config(config):
    """
    Сохраняет конфигурацию в файл config.json.
    """
    with open("config.json", "w") as file:
        json.dump(config, file, indent=4)
        logging.info("Конфигурация сохранена.")


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

        # Иконка приложения
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon(self.config["window"]["default_icon"]).pixmap(24, 24))
        self.icon_label.setStyleSheet("border: 1px solid #555; border-radius: 5px; padding: 2px;")
        layout.addWidget(self.icon_label)

        # Заголовок окна
        self.title = QLabel(self.config["window"]["title"])
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title, 1)

        # Кнопки управления окном
        self.minimize_btn = QPushButton("-")
        self.maximize_btn = QPushButton("□")
        self.close_btn = QPushButton("×")

        for btn in [self.minimize_btn, self.maximize_btn, self.close_btn]:
            btn.setFixedSize(40, 40)
            btn.setObjectName("window_button")

        self.minimize_btn.clicked.connect(parent.showMinimized)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        self.close_btn.clicked.connect(parent.close)

        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(self.close_btn)

    def toggle_maximize(self):
        """
        Переключает между полноэкранным и обычным режимом окна.
        """
        parent = self.parent()
        if parent.isMaximized():
            parent.showNormal()
        else:
            parent.showMaximized()


class ConsoleHighlighter(QSyntaxHighlighter):
    """
    Подсветка синтаксиса для консоли.
    """

    def __init__(self, document):
        super().__init__(document)
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#569CD6"))
        self.keyword_format.setFontWeight(QFont.Bold)
        self.keywords = ["echo", "help", "clear", "exit", "spaceworld"]

    def highlightBlock(self, text):
        """
        Подсвечивает ключевые слова в тексте.
        """
        for keyword in self.keywords:
            for match in re.finditer(rf"\b{keyword}\b", text, re.IGNORECASE):
                self.setFormat(match.start(), match.end() - match.start(), self.keyword_format)


class CustomConsole(QWidget):
    """
    Кастомная консоль с полем ввода и выводом.
    """

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(10)

        # Поле вывода
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setLineWrapMode(QTextEdit.NoWrap)

        # Поле ввода
        self.input = QLineEdit()
        self.input.returnPressed.connect(self.execute_command)
        self.input.installEventFilter(self)  # Для обработки событий клавиш

        self.layout.addWidget(self.output)
        self.layout.addWidget(self.input)

        self.highlighter = ConsoleHighlighter(self.output.document())
        self.output.append("SpaceWorld [Version 1.0.0]")
        self.output.append("(c) Binobinos official. Все права защищены.")

        # История команд
        self.command_history = []
        self.history_index = -1

        # Доступные команды
        self.available_commands = ["help", "clear", "echo", "spaceworld", "data"]

    def eventFilter(self, source, event):
        """
        Обрабатывает события клавиш для навигации по истории команд и автодополнения.
        """
        if event.type() == QEvent.Type.KeyPress and source == self.input:  # Исправлено здесь
            if event.key() == Qt.Key_Up:  # Стрелка вверх
                self.navigate_history(-1)
                return True
            elif event.key() == Qt.Key_Down:  # Стрелка вниз
                self.navigate_history(1)
                return True
            elif event.key() == Qt.Key_Tab:  # Tab для автодополнения
                self.auto_complete()
                return True
        return super().eventFilter(source, event)

    def navigate_history(self, direction):
        """
        Навигация по истории команд.
        """
        if not self.command_history:
            return

        # Обновляем индекс истории
        self.history_index += direction

        # Ограничиваем индекс в пределах истории
        if self.history_index < 0:
            self.history_index = 0
        elif self.history_index >= len(self.command_history):
            self.history_index = len(self.command_history) - 1

        # Устанавливаем текст из истории
        self.input.setText(self.command_history[self.history_index])

    def auto_complete(self):
        """
        Автодополнение команд.
        """
        current_text = self.input.text().strip()
        if not current_text:
            return

        # Ищем команды, которые начинаются с текущего текста
        matching_commands = [cmd for cmd in self.available_commands if cmd.startswith(current_text)]

        if matching_commands:
            # Если найдена одна команда, автодополняем
            if len(matching_commands) == 1:
                self.input.setText(matching_commands[0])
            else:
                # Если несколько команд, выводим их в консоль
                self.output.append("Доступные команды:")
                for cmd in matching_commands:
                    self.output.append(f"  - {cmd}")

    def execute_command(self):
        """
        Выполняет команду, введенную в консоли.
        """
        command = self.input.text().strip()
        self.output.append(f"> {command}")
        self.input.clear()

        # Добавляем команду в историю
        if command:
            self.command_history.append(command)
            self.history_index = len(self.command_history)

        if command.lower() == "clear":
            self.output.clear()
            self.output.append("SpaceWorld [Version 1.0.0]")
            self.output.append("(c) Binobinos official. Все права защищены.")
        elif command.lower() == "help":
            self.show_help()
        elif command.lower().startswith("echo"):
            self.output.append(command[4:].strip())
        elif command.lower().startswith("spaceworld"):
            self.handle_spaceworld(command[10:].strip())
        else:
            self.output.append(f"Unknown command: {command}")

    def show_help(self):
        """
        Показывает справку по командам.
        """
        help_text = """
        Available commands:
        - help: Show this help message
        - clear: Clear the console
        - echo [text]: Print text to console
        - spaceworld [command]: SpaceWorld specific commands
        """
        self.output.append(help_text.strip())

    def handle_spaceworld(self, command):
        """
        Обрабатывает команды, связанные с SpaceWorld.
        """
        if command == "version":
            self.output.append("SpaceWorld Console v1.0")
        elif command.startswith("datatime"):
            command = command.split()[1]
            if command == "time":
                pass
            elif command == "datatime":
                self.output.append(str(datetime.datetime.now()))
            elif command == "data":
                self.output.append(str(datetime.datetime.now()))
        else:
            self.output.append(f"Unknown SpaceWorld command: {command}")

    def set_theme(self, theme_data):
        """
        Применяет тему к консоли.
        """
        self.setStyleSheet(f"""
            QTextEdit, QLineEdit {{
                background-color: {theme_data['console_bg']};
                color: {theme_data['text_color']};
                border: 1px solid {theme_data['border_color']};
                border-radius: 5px;
                font-family: Consolas;
                font-size: 12px;
                padding: 5px;
            }}
            QLineEdit {{
                background-color: {theme_data['input_bg']};
            }}
        """)


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
        self.parent().resize(size, size * 0.75)
        self.close()


class MainWindow(QMainWindow):
    """
    Главное окно приложения.
    """

    def __init__(self):
        super().__init__()
        self.config = load_config()
        setup_logging(self.config)
        self.init_ui()
        self.apply_theme(self.config["window"]["theme"])
        self.dragging = False  # Флаг для перемещения окна
        self.offset = None  # Смещение для корректного перемещения

    def init_ui(self):
        """
        Инициализирует пользовательский интерфейс.
        """
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setWindowIcon(QIcon(self.config["window"]["default_icon"]))

        # Тень вокруг окна
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(self.config["window"]["shadow"]["blur_radius"])
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
        self.console_screen = CustomConsole(self.config)
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())