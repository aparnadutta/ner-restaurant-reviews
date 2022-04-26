import json
import sys


def main() -> None:
    """Input file is a command line argument."""
    filename = sys.argv[1]
    with open(filename, encoding='utf-8') as f:
        dicts = json.loads(f.read())
    for d in dicts:
        with open("updated_data/review_" + str(d['id']) + ".txt", 'w', encoding='utf-8') as out_f:
            out_f.write(d['review_text'])


if __name__ == '__main__':
    main()
