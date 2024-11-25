from translateDataset import TranslateDataset

if __name__ == '__main__':
    td = TranslateDataset(max_threads=8)
    td.translate_dir('./input', './output')
