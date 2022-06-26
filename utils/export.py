import pathlib
import argparse
import textwrap
import re

from tqdm.auto import tqdm
import pandas as pd
import nbgrader.api

from gdrive_share import upload_and_share


parser = argparse.ArgumentParser(
    description="Generate comments and optionally upload feedback html to google drive",
)
parser.add_argument("-n", "--source_notebook", required=True)
parser.add_argument("-u", "--upload_folder", help="Google Drive folder id or url to upload feedback to")
parser.add_argument("-o", "--output", required=True, help="Output csv path")

args = parser.parse_args()

nb_path = pathlib.Path(args.source_notebook).absolute()
assert nb_path.match("source/*/*.ipynb"), f"Invalid source notebook path {nb_path!r}"
notebook_name = nb_path.stem
assignment_name = nb_path.parent.name
course_dir = nb_path.parent.parent.parent


gb = nbgrader.api.Gradebook(f'sqlite:///{course_dir}/gradebook.db')


notebook = gb.find_notebook(notebook_name, assignment_name)

cell2task = dict()
for cell in notebook.grade_cells:
    match = re.match("task-(.*)-cell-.*", cell.name)
    if match is None:
        task = "other"
    else:
        [task] = match.groups()
    cell2task[cell.name] = task

tasks = sorted(set(cell2task.values()))

max_scores = {task: 0 for task in tasks}
for cell in notebook.grade_cells:
    max_scores[cell2task[cell.name]] += cell.max_score

records = []
for submission in tqdm(notebook.submissions):
    scores = {task: 0 for task in tasks}
    for cell in submission.grades:
        scores[cell2task[cell.name]] += cell.score

    student = submission.student.id

    feedback_path = course_dir / "feedback" / student / assignment_name / f"{notebook_name}.html"
    assert feedback_path.is_file()

    if args.upload_folder is not None:
        url = upload_and_share(
            local_path=str(feedback_path),
            remote_name=f"{student}.html",
            folder=args.upload_folder,
        )
    else:
        url = None

    total_score = sum(scores.values())
    assert total_score == submission.score
    records.append({
        "student": student,
        **scores,
        "sum": total_score,
        "comment": "\n".join(filter(None, (
            "Разбалловка:",
            *(
                f"- {task}: {scores[task]} / {max_scores[task]}"
                for task in max_scores.keys()
            ),
            f"Итоговый балл: {total_score}",
            (
                f"Подробный отчёт со скрытыми тестами: {url} (скачайте и откройте html в браузере)"
                if url is not None
                else None
            )
        ))),
    })
pd.DataFrame(records).set_index("student").sort_index().to_csv(args.output)