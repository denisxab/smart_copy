# Что это

Это программа нужна когда нам нужно часто выборочно копировать файлы и папки, из одной директории в другую.

Вы можете создавать файл конфигурации который будет "синхронизировать" две директории.

- Копировать файлы и папки если их нет в выходной директории, или если их хеш сумма различна
- Удалять файлы и папки в выходной директории, которые случайно там окопались

# Как пользоваться

Синхронизировать файлы и папки на основе конфигурации, например она расположена по пути `./copyconf.yaml`

```bash
./sm.bin -с ./copyconf.yaml
```

---

Посмотреть доступны команды

```bash
./sm.bin smart_copy/smart_copy.py --help
```

```bash
usage: smart_copy.py [-h] [-c PATH_CONF]

Умное копирование файлов

options:
  -h, --help            show this help message and exit
  -c PATH_CONF, --conf PATH_CONF
                        Путь к файлу конфигурации
```

# Установка

```bash
git clone https://github.com/denisxab/smart_copy;
python -m venv venv;
. ./venv/bin/activate;
pip install poetry;
poetry install;
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
