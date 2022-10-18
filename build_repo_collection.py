#!/usr/bin/env python3
"""
Automatically create a Jekyll collection of your public GitHub repositories.
"""

__author__ = "Kestin Goforth"
__copyright__ = "Copyright 2022, Kestin Goforth"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "kgoforth1503@gmail.com"

import datetime
import os

from github import Github

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", None)

DATE_FMT = "%Y-%m-%d %H:%M:%S"
DEST_DIR = "repos"
LAYOUT = "repo"


def get_repo_list(gh):
    return gh.get_user().get_repos(visibility="public")


def create_repo_file(repo):
    bytes = 0
    with open(os.path.join(DEST_DIR, f"{repo.name}.md"), "w+") as out:
        out.write(
            "\n".join(
                [
                    "---",
                    f"layout: {LAYOUT}",
                    f"name: {repo.name}",
                    f"full_name: {repo.full_name}",
                    f"description: {repo.description}",
                    f"url: {repo.html_url}",
                    f"is_archived: {repo.archived}",
                    f"is_fork: {repo.fork}",
                    f"watchers: {repo.watchers_count}",
                    f"forks: {repo.forks_count}",
                    f"stars: {repo.stargazers_count}",
                    f"pushed_at: {repo.pushed_at.strftime(DATE_FMT)}",
                    f"created_at: {repo.created_at.strftime(DATE_FMT)}",
                    f"updated_at: {repo.updated_at.strftime(DATE_FMT)}",
                    f"open_issues: {repo.open_issues_count}",
                    f"license: {repo.license.spdx_id if repo.license else None}",
                    f"checked_at: {datetime.datetime.now().strftime(DATE_FMT)}",
                    "---",
                    "",
                ]
            )
        )

        out.write(repo.get_readme().content)
        bytes = out.tell()
    return bytes


def main():
    import argparse
    import concurrent.futures
    import logging
    import sys

    """
    Automatically create a Jekyll collection of your public GitHub repositories.
    """

    global DATE_FMT, DEST_DIR, LAYOUT

    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(
        prog="build_repo_collection",
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Required Args
    parser.add_argument("dest", type=str, help="Destination Directory")

    # Optional Args
    parser.add_argument("--layout", "-l", type=str, help="Page Layout", default=LAYOUT)
    parser.add_argument("--date", "-d", type=str, help="Date Format", default=DATE_FMT)

    args = parser.parse_args()

    DEST_DIR = args.dest
    DATE_FMT = args.date
    LAYOUT = args.layout

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
    gh = Github(GITHUB_TOKEN)

    if os.path.isfile(DEST_DIR):
        logger.error("Destination Directory is exsisting file: %s", DEST_DIR)
        sys.exit(1)

    # Make sure output dir exists
    os.makedirs(DEST_DIR)

    futures = {}
    for repo in get_repo_list(gh):
        futures[executor.submit(create_repo_file, repo)] = repo.full_name

    for future in concurrent.futures.as_completed(futures):
        name = futures[future]
        try:
            logger.info("%d bytes written for %s completed", future.result(), name)
        except Exception as exc:
            logger.error("%s generated an exception: %s", name, exc)

    sys.exit(0)


if __name__ == "__main__":
    main()
