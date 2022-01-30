from collections import deque
from os import path, listdir, makedirs
from pprint import pformat
from re import match
from shutil import copyfile
from typing import NamedTuple

from loguru import logger
from mg_file import YamlFile
from pydantic.error_wrappers import ValidationError

from helpful import CopyConf, sha256sum


class DiffDir(NamedTuple):
    infloder: str
    outfolder: str
    not_exist_arr_file: set[str]
    not_exist_arr_folder: set[str]
    diff_data_arr_file: set[str]
    file_intruder: set[str]
    folder_intruder: set[str]

    def log(self):
        logger.warning(f"NotFile:\n{pformat(self.not_exist_arr_file)}")
        logger.warning(f"NotFolder:\n{pformat(self.not_exist_arr_folder)}")
        logger.warning(f"DiffHashFile:\n{pformat(self.diff_data_arr_file)}")
        logger.warning(f"FileIntruder:\n{pformat(self.file_intruder)}")
        logger.warning(f"FolderIntruder:\n{pformat(self.folder_intruder)}")


class BaseSmartDir:
    def __init__(self, path_conf: str):
        """
        Валидация файла конфигураций
        """
        self._file = YamlFile(path_conf)
        try:
            self.conf = CopyConf.parse_obj(self._file.readFile())
            self.infloder: str = self.conf.cp.infloder
            self.outfolder: str = self.conf.cp.outfolder
            self.exclude: set = set(self.conf.cp.exclude)
        except ValidationError as e:
            print(e.json())

    def getDiff(self) -> DiffDir:
        """
        Получить различия между дирекцией А и Б

        А - директория откуда брать данные
        Б - директория куда копировать данные
        """
        # Получаем пути к файлам и папкам, которые не исключены в конфигурациях
        arr_file, arr_folder = self._excludeFolderAndFile(self.exclude,
                                                          **self._getAllFileAndFolderFromPath(self.infloder))
        logger.info(f"Tracking:\n{pformat({'arr_file': arr_file, 'arr_folder': arr_folder}, compact=True, width=240)}")
        # Получим разницу между А и Б директориями
        objDiffDir = self._dirDiff(
            self.outfolder,
            self.infloder,
            arr_file,
            arr_folder)
        return objDiffDir

    @staticmethod
    def _getAllFileAndFolderFromPath(folder: str) -> dict[str, set[str] | str]:
        """
        Получить список всех файлов и папок по указному пути
        @param folder: Директория из которой нужно получить файлы и папки
        @return: Список файлов и список папок
        """
        # Список со всеми файлами
        arr_file: set[str] = set()
        # Список со всеми папками
        arr_folder: set[str] = set()
        ###################################
        # Изначальный путь к папке
        _path: str = folder
        # Временный список с папками для перебора
        _arr_select_folder: deque = deque([folder])
        _Live = True
        while _Live:
            # Выбираем первый элемент путь из очереди
            _path = _arr_select_folder[0]
            # Перебираем все файлы и папки в пути
            for x in listdir(_path):
                # Создаем полный путь
                file = path.join(_path, x)
                # Если папка
                if path.isdir(file):
                    # Добавляем в результирующий массив
                    arr_folder.add(file.replace(folder, ''))
                    # Добавляем в список перебора путей
                    _arr_select_folder.append(file)
                # Если файл
                else:
                    # Добавляем в результирующий список файлов
                    arr_file.add(file.replace(folder, ''))
            # Удаляем путь, который перебрали
            _arr_select_folder.popleft()
            # Если путей нет, то прекращаем перебор
            if len(_arr_select_folder) == 0:
                _Live = False
        return {
            "split_path": folder,
            "arr_file": arr_file,
            "arr_folder": arr_folder,
        }

    @staticmethod
    def _excludeFolderAndFile(arr_exclude: set[str], *,
                              arr_file: set[str],
                              arr_folder: set[str], **kwargs) -> tuple[set[str], set[str]]:
        """
        Метод для отчистки списка файлов и папок которые находятся в списке исключение

        @param arr_exclude: Список исключений
        @param arr_file: Список файлов
        @param arr_folder: Список папок
        @param split_path: Путь который нужно отсекать от пути файлов и папок
        @return: Новый список файлов и папок, с исключенными путями
        """

        def isExclude(_path: str, arr_exclude: set[str]) -> bool:
            # Проверяем путь на вхождение в список исключений
            for _re in arr_exclude:
                # Проверяем начло на соответствие шаблону исключения
                isExist = match(fr"{_re}[\W\w]*", _path)
                if isExist:
                    return True
            return False

        def logic(_arr_path) -> set[str]:
            _right_path: set[str] = set()
            # Перебираем пути
            for _path in _arr_path:
                # Если путь НЕ нужно исключить, то добавляем его в правильный путь
                if not isExclude(_path, arr_exclude):
                    _right_path.add(_path)
            return _right_path

        return logic(arr_file), logic(arr_folder)

    @classmethod
    def _dirDiff(cls,
                 outfolder: str, infolder: str,
                 arr_file: set[str], arr_folder: set[str]) -> DiffDir:
        """
        Метод для получения разницы между директориями.
        Проверка не пройдена если:
        - Файла или директории не существует
        - Файл имеют разные хеш суммы
        @return: Список директорий и файлов который нужно скопировать
        """

        def FolderIfNotExist() -> set[str]:
            """
            Получить список папок которых нет в Б директории
            """
            _res = set()
            for _path in arr_folder:
                _out_path = outfolder + _path
                if not path.isdir(_out_path):
                    _res.add(_path)
            return _res

        def FileIfChangeDataOrNotExist() -> tuple[set[str], set[str]]:
            """
            Скопировать файл если его нет или, у них различная хеш сумма
            """
            _diff_data_arr_file = set()
            _not_exist_arr_file = set()
            for _path in arr_file:
                _in_path = infolder + _path
                _out_path = outfolder + _path
                # Если файла нет, то копируем его
                if not path.isfile(_out_path):
                    _not_exist_arr_file.add(_path)
                # Если файл уже есть, то проверим его хеш
                else:
                    # Если хеш одинаковый, то не копируем файл
                    # Если хеш разный, то копируем файл
                    if sha256sum(_in_path) != sha256sum(_out_path):
                        _diff_data_arr_file.add(_path)

            return _diff_data_arr_file, _not_exist_arr_file

        """
        Получаем данные о директории А
        """
        # Файлы, которые имеют разную хеш сумму
        # Файлы которых есть в А, но нет в Б
        diff_data_arr_file, not_exist_arr_file = FileIfChangeDataOrNotExist()
        # Папки которых есть в А, но нет в Б
        not_exist_arr_folder: set[str] = FolderIfNotExist()

        """
        Получаем данные о директории Б 
        """
        # Получить список всех файлов и папок в директории Б
        all_path_out: dict[str, set[str] | str] = cls._getAllFileAndFolderFromPath(outfolder)
        # Файлы, которые существуют только в Б.
        # Это может происходить если мы добавили в исключение файл которые ранее в нем не был.
        file_intruder: set[str] = all_path_out['arr_file'].difference(arr_file)
        # Папки, которые существуют только в Б.
        # Это может происходить если мы добавили в исключение файл которые ранее в нем не был.
        folder_intruder: set[str] = all_path_out['arr_folder'].difference(arr_folder)

        _res = DiffDir(infolder, outfolder,
                       not_exist_arr_file,
                       not_exist_arr_folder,
                       diff_data_arr_file,
                       file_intruder,
                       folder_intruder)
        _res.log()
        return _res


