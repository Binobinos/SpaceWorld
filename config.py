import json
def load_config():
    """
    Загружает конфигурацию из файла config.json.
    Если файл отсутствует, используется конфигурация по умолчанию.
    """
    try:
        with open("config/config.json", "r") as file:
            config = json.load(file)
            return config
    except FileNotFoundError:
        return {
            "window": {
                "width": 800,
                "height": 600,
                "theme": "ocean",
                "border_radius": "15px",
                "default_icon": "app_icon.png",
                "title": "Space World",
                "shadow": {
                    "blur_radius": 15,
                    "color": [
                        0,
                        0,
                        0,
                        150
                    ],
                    "offset": [
                        0,
                        0
                    ]
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
                    "border_color": "#555",
                    "syntax_highlighting": {
                        "keyword_color": "#569CD6",
                        "subcommand_color": "#4EC9B0",
                        "argument_color": "#CE9178",
                        "path_color": "#808080"
                    }
                },
                "light": {
                    "main_bg": "#f0f0f0",
                    "title_bg": "#d0d0d0",
                    "text_color": "#000000",
                    "button_bg": "#ddd",
                    "console_bg": "#ffffff",
                    "input_bg": "#f0f0f0",
                    "border_color": "#ccc",
                    "syntax_highlighting": {
                        "keyword_color": "#0000FF",
                        "subcommand_color": "#008000",
                        "argument_color": "#FF4500",
                        "path_color": "#808080"
                    }
                },
                "blue": {
                    "main_bg": "#001f3f",
                    "title_bg": "#003366",
                    "text_color": "#ffffff",
                    "button_bg": "#004080",
                    "console_bg": "#002b4d",
                    "input_bg": "#003366",
                    "border_color": "#0059b3",
                    "syntax_highlighting": {
                        "keyword_color": "#569CD6",
                        "subcommand_color": "#4EC9B0",
                        "argument_color": "#CE9178",
                        "path_color": "#808080"
                    }
                },
                "cyberpunk": {
                    "main_bg": "#0d0d1a",
                    "title_bg": "#1a1a33",
                    "text_color": "#00ffcc",
                    "button_bg": "#6600cc",
                    "console_bg": "#1a1a33",
                    "input_bg": "#0d0d1a",
                    "border_color": "#00ffcc",
                    "syntax_highlighting": {
                        "keyword_color": "#00ffcc",
                        "subcommand_color": "#ff00ff",
                        "argument_color": "#ff9966",
                        "path_color": "#808080"
                    }
                },
                "ocean": {
                    "main_bg": "#001f3f",
                    "title_bg": "#003366",
                    "text_color": "#ffffff",
                    "button_bg": "#004080",
                    "console_bg": "#002b4d",
                    "input_bg": "#003366",
                    "border_color": "#0059b3",
                    "syntax_highlighting": {
                        "keyword_color": "#569CD6",
                        "subcommand_color": "#4EC9B0",
                        "argument_color": "#CE9178",
                        "path_color": "#808080"
                    }
                },
                "forest": {
                    "main_bg": "#1a2a1a",
                    "title_bg": "#0d1a0d",
                    "text_color": "#ccffcc",
                    "button_bg": "#336633",
                    "console_bg": "#0d1a0d",
                    "input_bg": "#1a2a1a",
                    "border_color": "#669966",
                    "syntax_highlighting": {
                        "keyword_color": "#00ff00",
                        "subcommand_color": "#00cc00",
                        "argument_color": "#ff9966",
                        "path_color": "#808080"
                    }
                },
                "retro": {
                    "main_bg": "#000000",
                    "title_bg": "#333333",
                    "text_color": "#00ff00",
                    "button_bg": "#666666",
                    "console_bg": "#333333",
                    "input_bg": "#000000",
                    "border_color": "#00ff00",
                    "syntax_highlighting": {
                        "keyword_color": "#00ff00",
                        "subcommand_color": "#00cc00",
                        "argument_color": "#ff9966",
                        "path_color": "#808080"
                    }
                },
                "monochrome": {
                    "main_bg": "#000000",
                    "title_bg": "#333333",
                    "text_color": "#ffffff",
                    "button_bg": "#666666",
                    "console_bg": "#333333",
                    "input_bg": "#000000",
                    "border_color": "#ffffff",
                    "syntax_highlighting": {
                        "keyword_color": "#ffffff",
                        "subcommand_color": "#cccccc",
                        "argument_color": "#999999",
                        "path_color": "#808080"
                    }
                },
                "purple": {
                    "main_bg": "#1a0d33",
                    "title_bg": "#330d66",
                    "text_color": "#cc99ff",
                    "button_bg": "#6600cc",
                    "console_bg": "#330d66",
                    "input_bg": "#1a0d33",
                    "border_color": "#cc99ff",
                    "syntax_highlighting": {
                        "keyword_color": "#cc99ff",
                        "subcommand_color": "#9966cc",
                        "argument_color": "#ff9966",
                        "path_color": "#808080"
                    }
                },
                "fire": {
                    "main_bg": "#331a0d",
                    "title_bg": "#66330d",
                    "text_color": "#ff9966",
                    "button_bg": "#cc6600",
                    "console_bg": "#66330d",
                    "input_bg": "#331a0d",
                    "border_color": "#ff9966",
                    "syntax_highlighting": {
                        "keyword_color": "#ff4500",
                        "subcommand_color": "#ff9966",
                        "argument_color": "#ffcc00",
                        "path_color": "#808080"
                    }
                },
                "gold": {
                    "main_bg": "#332a1a",
                    "title_bg": "#665533",
                    "text_color": "#ffcc00",
                    "button_bg": "#cc9900",
                    "console_bg": "#665533",
                    "input_bg": "#332a1a",
                    "border_color": "#ffcc00",
                    "syntax_highlighting": {
                        "keyword_color": "#ffcc00",
                        "subcommand_color": "#cc9900",
                        "argument_color": "#ff9966",
                        "path_color": "#808080"
                    }
                },
                "neon": {
                    "main_bg": "#0a0a0a",
                    "title_bg": "#1a1a1a",
                    "text_color": "#00ffcc",
                    "button_bg": "#6600cc",
                    "console_bg": "#1a1a1a",
                    "input_bg": "#0a0a0a",
                    "border_color": "#00ffcc",
                    "syntax_highlighting": {
                        "keyword_color": "#00ffcc",
                        "subcommand_color": "#ff00ff",
                        "argument_color": "#ff9966",
                        "path_color": "#808080"
                    }
                },
                "gradient": {
                    "main_bg": "#1e1e2f",
                    "title_bg": "#2d2d4f",
                    "text_color": "#ffffff",
                    "button_bg": "#4a4a8f",
                    "console_bg": "#2d2d4f",
                    "input_bg": "#1e1e2f",
                    "border_color": "#4a4a8f",
                    "syntax_highlighting": {
                        "keyword_color": "#ff7f50",
                        "subcommand_color": "#6a5acd",
                        "argument_color": "#ffd700",
                        "path_color": "#808080"
                    }
                },
                "pastel": {
                    "main_bg": "#f4f4f4",
                    "title_bg": "#e0e0e0",
                    "text_color": "#333333",
                    "button_bg": "#d1c4e9",
                    "console_bg": "#e0e0e0",
                    "input_bg": "#f4f4f4",
                    "border_color": "#d1c4e9",
                    "syntax_highlighting": {
                        "keyword_color": "#9575cd",
                        "subcommand_color": "#64b5f6",
                        "argument_color": "#81c784",
                        "path_color": "#808080"
                    }
                },
                "hitech": {
                    "main_bg": "#000000",
                    "title_bg": "#1a1a1a",
                    "text_color": "#00ff00",
                    "button_bg": "#333333",
                    "console_bg": "#1a1a1a",
                    "input_bg": "#000000",
                    "border_color": "#00ff00",
                    "syntax_highlighting": {
                        "keyword_color": "#00ff00",
                        "subcommand_color": "#00cc00",
                        "argument_color": "#ff9966",
                        "path_color": "#808080"
                    }
                },
                "sunset": {
                    "main_bg": "#2c3e50",
                    "title_bg": "#34495e",
                    "text_color": "#ecf0f1",
                    "button_bg": "#e67e22",
                    "console_bg": "#34495e",
                    "input_bg": "#2c3e50",
                    "border_color": "#e67e22",
                    "syntax_highlighting": {
                        "keyword_color": "#e67e22",
                        "subcommand_color": "#3498db",
                        "argument_color": "#2ecc71",
                        "path_color": "#808080"
                    }
                },
                "midnight": {
                    "main_bg": "#0a0a1a",
                    "title_bg": "#1a1a33",
                    "text_color": "#ffffff",
                    "button_bg": "#333366",
                    "console_bg": "#1a1a33",
                    "input_bg": "#0a0a1a",
                    "border_color": "#333366",
                    "syntax_highlighting": {
                        "keyword_color": "#569CD6",
                        "subcommand_color": "#4EC9B0",
                        "argument_color": "#CE9178",
                        "path_color": "#808080"
                    }
                }
            },
            "utilities": [
                {
                    "name": "Sorted",
                    "icon": "photo1.png"
                },
                {
                    "name": "Utility 2",
                    "icon": "C:\\Users\\Misha\\Downloads\\all files .png\\IMG-20220623-WA0001 yy(1).png"
                },
                {
                    "name": "Utility 3",
                    "icon": "icon3.png"
                }
            ],
            "logging": {
                "level": "INFO",
                "file": "app.log",
                "format": "%(asctime)s - %(levelname)s - %(message)s"
            },
            "command_history": [
                "settings",
                "theme ligth",
                "theme light",
                "theme dark",
                "theme dark",
                "theme cyberpunk",
                "theme cyberpunk1",
                "theme fire",
                "theme neon",
                "theme cyberpunk",
                "theme retro",
                "theme sunset",
                "theme midnight",
                "theme sunset",
                "theme",
                "theme retro"
            ]
        }


def save_config(config):
    """
    Сохраняет конфигурацию в файл config.json.
    """
    with open("config/config.json", "w") as file:
        json.dump(config, file, indent=4)
