import json
import sys


def main() -> None:
    """The input file should start with a number, ie. '02_cleaned_reviews.json'"""
    filename = sys.argv[1]
    batch_number = filename[5:].split("_")[0]
    with open(filename, encoding='utf-8') as f:
        dicts = json.loads(f.read())
    with open("data/prepared_data_" + batch_number + ".txt", 'w', encoding='utf-8') as out_f:
        for d in dicts:
            out_f.write(d['review_text'] + '\n')


if __name__ == '__main__':
    main()
