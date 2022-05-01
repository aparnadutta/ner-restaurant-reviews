"""
Go through updated_all_annotations.txt
Write to adjudicated_annotations.txt
Write each line
Pick an annotator
"""

from typing import NamedTuple

# Assumes you are running script from inside src directory
INPUT_PATH = "../UPDATED_all_annotations.txt"
OUTPUT_PATH = "../adjudicated_annotations.txt"

DOCSTART = "-DOCSTART-"
OUTSIDE = "O"
DELIM = " "
EMPTY = "N/A"

# 0 Aparna, 1 June, 2 Ayla


class Annotation(NamedTuple):
    """
    An immutable annotation with a token and annotations from three annotators
    """
    token: str
    annotator_0: str
    annotator_1: str
    annotator_2: str

def adjudicate():
    with open(INPUT_PATH, "r") as input_file, open(OUTPUT_PATH, "w") as output_file:
        for line in input_file:
            if line != "\n":
                tok, col0, col1, col2 = line.strip().split(" ")
                annotation = Annotation(token=tok, annotator_0=col0, annotator_1=col1, annotator_2=col2)
                if annotation.token == DOCSTART:
                    print(DOCSTART + DELIM + OUTSIDE, file=output_file)
                # Must check NOT EMPTY as there are tokens with three annotations
                elif annotation.annotator_0 != EMPTY and annotation.annotator_1 != EMPTY:
                    print(annotation.token + DELIM + annotation.annotator_0, file=output_file)
                elif annotation.annotator_1 != EMPTY and annotation.annotator_2 != EMPTY:
                    print(annotation.token + DELIM + annotation.annotator_1, file=output_file)
                elif annotation.annotator_2 != EMPTY and annotation.annotator_0 != EMPTY:
                    print(annotation.token + DELIM + annotation.annotator_2, file=output_file)
                else:
                    print("ERROR: ", line)
            else:
                print(file=output_file)


if __name__ == '__main__':
    adjudicate()
