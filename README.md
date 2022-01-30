# Что это

Это программа нужна когда нам нужно часто выборочно копировать файлы и папки, из одной директории в другую.

Вы можете создавать файл конфигурации который будет "синхронизировать" две директории.

- Копировать файлы и папки если их нет в выходной директории, или если их хеш сумма различна
- Удалять файлы и папки в выходной директории, которые случайно там окопались

# Установка

```bash
git clone https://github.com/denisxab/smart_copy;
python -m venv venv;
. ./venv/bin/activate;
pip install poetry;
poetry install;
```

# Как пользоваться

Синхронизировать файлы и папки на основе конфигурации, например она расположена по пути `./copyconf.yaml`

```bash
python smart_copy/main.py -с ./copyconf.yaml
```

---

Посмотреть доступны команды

```bash
python smart_copy/main.py --help
```

```bash
usage: main.py [-h] [-c PATH_CONF]

Умное копирование файлов

options:
  -h, --help            show this help message and exit
  -c PATH_CONF, --conf PATH_CONF
                        Путь к файлу конфигурации
```

# Пример файла конфигурации

```yaml
# Что будем делать:
# cp - копировать
cp:
  #  Папка откуда копировать
  infloder: "/home/prog/data_test/dev/"
  # Папка куда копировать
  outfolder: "/home/prog/data_test/main/"
  # Файл и папки которые не копировать
  exclude:
    - pf/package.json
    - pf/__env.env
    - pf/.gitignore
    - pf/node_modules
    - pf/project_name
    - pyproject.toml
    - pf/debloy/log_django
```
