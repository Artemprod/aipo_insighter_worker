import pathlib

import yaml


def load_settings_from_yaml(file_path: str):
    with open(file_path, 'r') as file:
        config_data = yaml.safe_load(file)

    return config_data


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

def find_config_file(root_path:str, file_name:str):
    root_dir = pathlib.Path(root_path)
    # Имя файла, который необходимо найти

    # Поиск файла
    file_path = next(root_dir.rglob(file_name), None)
    if file_path:
        print(f"Файл найден: {file_path}")
        return str(file_path)
    else:
        print("Файл не найден")
        return None

path = find_config_file("..", "rabitmq_workers_config.yml")
settings = load_settings_from_yaml(path)
resolved_settings = resolve_references(settings)



