from click import argument, command, option
from loguru import logger

from smart_copy import SmartCopy


@command("scc", short_help="Копирование")  # Указываем внешнее имя для команды
@option('is_delete', "--delete", '-d', is_flag=True, default=False,
        help="Удалить файлы и папки нарушители")
@option('is_copy', "--copy", '-c', is_flag=True, default=False,
        help="Копировать файлы и папки")
@option('is_info', "--info", '-i', is_flag=True, default=False,
        help="Показать подробный отчет")
@argument('path_conf')
def smart_copy_console(path_conf, is_delete, is_copy, is_info):
    """
    Умное копирование файлов и папок
    """
    logger.trace(f"{path_conf=},{is_delete=},{is_copy=},{is_info=}")
    obj: SmartCopy = SmartCopy(path_conf, is_delete, is_copy, is_info)
    obj.execute()

    # with click.progressbar([1, 2, 3],
    #                        label="Прогресс", ) as bar:
    #     for x in bar:
    #         print(f"sleep({x})...")
    #         time.sleep(x)


def main():
    smart_copy_console()


if __name__ == '__main__':
    main()
