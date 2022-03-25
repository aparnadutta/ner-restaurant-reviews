import json
import sys


def main() -> None:
    """Input file is a command line argument."""
    filename = sys.argv[1]
    # batch_number = filename[5:].split("_")[0]
    with open(filename, encoding='utf-8') as f:
        dicts = json.loads(f.read())
    for d in dicts:
        with open("updated_data/review_" + str(d['id']) + ".txt", 'w', encoding='utf-8') as out_f:
            out_f.write(d['review_text'])
    # with open("updated_data/prepared_data_" + batch_number + ".txt", 'w', encoding='utf-8') as out_f:
    #     for d in dicts:
    #         out_f.write(d['review_text'] + '\n')


if __name__ == '__main__':
    main()
