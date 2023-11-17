"""makedocs.py

Generates documentation from solutions and README.adoc files
"""

__version__ = "0.1"
__author__ = "Peter Wieland"

import sys
import os
from dataclasses import dataclass
from urllib.parse import quote


README_FILE = "README.adoc"
DAY_DIR_PREFIX = "day"
USERS_SUB_DIR = "users"

ADOC_GEN_DIR = os.path.join("gen", "adoc")
ADOC_BY_LANG_FILE = os.path.join(ADOC_GEN_DIR, "by_lang.adoc")
ADOC_BY_USER_FILE = os.path.join(ADOC_GEN_DIR, "by_user.adoc")
ADOC_BY_DAY_FILE = os.path.join(ADOC_GEN_DIR, "by_day.adoc")


@dataclass
class Solution:
    user: str
    lang: str
    day: int
    dir: str
    readme_file: str = None


def list_solutions(project_dir=os.path.abspath(sys.path[0])):
    """
    Find all solutions in current project directory.

    Parameters:
    project_dir (str, optional): the project directory. Defaults to the directory the interpreter was invoked from.

    Returns:
    list[Solution]: a list of solutions
    """
    solutions = []

    for day_dir_name in os.listdir(project_dir):
        day_dir = os.path.join(project_dir, day_dir_name)
        if not os.path.isdir(day_dir) \
            or not day_dir_name.startswith(DAY_DIR_PREFIX):
            # only process directories whose name starts with "day"
            continue

        # get the day part as int or skip entry
        try:
            day = int(day_dir_name[len(DAY_DIR_PREFIX):])
        except ValueError:
            continue

        for lang in os.listdir(day_dir):
            lang_dir = os.path.join(day_dir, lang)
            if not os.path.isdir(lang_dir):
                # only process directories
                continue

            for user in os.listdir(lang_dir):
                user_dir = os.path.join(lang_dir, user)
                if not os.path.isdir(user_dir):
                    # only process directories
                    continue

                readme_file = README_FILE \
                    if os.path.exists(os.path.join(user_dir, README_FILE)) \
                    else None

                solutions.append(
                    Solution(user, lang, day, user_dir, readme_file))

    return solutions



def make_user_docs(sols, adoc_file: str=ADOC_BY_USER_FILE):
    """
    Write an ADOC file per user and one summary ADOC file.

    Parameters:
    sols (list[Solution]): list of solutions
    adoc_file (str, optional): the summary file. Defaults to ADOC_BY_USER_FILE.
    """
    # create lists per user
    sols_for_users = {}
    for sol in sols:
        sols_for_users.setdefault(sol.user, []).append(sol)

    # determine number of solutions and documented solutions by user
    user_scores = []

    for user, user_sols in sols_for_users.items():
        n_tot = len(user_sols)
        n_doc = len([sol for sol in user_sols if sol.readme_file])
        user_scores.append((user, n_tot, n_doc))

    # sort to have highest number of documented solutions first,
    #    break ties by highest number of total solutions,
    #    break ties by sorting user names alphabetically
    user_scores.sort(key=lambda x: (-x[2], -x[1], x[0]))

    os.makedirs(os.path.dirname(adoc_file), exist_ok=True)
    with open(adoc_file, 'w', encoding="utf-8") as g:
        g.write("[[top]]\n");
        g.write("= Solutions by user\n\n")
        g.write("link:by_day.html[Solutions by Day] &bull; link:by_lang.html[Solutions by Language] &bull; link:by_user.html[Solutions by User]\n\n")
        g.write("|===\n")

        for user, n_tot, n_doc in user_scores:
            user_sols = sols_for_users[user]
            g.write(f"| link:users/{quote(user)}.html[{user}] | {n_tot} Solution{'s' if n_tot != 1 else ''} ({n_doc} documented)\n")

            user_file = os.path.join(os.path.dirname(adoc_file), "users", user + ".adoc")
            os.makedirs(os.path.dirname(user_file), exist_ok=True)
            with open(user_file, 'w', encoding="utf-8") as f:
                f.write("[[top]]\n")
                f.write(f"= Solutions by {user}\n\n")
                f.write("link:../by_day.html[Solutions by Day] &bull; link:../by_lang.html[Solutions by Language] &bull; link:../by_user.html[Solutions by User]\n\n")
                for sol in sorted(user_sols, key=lambda sol: (sol.day, sol.lang)):
                    f.write(f"\n[[sol-{sol.day}]]\n")

                    readme_file = sol.readme_file \
                        if not sol.readme_file or os.path.isabs(sol.readme_file) \
                        else os.path.join(sol.dir, sol.readme_file)
                    if readme_file:
                        f.write(f"include::{readme_file}[leveloffset=0]\n")
                    else:
                        f.write(f"== Undocumented {sol.lang} solution for day {sol.day}\n")
                    f.write("link:#top[Top]\n")

        g.write("|===\n")


