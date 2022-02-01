from collections import deque
from os import path, listdir, rmdir, remove, makedirs
from pprint import pformat
from re import match
from shutil import copyfile

from loguru import logger
from mg_file import YamlFile
from pydantic.error_wrappers import ValidationError

from helpful import CopyConf, sha256sum, OsSeparator, DiffDir


class BaseSmartDir:
    def __init__(self, path_conf: str, is_delete: bool, is_copy: bool, is_info: bool):
        """
        Валидация файла конфигураций
        """
        # Флаги
        self.is_info: bool = is_info
        self.is_copy: bool = is_copy
        self.is_delete: bool = is_delete
        # Работа с файлом конфигурации
        self._file = YamlFile(path_conf)
        try:
            self.conf = CopyConf.parse_obj(self._file.readFile())
            self.infloder: str = self.conf.cp.infloder
            self.outfolder: str = self.conf.cp.outfolder
            # Заменить имя при копировании
            self.replace_name_dict: dict[str, str] | dict = self.conf.cp.replace_name
            # Исключение файлов и папок
            self.exclude_copy: set = set(self.conf.cp.exclude_copy) if self.conf.cp.exclude_copy else set()
            self.exclude_delete: set = set(self.conf.cp.exclude_delete) if self.conf.cp.exclude_delete else set()
            self.exclude: set = set(self.conf.cp.exclude) if self.conf.cp.exclude else set()
        except ValidationError as e:
            print(e.json())

    def getDiff(self) -> DiffDir:
        """
        Получить различия между дирекцией А и Б

        А - директория откуда брать данные
        Б - директория куда копировать данные
        """
        # Получаем пути к файлам и папкам из директории А, которые не исключены в конфигурациях копирования
        arr_file_in, arr_folder_in = self._excludeFolderAndFile(self.exclude_copy.union(self.exclude),
                                                                **self._getAllFileAndFolderFromPath(self.infloder))
        # Получаем пути к файлам и папкам из директории Б, которые не исключены в конфигурациях копирования и удаления
        arr_file_out, arr_folder_out = self._excludeFolderAndFile(self.exclude_delete.union(self.exclude),
                                                                  **self._getAllFileAndFolderFromPath(self.outfolder))

        logger.debug(
            "Tracking:\n{0}".format(pformat(
                {'arr_file_in': arr_file_in,
                 'arr_folder_in': arr_folder_in,
                 'arr_file_out': arr_file_out,
                 'arr_folder_out': arr_folder_out}, compact=True)))

        # Получим разницу между А и Б директориями
        objDiffDir = self._dirDiff(
            self.outfolder,
            self.infloder,
            arr_file_in, arr_folder_in,
            arr_file_out, arr_folder_out,
        )
        return objDiffDir

    @staticmethod
    def _excludeFolderAndFile(arr_exclude: set[str], *,
                              arr_file: set[str],
                              arr_folder: set[str], **kwargs) -> tuple[set[str], set[str]]:
        """
        Метод для отчистки списка файлов и папок которые находятся в списке исключение

        @param arr_exclude: Список исключений
        @param arr_file: Список файлов
        @param arr_folder: Список папок
        @return: Новый список файлов и папок, с исключенными путями
        """

        # Если нечего исключать, то возвращаем исходные данные
        if not arr_exclude:
            return arr_file, arr_folder

        def isExclude(_path: str) -> bool:
            # Проверяем путь на вхождение в список исключений
            for _re in arr_exclude:
                # Проверяем начло не соответствие шаблону исключения
                isExist = match(fr"{_re}[\W\w]*", _path.__str__())
                if isExist:
                    return True
            return False

        def logic(_arr_path) -> set[str]:
            _right_path: set[str] = set()
            # Перебираем пути
            for _path in _arr_path:
                # Если путь НЕ нужно исключить, то добавляем его в правильный путь
                if not isExclude(_path):
                    _right_path.add(_path)
            return _right_path

        return logic(arr_file), logic(arr_folder)

    @classmethod
    def _dirDiff(cls,
                 outfolder: str, in_folder: str,
                 arr_file_in: set[str], arr_folder_in: set[str],
                 arr_file_out: set[str], arr_folder_out: set[str],

                 ) -> DiffDir:
        """
        Метод для получения разницы между директориями.
        Проверка не пройдена если:
        - Файла или директории не существует
        - Файл имеют разные хеш суммы
        - Файл или папка которая находиться в исключение, но существует в Б

        @return: Список директорий и файлов который нужно скопировать
        """

        def FolderIfNotExist() -> set[str]:
            """
            Получить список папок которых нет в Б директории
            """
            _res_f = set()
            for _path in arr_folder_in:
                _out_path = f"{outfolder}{_path}"
                if not path.isdir(_out_path):
                    _res_f.add(_path)
            return _res_f

        def FileIfChangeDataOrNotExist() -> tuple[set[str], set[str]]:
            """
            Скопировать файл если его нет или, у них различная хеш сумма
            """
            _diff_data_arr_file = set()
            _not_exist_arr_file = set()
            for _path in arr_file_in:
                _in_path = f"{in_folder}{_path}"
                _out_path = f"{outfolder}{_path}"
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
        # Файлы, которые имеют разную хеш сумму. Файлы которых есть в А, но нет в Б
        diff_data_arr_file, not_exist_arr_file = FileIfChangeDataOrNotExist()
        # Папки которых есть в А, но нет в Б
        not_exist_arr_folder: set[str] = FolderIfNotExist()

        """
        Получаем данные о директории Б 
        """
        # Файлы, которые существуют только в Б.
        # Это может происходить если мы добавили в исключение файл которые ранее в нем не был.
        file_intruder: set[str] = arr_file_out.difference(arr_file_in)
        # Папки, которые существуют только в Б.
        # Это может происходить если мы добавили в исключение файл которые ранее в нем не был.
        folder_intruder: set[str] = arr_folder_out.difference(arr_folder_in)
        _res = DiffDir(in_folder, outfolder,
                       not_exist_arr_file,
                       not_exist_arr_folder,
                       diff_data_arr_file,
                       file_intruder,
                       folder_intruder)
        return _res

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
                    # Если имя переименовали то создаем объект `TypeReplaceName
                    arr_folder.add(file.replace(folder, ''))
                    # Добавляем в список перебора путей
                    _arr_select_folder.append(file)
                # Если файл
                else:
                    # Добавляем в результирующий список файлов
                    # Если имя переименовали то создаем объект `TypeReplaceName
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
    def sort_path(arr_path: list[str] | set[str], reverse: bool) -> list[str]:
        """
        Отсортировать пути.
        Для создания и удаления папок необходимо соблюдать порядок путей.

        @param arr_path: Список путей
        @param reverse: Сортировать в обратном порядке
        @return: Отсортированные пути
        """
        # Создаем список с количеством разделителей директорий
        _res: list[tuple[int, str]] = [(len(_x.split(OsSeparator)), _x) for _x in list(arr_path)]
        # Сортируем директории по количеству разделителей, в обратном порядке
        _res.sort(key=lambda k: k[0], reverse=reverse)
        # Преобразуем данные
        _res: list[str] = [_x[1] for _x in _res]
        return _res