class SmartCopy(BaseSmartDir):

    def execute(self) -> DiffDir:
        objDiffDir: DiffDir = self.getDiff()
        # Скопируем папки и файлы из А в Б директорию
        self.smartCopy(objDiffDir)
        # Удаляем файлы, которые нарушают консистентность из директории Б
        self.deleteIntruder(objDiffDir)
        return objDiffDir

    @staticmethod
    def deleteIntruder(objDiffDir):
        ...

    @staticmethod
    def smartCopy(objDiffDir: DiffDir):
        """
        Скопировать файлы и создать папки из указанных путей
        """
        # Создаем папки
        for _path in objDiffDir.not_exist_arr_folder:
            _out_path = objDiffDir.outfolder + _path
            makedirs(_out_path, exist_ok=True)
            logger.success(f"Mkdir:\n{_path}")

        # Скопировать файлы
        objDiffDir.not_exist_arr_file.update(objDiffDir.diff_data_arr_file)
        for _path in objDiffDir.not_exist_arr_file:
            _in_path = objDiffDir.infloder + _path
            _out_path = objDiffDir.outfolder + _path
            copyfile(_in_path, _out_path)
            logger.success(f"Copy:\n{_in_path} -> {_out_path}")


if __name__ == "__main__":
    SmartCopy("./smart_copy/test/conf/copyconf.yaml").execute()
