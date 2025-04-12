import datetime
import json
import random
import re
import socket
import sys
import threading

import psutil
import speedtest
from PySide6.QtCore import QEvent, QProcess
from PySide6.QtGui import QColor, QTextCharFormat, QSyntaxHighlighter, QFont
from PySide6.QtWidgets import (
    QWidget, QTextEdit, QApplication
)

from SettingsDialog import *


class ConsoleHighlighter(QSyntaxHighlighter):
    def __init__(self, document, theme_data):
        super().__init__(document)
        self.theme_data = theme_data

        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor(self.theme_data["syntax_highlighting"]["keyword_color"]))
        self.keyword_format.setFontWeight(QFont.Bold)
        self.keywords = ["help", "clear", "echo", "spaceworld", "exit"]

        self.subcommand_format = QTextCharFormat()
        self.subcommand_format.setForeground(QColor(self.theme_data["syntax_highlighting"]["subcommand_color"]))
        self.subcommands = ["file", "datatime", "dir"]

        self.argument_format = QTextCharFormat()
        self.argument_format.setForeground(QColor(self.theme_data["syntax_highlighting"]["argument_color"]))
        self.arguments = ["create", "read", "write", "delete", "time", "date", "week", "year"]

        self.path_format = QTextCharFormat()
        self.path_format.setForeground(QColor(self.theme_data["syntax_highlighting"]["path_color"]))

        self.json_key_format = QTextCharFormat()
        self.json_key_format.setForeground(QColor("#569CD6"))
        self.json_key_format.setFontWeight(QFont.Bold)

        self.json_string_format = QTextCharFormat()
        self.json_string_format.setForeground(QColor("#CE9178"))

        self.json_number_format = QTextCharFormat()
        self.json_number_format.setForeground(QColor("#B5CEA8"))

        self.json_boolean_format = QTextCharFormat()
        self.json_boolean_format.setForeground(QColor("#569CD6"))

        self.json_null_format = QTextCharFormat()
        self.json_null_format.setForeground(QColor("#569CD6"))

    def highlightBlock(self, text):
        """
        Подсвечивает ключевые слова, подкоманды, аргументы, пути и JSON.
        """
        for keyword in self.keywords:
            for match in re.finditer(rf"\b{keyword}\b", text, re.IGNORECASE):
                self.setFormat(match.start(), match.end() - match.start(), self.keyword_format)

        for subcommand in self.subcommands:
            for match in re.finditer(rf"\b{subcommand}\b", text, re.IGNORECASE):
                self.setFormat(match.start(), match.end() - match.start(), self.subcommand_format)

        for argument in self.arguments:
            for match in re.finditer(rf"\b{argument}\b", text, re.IGNORECASE):
                self.setFormat(match.start(), match.end() - match.start(), self.argument_format)

        for match in re.finditer(r"~[^\s]+", text):
            self.setFormat(match.start(), match.end() - match.start(), self.path_format)

        self.highlight_json(text)

    def highlight_json(self, text):
        """
        Подсвечивает JSON-структуры.
        """
        for match in re.finditer(r'"([^"]+)":', text):
            self.setFormat(match.start(), match.end() - match.start(), self.json_key_format)

        for match in re.finditer(r'"[^"]*"', text):
            self.setFormat(match.start(), match.end() - match.start(), self.json_string_format)

        for match in re.finditer(r'\b\d+\b', text):
            self.setFormat(match.start(), match.end() - match.start(), self.json_number_format)

        for match in re.finditer(r'\b(true|false)\b', text):
            self.setFormat(match.start(), match.end() - match.start(), self.json_boolean_format)

        for match in re.finditer(r'\bnull\b', text):
            self.setFormat(match.start(), match.end() - match.start(), self.json_null_format)

