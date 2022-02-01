from hashlib import sha256
from pprint import pformat
from sys import platform
from typing import NamedTuple, Optional

from loguru import logger
from pydantic import BaseModel


class CopyConfCp(BaseModel):
    """
    Вложенная структура файла конфигурации
    """
    exclude_copy: Optional[list[str]] = None
    exclude_delete: Optional[list[str]] = None
    exclude: Optional[list[str]] = None
    replace_name: Optional[dict[str, str]] = dict()
    infloder: str
    outfolder: str


class CopyConf(BaseModel):
    """
    Структура файла конфигурации
    """
    cp: CopyConfCp


# class TypeReplaceName(NamedTuple):
#     real_name: str
#     replace_name: str | None
#
#     def __str__(self):
#         return self.real_name
#
#     def __repr__(self):
#         return f"{self.real_name}:{self.replace_name}"
# class ReplaceName:
#     # @classmethod
#     # def checkReplaceName(cls, _path: str, replace_name_dict: dict[str, str]) -> str | TypeReplaceName:
#     #     if cls.IsReplaceName(_path, replace_name_dict):
#     #         return TypeReplaceName(_path, replace_name_dict[_path])
#     #     return _path
#     @classmethod
#     def getSetPathIfReplaceName(cls, _arr_path: set[str], _arr_replace_name: dict[str, str]) -> set[str]:
#         """
#         Вернуть множество путей с замененным именем
#
#         @param _arr_path: Множеств путей
#         @param _arr_replace_name: Словарь замены
#         @return: Новое множество с учетом замены имении
#         """
#         return {cls.replace_name(_x, _arr_replace_name) for _x in _arr_path}
#
#     @classmethod
#     def replace_name(cls, _path: str, replace_name: dict[str, str]) -> str:
#         if _path in replace_name:
#             res = _path.split(OsSeparator)[:-1]
#             res.append(replace_name[_path])
#             return f'{OsSeparator}'.join(res)
#         return _path


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


OsSeparator: str = "/" if platform == "linux" else "\\"


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
