import re
import json
import sys


def fix_with_regex(data: str) -> str:
    pattern = re.compile(r'[^\x00-\x7F]')
    data = re.sub(pattern, '_', data)
    return data


def main() -> None:
    filename = sys.argv[-1]
    filepath = '../data/annotated_data/'
    out_filename = filename[:-6] + '_fixed.jsonl'
    with open(filepath+out_filename, 'w', encoding='utf8') as out_f:
        with open(filepath+filename, 'r', encoding='utf8') as f:
            # read each of the lines in the file
            for line in f:
                data = json.loads(line)
                # replace the weird characters (currently with _)
                data['data'] = fix_with_regex(data['data'])
                out_f.write(json.dumps(data) + '\n')


if __name__ == "__main__":
    main()
