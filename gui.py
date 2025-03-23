import datetime
import json
import logging
import os
import random
import re
import socket
import sys
import threading
import psutil
import speedtest
from PySide6.QtCore import QEvent  # Добавьте этот импорт
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QMouseEvent, QIcon, QColor, QTextCharFormat, QSyntaxHighlighter, QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QListWidgetItem, QStackedWidget,
    QTextEdit, QLineEdit, QScrollArea, QDialog, QGraphicsDropShadowEffect, QSlider, QComboBox
)


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

        # Основные команды (синий)
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#569CD6"))  # Синий
        self.keyword_format.setFontWeight(QFont.Bold)
        self.keywords = ["help", "clear", "echo", "spaceworld", "exit"]

        # Подкоманды (зелёный)
        self.subcommand_format = QTextCharFormat()
        self.subcommand_format.setForeground(QColor("#4EC9B0"))  # Зелёный
        self.subcommands = ["file", "datatime", "dir"]

        # Аргументы (оранжевый)
        self.argument_format = QTextCharFormat()
        self.argument_format.setForeground(QColor("#CE9178"))  # Оранжевый
        self.arguments = ["create", "read", "write", "delete", "time", "date", "week", "year"]

        # Пути и имена файлов (серый)
        self.path_format = QTextCharFormat()
        self.path_format.setForeground(QColor("#808080"))  # Серый

    def highlightBlock(self, text):
        """
        Подсвечивает ключевые слова, подкоманды, аргументы и пути в тексте.
        """
        # Подсветка основных команд
        for keyword in self.keywords:
            for match in re.finditer(rf"\b{keyword}\b", text, re.IGNORECASE):
                self.setFormat(match.start(), match.end() - match.start(), self.keyword_format)

        # Подсветка подкоманд
        for subcommand in self.subcommands:
            for match in re.finditer(rf"\b{subcommand}\b", text, re.IGNORECASE):
                self.setFormat(match.start(), match.end() - match.start(), self.subcommand_format)

        # Подсветка аргументов
        for argument in self.arguments:
            for match in re.finditer(rf"\b{argument}\b", text, re.IGNORECASE):
                self.setFormat(match.start(), match.end() - match.start(), self.argument_format)

        # Подсветка путей и имён файлов
        for match in re.finditer(r"~[^\s]+", text):
            self.setFormat(match.start(), match.end() - match.start(), self.path_format)

