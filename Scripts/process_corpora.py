from Code.updates_and_checks import process_corpus, corpora

if __name__ == '__main__':
    for c in corpora:
        process_corpus(c, combine=True, slices=True, feedback=True, overwrite=True)