class CustomConsole(QWidget):
    def __init__(self, config, main, theme_data):
        super().__init__()
        self.config = config
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(10)
        self.MainWindow = main

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setLineWrapMode(QTextEdit.NoWrap)

        self.input = QLineEdit()
        self.input.returnPressed.connect(self.execute_command)
        self.input.installEventFilter(self)

        self.layout.addWidget(self.output)
        self.layout.addWidget(self.input)
        self.art = r""" ____                        
/ ___| _ __   __ _  ___ ___  
\___ \| '_ \ / _` |/ __/ _ \ 
 ___) | |_) | (_| | (_|  __/ 
|____/| .__/ \__,_|\___\___| 
\ \   |_|/ /__  _ __| | __| |
 \ \ /\ / / _ \| '__| |/ _` |
  \ V  V / (_) | |  | | (_| |
   \_/\_/ \___/|_|  |_|\__,_|"""
        self.highlighter = ConsoleHighlighter(self.output.document(), theme_data)
        self.output.append("SpaceWorld [Version beta 1.0.0]")
        self.output.append("(c) Binobinos official. Все права защищены.")
        self.output.append(self.art)
        self.command_history = config.get('command_history', [])
        self.history_index = -1

        self.available_commands = {
            "clear": {},
            "echo": {},
            "exit": {},
            "restart": {},
            "settings": {},
            "theme": dict(self.config["themes"]),
            "resize": {},
            "maximize": {},
            "minimize": {},
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
                    "sorted": {}
                },
                "ip": {},
                "speedtest": {},
                "version": {},
                "start": {},
                "random": {}
            },
        }

        self.waiting_for_confirmation = False
        self.confirmation_command = None

    def handle_spaceworld(self, command):
        """
        Обрабатывает команды, связанные с SpaceWorld.
        """
        command = command.split()
        if len(command) > 1:
            command = " ".join(command[1:])
            print(command)
        else:
            self.append_output(f"Unknown SpaceWorld command: {command}", color="#FF0000")
            return
        if command.strip().lower() == "version":
            self.append_output("SpaceWorld Console beta 1.0.0", color="#569CD6")
        elif command.startswith("datatime"):
            self.handle_spaceworld_datatime(command)
        elif command.startswith("file"):
            self.handle_spaceworld_file(command)
        elif command.startswith("dir"):
            self.handle_spaceworld_dir(command)
        elif command == "speedtest":
            speed_thread = threading.Thread(target=self.check_internet_speed)
            speed_thread.start()
        elif command == "ip":
            ips = self.get_all_ip_addresses()
            for ip in ips:
                self.append_output(str(ip), color="#5cde2c")
        elif command.startswith("start"):
            commands = command.split()[1:]
            for file in commands:
                os.startfile(file)
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

    def append_output(self, text, color=None, font=None):
        """
        Выводит текст в консоль с возможностью задания цвета и шрифта.
        """
        if color:
            self.output.setTextColor(QColor(color))
        if font:
            self.output.setCurrentFont(font)
        self.output.append(text)
        self.output.setTextColor(QColor(self.config["themes"][self.config["window"]["theme"]]["text_color"]))
        self.output.setCurrentFont(QFont("Consolas", 12))

    def remove_last_line(self):
        """Удаляет последнюю строку в QTextEdit."""
        cursor = self.output.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.select(cursor.SelectionType.BlockUnderCursor)
        cursor.removeSelectedText()

    def check_internet_speed(self):
        st = speedtest.Speedtest()

        self.append_output("Выбор лучшего сервера...", color="#4EC9B0")
        st.get_best_server()
        self.append_output("Проверка скорости загрузки...", color="#4EC9B0")
        download_speed = st.download() / 1000000

        self.append_output("Проверка скорости выгрузки...", color="#4EC9B0")
        upload_speed = st.upload() / 1000000

        ping = st.results.ping
        self.append_output("\nРезультаты теста скорости:", color="#4EC9B0")
        self.append_output(f"Скорость загрузки: {download_speed:.2f} Мбит/с", color="#4EC9B0")
        self.append_output(f"Скорость выгрузки: {upload_speed:.2f} Мбит/с", color="#4EC9B0")
        self.append_output(f"Пинг: {ping:.2f} мс", color="#4EC9B0")

    def eventFilter(self, source, event):
        """
        Обрабатывает события клавиш для навигации по истории команд и автодополнения.
        """
        if event.type() == QEvent.Type.KeyPress and source == self.input:
            if event.key() == Qt.Key_Up:
                self.navigate_history(-1)
                return True
            elif event.key() == Qt.Key_Down:
                self.navigate_history(1)
                return True
            elif event.key() == Qt.Key_Tab:
                self.auto_complete()
                return True
        return super().eventFilter(source, event)

    def navigate_history(self, direction):
        """
        Навигация по истории команд.
        """
        if not self.command_history:
            return

        self.history_index += direction

        if self.history_index < 0:
            self.history_index = 0
        elif self.history_index >= len(self.command_history):
            self.history_index = len(self.command_history) - 1

        self.input.setText(self.command_history[self.history_index])

    def auto_complete(self):
        """
        Автодополнение команд и аргументов.
        """
        current_text = self.input.text().strip()
        if not current_text:
            return
        parts = current_text.split()
        if not parts:
            return

        current_level = self.available_commands

        for i, part in enumerate(parts):
            part = part.lower()
            if part in current_level:
                current_level = current_level[part]
            else:
                matching_commands = [cmd for cmd in current_level.keys() if cmd.startswith(part)]
                if matching_commands:
                    if len(matching_commands) == 1:
                        parts[i] = matching_commands[0]
                        self.input.setText(" ".join(parts) + " ")
                    else:
                        self.append_output("Доступные команды:", color="#569CD6")
                        for cmd in matching_commands:
                            self.append_output(f"  - {cmd}", color="#569CD6")
                    return

        if current_level:
            subcommands = list(current_level.keys())
            if len(subcommands) == 1:
                self.input.setText(" ".join(parts + [subcommands[0]]) + " ")
            else:
                self.append_output("Доступные подкоманды:", color="#4EC9B0")
                for sub in subcommands:
                    self.append_output(f"  - {sub}", color="#4EC9B0")

        if parts[-1].startswith("~"):
            path = parts[-1][1:]
            dir_path = os.path.dirname(path)
            base_name = os.path.basename(path)
            if os.path.exists(dir_path):
                matching_files = [f for f in os.listdir(dir_path) if f.startswith(base_name)]
                if matching_files:
                    if len(matching_files) == 1:
                        new_path = os.path.join(dir_path, matching_files[0])
                        parts[-1] = "~" + new_path
                        self.input.setText(" ".join(parts) + " ")
                    else:
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

        if command:
            self.command_history.append(command)
            self.history_index = len(self.command_history)
            self.config["command_history"].append(command)
            if command.lower() == "clear":
                self.output.clear()
                self.output.setCurrentFont(QFont("Consolas", 12))  # Явно устанавливаем шрифт
                self.output.append("SpaceWorld [Version 1.0.0]")
                self.output.append("(c) Binobinos official. Все права защищены.")
                self.output.append(self.art)
            elif command == "help":
                text = """
|===============================================================|
|clear - Очищает консоль                                        |
|echo - повторяет сообщение                                     |
|exit - Выход из программы                                      |
|restart - перезапуск приложения                                |
|settings - Открывает настйроки                                 |
|theme - Меняет тему на указанную                               |
|resize - Изменяет размер окна                                  |
|maximize - Открывает во весь экран                             |
|minimize - Сворачивает приложение                              |
|spaceworld - Категория команд SpaceWorld                       |
|spaceworld file - подкоманды файлов                            |
|spaceworld file create - Создает файл                          |
|spaceworld file read - Читает и выводит содержимое файла       |
|spaceworld file write - Записывает в файл                      |
|spaceworld file delete - Удаляет файл                          |
|spaceworld datatime - подкоманды времени                       |
|spaceworld datatime time - Выводит текущие время               |
|spaceworld datatime data - Выводит текущию дату                |
|spaceworld datatime week - Выводит текущию неделю и день нелели|
|spaceworld datatime year - Выводит текущий год и месяц         |
|spaceworld dir - подкоманды директорий                         |
|spaceworld dir create - Создает директорию                     |
|spaceworld dir delete - Удаляет деректорию                     |
|spaceworld ip - Выводит все ip адреса                          |
|spaceworld speedtest - Запускает тестирование интернета        |
|spaceworld version - Выводит текущию версию программы          |
|spaceworld start - Запускает все файлы казанные через пробел   |
|spaceworld random - Генерирует число от a до b                 |
|===============================================================|
""".strip()

                self.append_output(text)
            elif command.lower().startswith("echo"):
                self.append_output(command[4:].strip())
            elif command.lower() == "exit":
                self.MainWindow.close()
            elif command.lower() == "restart":
                self.restart_application()
            elif command == "config":
                config_str = json.dumps(self.config, indent=4)
                self.output.append(config_str)
            elif command.lower() == "settings":
                self.MainWindow.show_settings()
            elif command.lower().startswith("theme"):
                self.change_theme(command)
                self.output.lower()
            elif command.lower().startswith("resize"):
                self.resize_window(command)
            elif command.lower().startswith("spaceworld"):
                self.handle_spaceworld(command)
            elif command.lower() == "maximize":
                self.MainWindow.showMaximized()
            elif command.lower() == "minimize":
                self.MainWindow.showMinimized()
            else:
                self.append_output(f"Unknown command1: {command}", color="#FF0000")

    def handle_confirmation(self, response):
        """
        Обрабатывает ответ пользователя на запрос подтверждения.
        """
        if response == "y":
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

    @staticmethod
    def get_all_ip_addresses():
        ip_addresses = []
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ip_addresses.append(addr.address)
                elif addr.family == socket.AF_INET6:
                    ip_addresses.append(addr.address)

        return ip_addresses

    def restart_application(self):
        """
        Перезапускает приложение.
        """
        self.append_output("Restarting application...", color="#00FF00")
        QApplication.quit()  # Закрываем текущее приложение
        QProcess.startDetached(sys.executable, sys.argv)  # Запускаем новое

    def change_theme(self, command):
        """
        Изменяет тему приложения.
        """
        parts = command.split()
        if len(parts) != 2:
            self.append_output("Usage: theme [dark/light/blue]", color="#FF0000")
            return

        theme = parts[1].lower()
        self.MainWindow.apply_theme(theme)
        self.append_output(f"Theme changed to {theme}.", color="#00FF00")

    def resize_window(self, command):
        """
        Изменяет размер окна.
        """
        parts = command.split()
        if len(parts) != 3:
            self.append_output("Usage: resize [width] [height]", color="#FF0000")
            return

        try:
            width = int(parts[1])
            height = int(parts[2])
            self.MainWindow.resize(width, height)
            self.append_output(f"Window resized to {width}x{height}.", color="#00FF00")
        except ValueError:
            self.append_output("Invalid width or height. Please enter numbers.", color="#FF0000")

    def handle_spaceworld_file(self, command):
        command_ = command
        command = command.split()[1]
        if command == "create":
            args = command_[command_.find("~") + 1:]
            try:
                open(os.path.join(args), 'w')
            except Exception as error:
                self.append_output(str(error), color="#FF0000")
            else:
                self.append_output(f"The {args} file was created in {os.path.join(os.path.join(args[0], args[1]))}",
                                   color="#00FF00")
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
                    self.append_output(f"The {args[0]} dir was created in "
                                       f"{os.path.join(os.path.join(args[0], args[1]))}", color="#00FF00")
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
