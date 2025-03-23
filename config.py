import json
def load_config():
    """
    Загружает конфигурацию из файла config.json.
    Если файл отсутствует, используется конфигурация по умолчанию.
    """
    try:
        with open("config.json", "r") as file:
            config = json.load(file)
            return config
    except FileNotFoundError:
        return {
            "window": {
                "width": 1000,
                "height": 60,
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
