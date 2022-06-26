## Краткие отличия от nbgrader

Сайт проекта https://nbgrader.readthedocs.io/

Составление и проверка дз ничем не отличается от обычного использования nbgrader, за исключением:
1. Наличия своего `nbgrader_config.py` с локализованными placeholder'ами решений и timeout'ами на выполнение
2. Возможности импорта решений студентов из папки, сформированной ботом (`utils/import_submissions.py`)
3. Опционального требования именовать id'шники "Autograder tests"-ячеек в формате `task-(имя задачи)-cell-(id'шник ячейки)` для п. 3
4. Возможности экспорта оценок (с гранулярностью по каждому заданию), отчётов о проверке (загружаются на google drive) и комментариев для рассылки ботом (`utils/export.py`)
    - для загрузки на гугл-диск необходимо положить креды гугла с доступом в api гугл-диска в `utils/credentials.json`

## Краткая инструкция

Инструкция ниже ничем не отличается от [документации nbgrader'а](https://nbgrader.readthedocs.io), кроме моментов, перечисленных в тексте выше.

### Установка

Было протестировано с python 3.9, работоспособность для более старых версий не гарантируется

```bash
pip install -r requirements.txt
jupyter nbextension install --user --py nbgrader --overwrite
jupyter nbextension enable --user --py nbgrader
jupyter serverextension enable --user --py nbgrader
```

(подробнее в [документации](https://nbgrader.readthedocs.io/en/stable/user_guide/installation.html))

### Создание задания

1. Создать новую папку для курса (например, `course_dir`) и перейти в неё
2. Расположить в ней `nbgrader_config.py` из данного репозитория
3. Запустить `jupyter notebook` (находясь в этой папке)
4. Проследовать инструкции из замечательной [документации](https://nbgrader.readthedocs.io/en/stable/user_guide/creating_and_grading_assignments.html#developing-assignments-with-the-assignment-toolbar) по созданию и оформления дз для автопроверки nbgrader'ом, опционально пропустив пункты про manually graded cells. Если кратко, нужно проделать следующие шаги:
    - создать ноутбук по пути типа `source/assignment1/hw1.ipynb`
    - написать в отдельных ячейках решения, выделив комментариями в них код, который будет вырезан из версии для студентов
    - написать в отдельных ячейках тесты assert'ами (опционально скрытые)
    - nbgrader'ом создать версию для студентов, из которой будут удалены решения и скрытые тесты
5. Для возможности точной разбалловки по задачам, у `"Autograder tests"`-ячеек id'шник следует указать в формате `task-{номер задачи}-cell-{изначальный id}`. Напрмер, чтобы отнести ячейку к задаче `2.1`, нужно произвести замену:
    - из `cell-28ce37d0e0fe5140`
    - на `task-2.1-cell-28ce37d0e0fe5140`

### Запуск автопроверки

Предполагается, что решения студентов находятся в папке `submissions-from-bot` в формате:
```
./submissions-from-bot/John Smith - 2022-05-22 23-06-50-982887 - hw1_joshsmith (1).ipynb
./submissions-from-bot/Пример Примерыч - 2022-05-23 23-06-50-982887 - решение.ipynb
...
```

1. Импортировать решения в директорию курса командой:
```shell
python {путь до репозитория}/utils/import_submissions.py --assigmnet assignment1 --notebook hw1.ipynb --source ./submissions-from-bot --destination {путь до директории курса}
```
2. Из папки курса запустить команды (или почитать как это делать в [документации](https://nbgrader.readthedocs.io/en/stable/user_guide/creating_and_grading_assignments.html#autograde-assignments)) для запуска автопроверки и генерации html-отчётов:
```shell
nbgrader autograde --assignment assignment1
nbgrader generate_feedback --assignment assignment1
```
Для повторного запуска после изменения посылки можно добавить флаг `--force`, т.к. nbgrader не запускает проверку и генерацию отчётов, если результат уже есть.

3. Сгенерировать csv-файл с оценками и комментариями с помощью команды (где папку на гугл-диске заменить на свою, либо вовсе убрать аргумент `-u`): 
```
python {путь до репозитория}/utils/export.py \
    -n ./source/assignment1/hw1.ipynb \
    -u "https://drive.google.com/drive/u/1/folders/1DwwmlmQs7TAm1RO6hzK2fVvSKGQD8b3M" \
    -o ./feedback.csv
```