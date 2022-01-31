from click import argument, command, option
from loguru import logger

from smart_copy import SmartCopy


@command("scc", short_help="Краткое описание команды 1")  # Указываем внешнее имя для команды
@option('isdelete', "--delete", '-d', is_flag=True, default=False,
        help="Нужно ли удалять файлы и папки нарушители ?")
@option('iscopy', "--copy", '-c', is_flag=True, default=False,
        help="Нужно ли копировать файлы и папки ?")
@option('isinfo', "--info", '-i', is_flag=True, default=False,
        help="Нужно ли показать подробный отчет ?")
@argument('path_conf')
def smart_copy_console(path_conf, isdelete, iscopy, isinfo):
    """
    Умное копирование файлов и папок
    """
    logger.trace(f"{path_conf=},{isdelete=},{iscopy=},{isinfo=}")
    obj: SmartCopy = SmartCopy(path_conf, isdelete, iscopy, isinfo)
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
