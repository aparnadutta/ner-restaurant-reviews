"""
Runs adjudication and creates gold standard annotation file
"""

INPUT_PATH = "all_annotations.txt"
OUTPUT_PATH = "adjudicated_annotations.txt"

DOCSTART = "-DOCSTART-"
OUTSIDE = "O"
DELIM = " "
EMPTY = "None"


def adjudicate():
    with open(INPUT_PATH, "r") as input_file, open(OUTPUT_PATH, "w") as output_file:
        for line in input_file:
            if line != "\n":
                token, annotator0, annotator1, annotator2 = line.strip().split(" ")
                if token == DOCSTART:
                    print(DOCSTART + DELIM + OUTSIDE, file=output_file)
                elif annotator1 != EMPTY:
                    print(token + DELIM + annotator1, file=output_file)
                elif annotator0 != EMPTY:
                    print(token + DELIM + annotator0, file=output_file)
                else:
                    print("ERROR: ", line)
            else:
                print(file=output_file)


if __name__ == '__main__':
    adjudicate()
