import pathlib
import shutil
import datetime
import argparse
import textwrap
from collections import Counter

parser = argparse.ArgumentParser(
description="Import ipynb notebooks from directory with students' submissions to nbgrader course directory.",
    usage=textwrap.dedent("""    
        Expected source directory format:
            <source>/John Smith - 2022-05-22 23-06-50-982887 - hw2_joshsmith (1).ipynb
            ...

        When run as
            python import_submissions.py --assigmnet assignment1 --notebook notebook1.ipynb --source <source> --destination <destination>

        Notebooks will be copied to:
            <destination>/submitted/John Smith/assignment1/notebook1.ipynb
    """),
)
parser.add_argument("-s", "--source", required=True)
parser.add_argument("-d", "--destination", required=True)
parser.add_argument("-a", "--assignment", required=True)
parser.add_argument("-n", "--notebook", required=True)

args = parser.parse_args()

assert args.notebook.endswith(".ipynb")
assert (pathlib.Path(args.destination) / "source").exists(), f"{args.destination!r} doesn't look like nbgrader course directory"

def list_submissions():
    for path in pathlib.Path(args.source).glob("*.ipynb"):
        name, ts, fname = path.name.split(" - ", maxsplit=2)
        ts = datetime.datetime.strptime(ts, "%Y-%m-%d %H-%M-%S-%f")
        yield {"student": name, "time": ts, "path": path}

submissions = list(list_submissions())

counts = Counter(submission["student"] for submission in submissions)
assert set(counts.values()) == {1}, "TODO: student must submit exactly one notebook"

for submission in submissions:
    assert "/" not in submission["student"]
    dst = pathlib.Path(args.destination) / "submitted" / submission["student"] / args.assignment / args.notebook
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(str(submission["path"]), str(dst))
    print("Done -", submission["student"])
