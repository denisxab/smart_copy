


# Написать программу по авто копированию файлов

Например, мы создаем `yaml` файл в котором указываем те файлы/папки которые нужно исключить из копирования.

```yaml
# Что будем делать:
# copy - копировать
copy:
  #  Папка откуда копировать 
  floder: "/home/denis/test_prog"
  # Файл и папки которые не копировать  
  exclude:
    - { { project_name } }/package.json
    - {{ project_name }}/__env.env
    - {{ project_name }}/.dockerignore
    - {{ project_name }}/.gitignore
    - pyproject.toml
    - {{ project_name }}/debloy/log_django
```