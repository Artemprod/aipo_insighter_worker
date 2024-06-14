import os
import pathlib

import yaml
from loguru import logger


def load_settings_from_yaml(file_path: str):
    try:
        with open(file_path, 'r') as file:
            config_data = yaml.safe_load(file)

        return config_data
    except Exception as e:
        logger.info(e)


def resolve_references(config_data):
    # Создаём словарь для хранения реальных ссылок на обменники для consumers
    resolved_config = {"exchangers": {}, "consumers": {}}
    # Обработка exchangers
    if "exchangers" in config_data:
        resolved_config["exchangers"] = config_data["exchangers"]
    # Обработка consumers
    if "consumers" in config_data:
        for consumer_name, consumer_details in config_data["consumers"].items():
            exchanger_path = consumer_details.get("exchanger")
            if exchanger_path:
                # Разбиваем путь (например exchangers.process_exchanger) на части
                path_parts = exchanger_path.split('.')
                resolved_exchanger = config_data
                try:
                    for part in path_parts:
                        resolved_exchanger = resolved_exchanger[part]
                    consumer_details["exchanger"] = resolved_exchanger
                except KeyError as e:
                    raise RuntimeError(f"Path {exchanger_path} is invalid: {e}")
            resolved_config["consumers"][consumer_name] = consumer_details
    return resolved_config


def find_config_file(root_path: str, file_name: str):
    root_dir = pathlib.Path(root_path)
    # Имя файла, который необходимо найти

    # Поиск файла
    file_path = next(root_dir.rglob(file_name), None)
    if file_path:
        logger.info(f"Файл найден: {file_path}")
        return str(file_path)
    else:
        logger.info("Файл не найден")
        return None


def find_project_root(current_file, marker_file_or_folder):
    """
    Функция для поиска корневой папки проекта относительно текущего файла.

    :param current_file: Путь к текущему файлу (__file__)
    :param marker_file_or_folder: Имя файла или папки, который обозначает корень проекта
    :return: Путь к корневой папке проекта
    """
    current_dir = os.path.dirname(current_file)

    while True:
        if marker_file_or_folder in os.listdir(current_dir):
            return current_dir
        new_dir = os.path.dirname(current_dir)
        if new_dir == current_dir:  # Мы достигли корневого каталога файловой системы
            raise FileNotFoundError(f"Маркерный файл или папка '{marker_file_or_folder}' не найдены в пути.")
        current_dir = new_dir


current_file = __file__
marker_file_or_folder = "Readme.md"  # Укажите имя файла или папки, которая обозначает корень вашего проекта
project_root = find_project_root(current_file, marker_file_or_folder)
path = find_config_file(project_root, "rabitmq_workers_config.yml")
if path is None:
    raise FileNotFoundError("Configuration file not found")

settings = load_settings_from_yaml(path)
if settings is None:
    raise ValueError("Failed to load configuration")

resolved_settings = resolve_references(settings)