class CustomConsole(QWidget):
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
        self.command_history = config.get('command_history', [])
        self.history_index = -1

        # Доступные команды
        self.available_commands = {
            "help": {},  # Пустой словарь, так как у команды help нет подкоманд
            "clear": {},  # Пустой словарь, так как у команды clear нет подкоманд
            "echo": {},  # Пустой словарь, так как у команды echo нет подкоманд
            "spaceworld": {
                "file": {
                    "create": {},
                    "read": {},
                    "write": {},
                    "delete": {},
                },
                "datatime": {
                    "time": {},
                    "data": {},
                    "week": {},
                    "year": {},
                },
                "dir": {
                    "create": {},
                    "delete": {},
                },
            },
        }

        # Флаги для запроса подтверждения
        self.waiting_for_confirmation = False
        self.confirmation_command = None

    def append_output(self, text, color=None, font=None):
        """
        Выводит текст в консоль с возможностью задания цвета и шрифта.
        """
        if color:
            self.output.setTextColor(QColor(color))
        if font:
            self.output.setCurrentFont(font)
        self.output.append(text)
        # Возвращаем стандартные настройки
        self.output.setTextColor(QColor(self.config["themes"][self.config["window"]["theme"]]["text_color"]))
        self.output.setCurrentFont(QFont("Consolas", 12))

    def eventFilter(self, source, event):
        """
        Обрабатывает события клавиш для навигации по истории команд и автодополнения.
        """
        if event.type() == QEvent.Type.KeyPress and source == self.input:
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
        Автодополнение команд и аргументов.
        """
        current_text = self.input.text().strip()
        if not current_text:
            return

        # Разделяем введённый текст на части
        parts = current_text.split()
        if not parts:
            return

        # Начинаем с корневого уровня команд
        current_level = self.available_commands

        # Проходим по всем частям команды
        for i, part in enumerate(parts):
            part = part.lower()
            if part in current_level:
                current_level = current_level[part]
            else:
                # Если часть команды не найдена, ищем варианты автодополнения
                matching_commands = [cmd for cmd in current_level.keys() if cmd.startswith(part)]
                if matching_commands:
                    if len(matching_commands) == 1:
                        # Если совпадение одно, подставляем его
                        parts[i] = matching_commands[0]
                        self.input.setText(" ".join(parts) + " ")
                    else:
                        # Если совпадений несколько, выводим их в консоль
                        self.append_output("Доступные команды:", color="#569CD6")
                        for cmd in matching_commands:
                            self.append_output(f"  - {cmd}", color="#569CD6")
                    return

        # Если все части команды найдены, предлагаем подкоманды
        if current_level:
            subcommands = list(current_level.keys())
            if len(subcommands) == 1:
                # Если подкоманда одна, подставляем её
                self.input.setText(" ".join(parts + [subcommands[0]]) + " ")
            else:
                # Если подкоманд несколько, выводим их в консоль
                self.append_output("Доступные подкоманды:", color="#4EC9B0")
                for sub in subcommands:
                    self.append_output(f"  - {sub}", color="#4EC9B0")

        # Автодополнение для путей
        if parts[-1].startswith("~"):
            path = parts[-1][1:]
            dir_path = os.path.dirname(path)
            base_name = os.path.basename(path)
            if os.path.exists(dir_path):
                matching_files = [f for f in os.listdir(dir_path) if f.startswith(base_name)]
                if matching_files:
                    if len(matching_files) == 1:
                        # Если совпадение одно, подставляем его
                        new_path = os.path.join(dir_path, matching_files[0])
                        parts[-1] = "~" + new_path
                        self.input.setText(" ".join(parts) + " ")
                    else:
                        # Если совпадений несколько, выводим их в консоль
                        self.append_output("Доступные файлы/папки:", color="#808080")
                        for f in matching_files:
                            self.append_output(f"  - {f}", color="#808080")

    def execute_command(self):
        """
        Выполняет команду, введенную в консоли.
        """
        command = self.input.text().strip()
        self.append_output(f"{os.getcwd()}> {command}")
        self.input.clear()

        if self.waiting_for_confirmation:
            if command.lower() in ["y", "n"]:
                self.handle_confirmation(command.lower())
            else:
                self.append_output("Please enter 'y' or 'n'.", color="#FF0000")
            return

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
                self.append_output(command[4:].strip())
            elif command.lower().startswith("spaceworld"):
                self.handle_spaceworld(command[10:].strip())
            else:
                self.append_output(f"Unknown command: {command}", color="#FF0000")

    def handle_confirmation(self, response):
        """
        Обрабатывает ответ пользователя на запрос подтверждения.
        """
        if response == "y":
            # Выполняем команду, которая ожидала подтверждения
            self.append_output(f"Executing command: {self.confirmation_command}", color="#00FF00")
            self.execute_confirmation_command()
        else:
            self.append_output("Command canceled.", color="#FF0000")
        self.waiting_for_confirmation = False
        self.confirmation_command = None

    def execute_confirmation_command(self):
        """
        Выполняет команду, которая ожидала подтверждения.
        """
        if self.confirmation_command.startswith("spaceworld file delete"):
            path = self.confirmation_command.split("~")[1].strip()
            try:
                os.remove(path)
                self.append_output(f"File {path} deleted successfully.", color="#00FF00")
            except Exception as e:
                self.append_output(f"Error deleting file: {e}", color="#FF0000")
        elif self.confirmation_command.startswith("spaceworld dir delete"):
            path = self.confirmation_command.split("~")[1].strip()
            try:
                os.rmdir(path)
                self.append_output(f"Directory {path} deleted successfully.", color="#00FF00")
            except Exception as e:
                self.append_output(f"Error deleting directory: {e}", color="#FF0000")

    def handle_spaceworld(self, command):
        """
        Обрабатывает команды, связанные с SpaceWorld.
        """
        if command == "version":
            self.append_output("SpaceWorld Console v1.0", color="#569CD6")
        elif command.startswith("datatime"):
            self.handle_spaceworld_datatime(command)
        elif command.startswith("file"):
            self.handle_spaceworld_file(command)
        elif command.startswith("dir"):
            self.handle_spaceworld_dir(command)
        elif command == "speedtest":
            speed_thread = threading.Thread(target=self.check_internet_speed)
            speed_thread.start()  # Запускаем поток
        elif command == "ip":
            ips = self.get_all_ip_addresses()
            for ip in ips:
                self.append_output(str(ip), color="#569CD6")
        elif command.startswith("random"):
            command = command.split()[1:]
            start = 0
            if len(command) == 1:
                end = command[0]
            elif len(command) == 2:
                start = command[0]
                end = command[1]
            else:
                self.append_output("Incorrect arguments", color="#FF0000")
                return
            self.append_output(str(random.randint(int(start), int(end))), color="#569CD6")
        else:
            self.append_output(f"Unknown SpaceWorld command: {command}", color="#FF0000")

    def handle_spaceworld_file(self, command):
        command_ = command
        command = command.split()[1]
        if command == "create":
            args = command_[command_.find("~") + 1:]
            if len(args) != 1:
                self.append_output("Incorrect arguments", color="#FF0000")
            else:
                try:
                    open(args, 'w')
                except Exception as error:
                    self.append_output(str(error), color="#FF0000")
                else:
                    self.append_output(f"The {args} file was created in {os.path.join(os.path.join(args[0], args[1]))}", color="#00FF00")
        elif command == "read":
            args = command_[command_.find("~") + 1:].split()
            if len(args) != 1:
                self.append_output("Incorrect arguments", color="#FF0000")
            else:
                try:
                    with open(f"{args[0]}", 'r') as file:
                        self.append_output("".join(file.readlines()), color="#569CD6")
                except Exception as error:
                    self.append_output(str(error), color="#FF0000")
        elif command == "write":
            args = command_[command_.find("~") + 1:].split()
            if len(args) < 2:
                self.append_output("Incorrect arguments", color="#FF0000")
            else:
                try:
                    with open(args[0], 'w') as file:
                        file.write("".join(args[1:]))
                except Exception as error:
                    self.append_output(str(error), color="#FF0000")
        elif command == "delete":
            path = command_[command_.find("~") + 1:].strip()
            self.append_output(f"Are you sure you want to delete {path}? (y/n)", color="#FFA500")
            self.waiting_for_confirmation = True
            self.confirmation_command = f"spaceworld file delete ~{path}"
        else:
            self.append_output(f"Unknown SpaceWorld command: {command}", color="#FF0000")

    def handle_spaceworld_datatime(self, command):
        command = command.split()
        print(command)
        if len(command) > 1:
            command = command[1]
        else:
            self.append_output(f"empty command", color="#FF0000")
            return
        if command == "time":
            self.append_output(str(datetime.datetime.now().time()), color="#569CD6")
        elif command == "datatime":
            self.append_output(str(datetime.datetime.now()), color="#569CD6")
        elif command == "data":
            self.append_output(str(datetime.date.today()), color="#569CD6")
        elif command == "week":
            day_of_week = datetime.datetime.now().strftime("%A")
            self.append_output(str(day_of_week), color="#569CD6")
        elif command == "year":
            now = datetime.datetime.now()
            month = now.strftime("%B")
            year = now.year
            self.append_output(f"Month: {month}", color="#569CD6")
            self.append_output(f"Year: {year}", color="#569CD6")
        else:
            self.append_output(f"Unknown SpaceWorld command: {command}", color="#FF0000")


    def handle_spaceworld_dir(self, command):
        command_ = command
        command = command.split()[1]
        if command == "create":
            args = command_[command_.find("~") + 1:].split()
            if len(args) != 2:
                self.append_output("Incorrect arguments", color="#FF0000")
            else:
                try:
                    os.mkdir(os.path.join(args[0], args[1]))
                except Exception as error:
                    self.append_output(str(error), color="#FF0000")
                else:
                    self.append_output(f"The {args[0]} dir was created in {os.path.join(os.path.join(args[0], args[1]))}", color="#00FF00")
        elif command == "delete":
            path = command_[command_.find("~") + 1:].strip()
            self.append_output(f"Are you sure you want to delete {path}? (y/n)", color="#FFA500")
            self.waiting_for_confirmation = True
            self.confirmation_command = f"spaceworld dir delete ~{path}"
        else:
            self.append_output(f"Unknown SpaceWorld command: {command}", color="#FF0000")

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
    def __init__(self):
        super().__init__()
        self.config = load_config()
        setup_logging(self.config)
        self.init_ui()
        self.apply_theme(self.config["window"]["theme"])
        self.dragging = True  # Флаг для перемещения окна
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