class SmartCopy(BaseSmartDir):
    def execute(self) -> DiffDir:
        objDiffDir: DiffDir = self.getDiff()
        # Показать подробный отчет
        if self.is_info:
            objDiffDir.log()
        # Скопируем папки и файлы из директории А в директорию Б
        if self.is_copy:
            self.smartCopy(objDiffDir)
        # Удаляем файлы, которые нарушают консистентность из директории Б
        if self.is_delete:
            self.deleteIntruder(objDiffDir)
        return objDiffDir

    def deleteIntruder(self, objDiffDir: DiffDir):
        """
        Удаляем файлы, которые нарушают консистентность из директории Б
        """
        # Удаляем файлы
        _tmp = []
        for _path_file in objDiffDir.file_intruder:
            _out_path_file = objDiffDir.outfolder + _path_file
            remove(_out_path_file)
            _tmp.append(_out_path_file)
        logger.warning("DelFile:\n{0}".format(pformat(_tmp)))

        # Удаляем папки
        _tmp = []
        for _path_folder in self.sort_path(objDiffDir.folder_intruder, True):
            _out_path_folder = objDiffDir.outfolder + _path_folder
            rmdir(_out_path_folder)
            _tmp.append(_out_path_folder)
        logger.warning("DelDir:\n{0}".format(pformat(_tmp)))

    def smartCopy(self, objDiffDir: DiffDir):
        """
        Скопировать файлы и создать папки из указанных путей
        """

        # Создаем папки
        _tmp = []
        for _path in self.sort_path(objDiffDir.not_exist_arr_folder, False):
            _out_path = objDiffDir.outfolder + _path
            makedirs(_out_path)
            _tmp.append(_out_path)
        logger.success("Mkdir:\n{0}".format(pformat(_tmp)))

        # Скопировать файлы
        _tmp = []
        objDiffDir.not_exist_arr_file.update(objDiffDir.diff_data_arr_file)
        for _path in objDiffDir.not_exist_arr_file:
            _in_path = objDiffDir.infloder + _path
            _out_path = objDiffDir.outfolder + _path
            copyfile(_in_path, _out_path)
            _tmp.append(_in_path)
        logger.success("Copy:\n{0}".format(pformat(_tmp)))


if __name__ == "__main__":
    ...
    # print(SmartCopy("./smart_copy/test/conf/copyconf.yaml").execute())
