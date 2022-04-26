"""
Quick Script to change file encoding from iso 8859-1 to utf8
"""
from argparse import ArgumentParser

import jsonlines as jsonlines


def change_encoding():
    parser = ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()

    with open(args.input, "r", encoding="iso-8859-1") as in_file:
        reader = jsonlines.Reader(in_file)
        objects = [object for object in reader.iter(type=dict)]

    with open(args.output, "w", encoding="utf8") as outfile:
        writer = jsonlines.Writer(outfile)
        writer.write_all(objects)


if __name__ == "__main__":
    change_encoding()
