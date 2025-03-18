# 🚀 SpaceWorld

**Программа для управления утилитами с кастомной консолью, минималистичным интерфейсом и расширяемой экосистемой.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-green)](https://python.org)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

<div align="center">
  <img src="https://via.placeholder.com/800x400.png?text=SpaceWorld+Demo" alt="Демо">
</div>

## 🌟 Особенности
- **Кастомная консоль** с подсветкой синтаксиса и темами
- **Утилиты на любой случай**: сортировка файлов, автокликер, очистка системы
- **Формат CBCJ** — безопасный конфиг с шифрованием и бинарным режимом
- **Профили настроек** для быстрого доступа к частым задачам
- **Модульность** — добавляйте свои скрипты через API
- **Кроссплатформенность**: Windows, Linux, macOS

## 🛠 Установка
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/yourusername/SpaceWorld.git
   cd SpaceWorld
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Запустите программу:
   ```bash
   python src/cli/main.py
   ```

## 🖥 Использование
### Примеры команд
```bash
# Сортировка файлов по дате
spaceworld sort --by date --dir ~/downloads

# Создание профиля
spaceworld sort --profile create work

# Просмотр информации о профиле
spaceworld sort --profile info work
```

### GUI
Запустите графический интерфейс:
```bash
python src/gui/main.py
```

## 📁 Формат CBCJ
Конфиги хранятся в формате `.cbcj` с поддержкой:
- Шифрования через AES-256
- Бинарного/текстового режима
- Автоматической конвертации в JSON

**Пример файла:**
```cbcj
<cbcj 1.0>
<cry-F>
dict({
  "rules": list({
    dict({ "action": str(|sort|), "type": str(|date|) })
  })
})
```

## 📃 Документация
Полное руководство доступно в [Wiki](https://github.com/yourusername/SpaceWorld/wiki).

## 🤝 Участие в проекте
1. Форкните репозиторий
2. Создайте ветку для своей фичи (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Запушьте ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📜 Лицензия
Распространяется под лицензией MIT. Подробнее см. [LICENSE](LICENSE).
