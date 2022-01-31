from hashlib import sha256
from pprint import pformat
from sys import platform
from typing import NamedTuple

from loguru import logger
from pydantic import BaseModel


class CopyConfCp(BaseModel):
    """
    Вложенная структура файла конфигурации
    """
    exclude_copy: list[str] = ['']
    exclude_delete: list[str] = ['']
    infloder: str
    outfolder: str


class CopyConf(BaseModel):
    """
    Структура файла конфигурации
    """
    cp: CopyConfCp


class DiffDir(NamedTuple):
    """
    Объект для хранения разницы меду директориями
    """
    infloder: str
    outfolder: str
    not_exist_arr_file: set[str]
    not_exist_arr_folder: set[str]
    diff_data_arr_file: set[str]
    file_intruder: set[str]
    folder_intruder: set[str]

    def log(self):
        logger.info(f"NotFile:\n{pformat(self.not_exist_arr_file)}")
        logger.info(f"NotFolder:\n{pformat(self.not_exist_arr_folder)}")
        logger.info(f"DiffHashFile:\n{pformat(self.diff_data_arr_file)}")
        logger.info(f"FileIntruder:\n{pformat(self.file_intruder)}")
        logger.info(f"FolderIntruder:\n{pformat(self.folder_intruder)}")


getOsSeparator: str = "/" if platform == "linux" else "\\"


def sha256sum(path_file):
    """
    Получить хеш сумму файла
    @param path_file: Путь к файлу
    """
    h = sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(path_file, 'rb', buffering=0) as f:
        for n in iter(lambda: f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()
