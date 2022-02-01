# Что это

Это программа нужна когда нам нужно часто выборочно копировать файлы и папки, из одной директории в другую.

Вы можете создавать файл конфигурации который будет "синхронизировать" две директории.

- Копировать файлы и папки если их нет в выходной директории, или если их хеш сумма различна
- Удалять файлы и папки в выходной директории, которые случайно там окопались

Термины `A` `Б`:

- `A` - Директория ОТКУДА копируют данные
- `Б` - Директория КУДА копируют данные

# Как пользоваться

Посмотреть доступны команды

```bash
./sm --help
```

Получить информацию о двух директориях на основе конфигурации, например она расположена по пути `./copyconf.yaml`

```bash
./sm ./copyconf.yaml -i
```

Синхронизировать файлы и папки на основе конфигурации, например она расположена по пути `./copyconf.yaml`.

```bash
./sm ./copyconf.yaml -dc
```

---

# Запустить через `Python`

```bash
git clone https://github.com/denisxab/smart_copy;
python -m venv venv;
. ./venv/bin/activate;
pip install poetry;
poetry install;
python ./smart_copy/main.py --help
```

# Пример файла конфигурации `copyconf.yaml`

![Про `exclude`](./smart_copy/Group.jpg)

- `exclude_copy` - Не копировать файлы из `А` в `Б` (Эти файлы существуют только в `A`)
- `exclude_delete` - Не удалять файл из `Б` если их нет в `A` (Эти файлы существуют только в `Б`)
- `exclude` - Будет добавлен в  `exclude_copy` и `exclude_delete`
  (Эти файлы могу независимо существовать и в `А` и в `Б`)
- Пересечение обозначает что эти данные синхронизируются в одну сторону. В одну сторону обозначает, если мы случайно
  изменили данные в `Б`  то они заменяться на значения из `A`
  (Если данные изменились в `А` то они копируются в `Б`)

```yaml
# Что будем делать:
# cp - копировать
cp:
    # Путь к директории ОТКУДА копировать данные
    infloder: '/home/denis/PycharmProjects/pythonProject1/'
    # Файл и папки которые не копировать (Существуют в А но не в Б)
    exclude_copy:
        - poetry.lock
        - project_template/package-lock.json
        - project_template/project_name/frontend_react/static/frontend_react/public/
        - project_template/node_modules
        - project_template/deploy/log_django/error.log
        - project_template/deploy/log_django/all.log
        - project_template/deploy/log_django/trace.log
        - project_template/project_name/db.sqlite3
        - project_template/project_name/__cache
        - project_template/__pycache__
        - project_template/project_name/__pycache__
        - project_template/project_name/frontend_react/__pycache__
        - project_template/project_name/api/__pycache__
        - project_template/project_name/conf/__pycache__
    # Путь к директории КУДА копировать
    outfolder: '/home/denis/prog/django-start-pack_2/'
    # Файлы и папки которые не удалять (Существуют в Б)
    exclude_delete:
        - .git
        - app_template
    # Добавиться в `exclude_copy` и `exclude_delete`
    exclude:
        - pyproject.toml
        - .idea
        - venvs
        - project_template/package.json
        - project_template/.gitignore
        - project_template/.dockerignore
        - project_template/__env.env
```
