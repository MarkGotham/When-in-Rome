# -*- coding: utf-8 -*-
"""
NAME
===============================
Test Remote Score URLs (test_remote_urls.py)

BY:
===============================
Malcolm Sailor and Mark Gotham, 2023


LICENCE:
===============================
Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================

Test validity of remote urls.
Curently score only.

# TODO consider splitting this into two: `get_remote_scores` user function and `test_remote_score_URLs` testing validity

See also `collect_convert.convert_and_write_local`

"""

import json
from functools import partial
from multiprocessing import Manager
from multiprocessing.pool import Pool

import requests

from . import get_corpus_files

files = get_corpus_files(file_name="remote*.json")


def download_file(url, empty_files, errors, invalid_urls):
    print(f"Downloading {url}")
    try:
        response = requests.get(url)
    except requests.exceptions.MissingSchema:
        invalid_urls.append(url)
        return

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Open a file for writing in binary mode
        if not response.content:
            empty_files.append(url)
    else:
        errors.append(url)


remote_score_keys = [
    "remote_score_mscx",
    "remote_score_krn",
    "remote_score_mxl",
]


def main():
    manager = Manager()
    empty_files = manager.list()
    errors = manager.list()
    not_urls = manager.list()
    invalid_urls = manager.list()
    files_to_download = []
    download_f = partial(
        download_file, empty_files=empty_files, errors=errors, invalid_urls=invalid_urls
    )
    for f in files:
        with open(f) as inf:
            data = json.load(inf)
        for key in remote_score_keys:
            if key in data:
                url = data[key]

                if url is None:  # Key set but already declared to not exist
                    continue

                if not isinstance(url, str):
                    invalid_urls.append(f)
                    continue

                if not url.startswith("https://"):
                    not_urls.append(f)
                    continue

                files_to_download.append(url)

    with Pool(24) as pool:
        list(pool.imap(download_f, files_to_download))
    print(f"{len(empty_files)} empty files")
    for f in empty_files:
        print(f)

    print(f"{len(errors)} errors")
    for f in errors:
        print(f)

    print(f"{len(not_urls)} strings that are perhaps paths, not urls")
    for f in not_urls:
        print(f)

    print(f"{len(invalid_urls)} invalid URLS")
    for f in invalid_urls:
        print(f)

    return empty_files + errors + not_urls + invalid_urls  # return flat long list


if __name__ == "__main__":
    main()
