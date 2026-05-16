"""
@title

@description

"""
import json
import pickle
from pathlib import Path

import frontmatter
import jsonlines
import pandas as pd
import yaml


def _save_text(data, save_path):
    with open(save_path, 'w') as data_file:
        data_file.writelines(data)
    return save_path


def _load_text(save_path):
    with open(save_path, 'r', encoding='utf-8') as data_file:
        data = data_file.read()
    data = data.strip()
    return data


def _save_json(data, save_path, human_readable=False):
    with open(save_path, 'w') as data_file:
        # noinspection PyTypeChecker
        json.dump(data, data_file, indent=2 if human_readable else None)
    return save_path


def _load_json(save_path):
    with open(save_path, 'r') as data_file:
        data = json.load(data_file)
    return data


def _save_jsonl(data, save_path, append=False):
    if not isinstance(data, list):
        data = [data]

    open_flag = 'a' if append else 'w'
    with jsonlines.open(save_path, mode=open_flag) as jl_file:
        jl_file.write_all(data)
    return save_path


def _load_jsonl(save_path):
    with jsonlines.open(save_path) as reader:
        data = [obj for obj in reader]
    return data


def _save_pkl(data, save_path, **kwargs):
    with open(save_path, 'wb') as data_file:
        # noinspection PyTypeChecker
        pickle.dump(data, data_file)
    return save_path


def _load_pkl(save_path):
    with open(save_path, 'rb') as data_file:
        data = pickle.load(data_file)
    return data


def _save_csv(data, save_path, **kwargs):
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    data.to_csv(save_path, index=False)
    return save_path


def _load_csv(save_path):
    return pd.read_csv(save_path)


def _save_markdown(data, save_path, **kwargs):
    raise NotImplementedError


def _load_markdown(save_path):
    data = _load_text(save_path)
    each_prompt = frontmatter.loads(each_txt)
    return md_data


def _save_yaml(data, save_path):
    with open(save_path, 'w') as data_file:
        yaml.dump(data, data_file)
    return save_path


def _load_yaml(save_path):
    with open(save_path, 'r') as data_file:
        data = yaml.safe_load(data_file)
    return data


def determine_datatype(save_path, data_type):
    data_type = data_type or save_path.suffix
    if not data_type.startswith('.'):
        data_type = f'.{data_type}'
    return data_type


def save_data(data, save_path: Path, data_type=None, **kwargs):
    if not save_path.parent.exists():
        save_path.parent.mkdir(parents=True, exist_ok=True)

    # noinspection PyTypeChecker
    func_map = {
        '.txt': _save_text,
        '.md': _save_markdown,
        '.json': _save_json,
        '.pkl': _save_pkl,
        '.jsonl': _save_jsonl,
        '.csv': _save_csv,
        '.yml': _save_yaml,
        '.yaml': _save_yaml,
    }
    data_type = determine_datatype(save_path, data_type)
    save_func = func_map.get(data_type, _save_text)
    result = save_func(data, save_path, **kwargs)
    return result


def load_data(save_path: Path, default_value=None, data_type=None, **kwargs):
    if not save_path.exists():
        return default_value

    func_map = {
        '.txt': _load_text,
        '.md': _load_markdown,
        '.json': _load_json,
        '.pkl': _load_pkl,
        '.jsonl': _load_jsonl,
        '.csv': _load_csv,
        '.yml': _load_yaml,
        '.yaml': _load_yaml,
    }
    data_type = determine_datatype(save_path, data_type)
    load_func = func_map.get(data_type, _load_text)
    data = load_func(save_path, **kwargs)
    if data is None:
        data = default_value
    return data
