# Бот для записи в салон красоты

### Описание 
Бот для записи в салон красоты

## 1. Установка:
### Клонировать репозиторий: 
```
git clone https://github.com/alexdiptan/dvmn_project_beauty_saloon_bot.git
```
### Перейти в полученную директорию:
```
cd dvmn_project_beauty_saloon_bot
```
### Создать виртуальное окружение:
```
python3 -m venv my_env
```
### Активировать виртуальное окружение:
```
source my_env/bin/activate
```
### Установить зависимости:
```
pip install -r requirements.txt
```
### Переименовать файл
Переменные окружения, скрипт берет из файла `.env`. Шаблон файла .env, называется .env_template.
Нужно переименовать файл `.env_template -> .env`.
В полученном файле нужно заполнить 2 переменные окружения: `TG_BOT_TOKEN` и `PAYMENTS_PROVIDER_TOKEN`.

## 2. Запуск скрипта
### Бот запускается командой:
```
python3 main.py
```