def make_lang_doc(sols, adoc_file: str=ADOC_BY_LANG_FILE):
    """
    Write an ADOC file for an overview by language.

    Parameters:
    sols (list[Solution]): list of solutions
    adoc_file (str, optional): the file to be written. Defaults to ADOC_BY_LANG_FILE
    """
    os.makedirs(os.path.dirname(adoc_file), exist_ok=True)
    with open(adoc_file, 'w', encoding="utf-8") as f:
        cur_lang = None
        cur_day = None
        f.write("[[top]]\n")
        f.write("= Solutions by language\n\n")
        f.write("link:by_day.html[Solutions by Day] &bull; link:by_lang.html[Solutions by Language] &bull; link:by_user.html[Solutions by User]\n\n")
        for sol in sorted(sols, key=lambda sol: (sol.lang, sol.day, sol.user)):
            if cur_lang != sol.lang:
                if cur_lang != None:
                    f.write("|===\n\n")
                    f.write("link:#top[Top]\n\n")
                f.write(f"== {sol.lang}\n\n")
                f.write("|===\n")

            f.write(f"| {sol.day if sol.day != cur_day else '':2} | link:users/{quote(sol.user)}.html#sol-{sol.day}[{sol.user}]\n")

            cur_lang = sol.lang
            cur_day = sol.day

        if cur_lang != None:
            f.write("|===\n")
            f.write("link:#top[Top]\n\n")


def make_day_doc(sols, adoc_file: str=ADOC_BY_DAY_FILE):
    """
    Write an ADOC file for an overview by day.

    Parameters:
    sols (list[Solution]): list of solutions
    adoc_file (str, optional): the file to be written. Defaults to ADOC_BY_DAY_FILE
    """
    os.makedirs(os.path.dirname(adoc_file), exist_ok=True)
    with open(adoc_file, 'w', encoding="utf-8") as f:
        cur_day = None
        cur_lang = None
        f.write("[[top]]\n")
        f.write("= Solutions by day\n\n")
        f.write("link:by_day.html[Solutions by Day] &bull; link:by_lang.html[Solutions by Language] &bull; link:by_user.html[Solutions by User]\n\n")
        for sol in sorted(sols, key=lambda sol: (sol.day, sol.lang, sol.user)):
            if cur_day != sol.day:
                if cur_day != None:
                    f.write("|===\n\n")
                    f.write("link:#top[Top]\n\n")
                f.write(f"== Day {sol.day}\n\n")
                f.write("|===\n")

            f.write(f"| {sol.lang if sol.lang != cur_lang else '':10} | link:users/{quote(sol.user)}.html#sol-{sol.day}[{sol.user}]\n")

            cur_day = sol.day
            cur_lang = sol.lang

        if cur_day != None:
            f.write("|===\n")
            f.write("link:#top[Top]\n\n")


sols = list_solutions()
make_user_docs(sols)
make_lang_doc(sols)
make_day_doc(sols)

# asciidoctor -a toc=right -a code-highlighter=rouge -D gen/html gen/adoc/*.adoc
# asciidoctor -a toc=right -a code-highlighter=rouge -D gen/html/users gen/adoc/users/*.adoc
