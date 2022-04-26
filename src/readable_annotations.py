import json
import sys

OUTSIDE = "0"
BEGIN = "B"
INSIDE = "I"
DELIM = "_"


def read_file(filename: str) -> dict:
    with open(filename, "r") as f:
        data = f.read()
    return json.loads(data)


def process_annotations(annotation: list) -> list[tuple]:
    text, entity_dict = annotation
    # split_text = text.split()
    encoded_text = []
    entities = entity_dict["entities"]
    prev = 0
    for entity in entities:
        start, end, tag = entity
        prev_text = text[prev:start].split()
        for tok in prev_text:
            encoded_text.append((tok, OUTSIDE))
        span = text[start:end].split()
        if len(span) > 1:
            encoded_text.append((span[0], BEGIN + DELIM + tag))
            for tok in span[1:]:
                encoded_text.append((tok, INSIDE + DELIM + tag))
        else:
            encoded_text.append((span[0], BEGIN + DELIM + tag))
        prev = end
    print(encoded_text)
    return encoded_text


def main():
    annot = read_file(sys.argv[1])
    annotations = annot["annotations"]
    annotation_list = []
    for annotation in annotations:
        annotation_list.append(process_annotations(annotation))


if __name__ == "__main__":
    main()
