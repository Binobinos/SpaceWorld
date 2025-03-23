import datetime
import os
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
    QWidget, QTextEdit, QLineEdit, QApplication
)

from SettingsDialog import *


class ConsoleHighlighter(QSyntaxHighlighter):
    def __init__(self, document, theme_data):
        super().__init__(document)
        self.theme_data = theme_data

        # Основные команды
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor(self.theme_data["syntax_highlighting"]["keyword_color"]))
        self.keyword_format.setFontWeight(QFont.Bold)
        self.keywords = ["help", "clear", "echo", "spaceworld", "exit"]

        # Подкоманды
        self.subcommand_format = QTextCharFormat()
        self.subcommand_format.setForeground(QColor(self.theme_data["syntax_highlighting"]["subcommand_color"]))
        self.subcommands = ["file", "datatime", "dir"]

        # Аргументы
        self.argument_format = QTextCharFormat()
        self.argument_format.setForeground(QColor(self.theme_data["syntax_highlighting"]["argument_color"]))
        self.arguments = ["create", "read", "write", "delete", "time", "date", "week", "year"]

        # Пути и имена файлов
        self.path_format = QTextCharFormat()
        self.path_format.setForeground(QColor(self.theme_data["syntax_highlighting"]["path_color"]))

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
    def __init__(self, config, main, theme_data):
        super().__init__()
        self.config = config
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(10)
        self.MainWindow = main

        # Поле вывода
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setLineWrapMode(QTextEdit.NoWrap)

        # Поле ввода
        self.input = QLineEdit()
        self.input.returnPressed.connect(self.execute_command)
        self.input.installEventFilter(self)

        self.layout.addWidget(self.output)
        self.layout.addWidget(self.input)

        self.highlighter = ConsoleHighlighter(self.output.document(), theme_data)
        self.output.append("SpaceWorld [Version 1.0.0]")
        self.output.append("(c) Binobinos official. Все права защищены.")

        # История команд
        self.command_history = config.get('command_history', [])
        self.history_index = -1

        # Доступные команды
        self.available_commands = {
            "clear": {},
            "echo": {},
            "exit": {},
            "restart": {},
            "settings": {},
            "theme": {},
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
                },
                "ip": {},
                "speedtest": {}
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

    def check_internet_speed(self):
        st = speedtest.Speedtest()

        print("Выбор лучшего сервера...")
        st.get_best_server()

        print("Проверка скорости загрузки...")
        download_speed = st.download() / 1_000_000  # Переводим в Мбит/с

        print("Проверка скорости выгрузки...")
        upload_speed = st.upload() / 1_000_000  # Переводим в Мбит/с

        ping = st.results.ping

        print("\nРезультаты теста скорости:")
        print(f"Скорость загрузки: {download_speed:.2f} Мбит/с")
        print(f"Скорость выгрузки: {upload_speed:.2f} Мбит/с")
        print(f"Пинг: {ping:.2f} мс")

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
            elif command.lower().startswith("echo"):
                self.append_output(command[4:].strip())
            elif command.lower() == "exit":
                self.MainWindow.close()  # Завершение работы приложения
            elif command.lower() == "restart":
                self.restart_application()  # Перезапуск приложения
            elif command.lower() == "settings":
                self.MainWindow.show_settings()  # Открытие настроек
            elif command.lower().startswith("theme"):
                self.change_theme(command)  # Изменение темы
            elif command.lower().startswith("resize"):
                self.resize_window(command)  # Изменение размера окна
            elif command.lower() == "maximize":
                self.MainWindow.showMaximized()  # Разворачивание окна
            elif command.lower() == "minimize":
                self.MainWindow.showMinimized()  # Сворачивание окна
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

    @staticmethod
    def get_all_ip_addresses():
        ip_addresses = []
        # Получаем информацию о всех сетевых интерфейсах
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:  # Проверяем, что это IPv4
                    ip_addresses.append(addr.address)
                elif addr.family == socket.AF_INET6:  # Проверяем, что это IPv6
                    ip_addresses.append(addr.address)

        return ip_addresses

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
                self.append_output(str(ip), color="#5cde2c")
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
            if len(args) != 1:
                self.append_output("Incorrect arguments", color="#FF0000")
            else:
                try:
                    open(args, 'w')
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
