# TODO split this into two: `get_remote_scores` user function and `test_remote_score_URLs` testing validity

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


def main():
    manager = Manager()
    empty_files = manager.list()
    errors = manager.list()
    invalid_urls = manager.list()
    files_to_download = []
    download_f = partial(
        download_file, empty_files=empty_files, errors=errors, invalid_urls=invalid_urls
    )
    for f in files:
        with open(f) as inf:
            data = json.load(inf)
        for key in [
            "remote_score_mscx",
            "remote_score_krn",
            "remote_score_mxl",
        ]:
            if key in data:
                url = data[key]
                if not isinstance(url, str):
                    invalid_urls.append(f)
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

    print(f"{len(invalid_urls)} invalid URLS")
    for f in invalid_urls:
        print(f)


if __name__ == "__main__":
    main()
