import json
import jsonlines
from collections import defaultdict
from data_process_utils import (
    read_file,
    change_encoding,
    match_meta,
)

FILES = ["aparna_annotations.jsonl", "june_annotations.jsonl", "ayla_annotations.jsonl"]
PATH = "annotated_data/"
METAFILE = "raw_data/cleaned_reviews.json"
DOCSTART = "-DOCSTART- -X- -X- O\n"


def make_conll(annotations):
    metadata = []
    with open(METAFILE, encoding="utf8") as f:  # read in file with metadata
        for line in f:
            metadata = json.loads(line)

    encoded_data = []
    data_with_metadata = dict(dict())

    for i, annotation in enumerate(annotations):
        for doc in annotation:
            meta_doc = match_meta(doc, metadata)
            date = meta_doc["date"]
            if date not in set(data_with_metadata.keys()):
                data_with_metadata[date] = dict()
                data_with_metadata[date][0] = []
                data_with_metadata[date][1] = []
                data_with_metadata[date][2] = []
                data_with_metadata[date]["tokens"] = []
            for x in meta_doc["data"].split("\n"):
                if len(x.split()) > 1:
                    # print(x, x.split()[0], x.split()[-1])
                    data_with_metadata[date]["tokens"].append(x.split()[0])
                    data_with_metadata[date][i].append(x.split()[-1])
                else:
                    data_with_metadata[date]["tokens"].append(x)
                    data_with_metadata[date][i].append("")
            if data_with_metadata[date][i]:
                data_with_metadata[date]["tokens"] = data_with_metadata[date]["tokens"][
                                                     : len(data_with_metadata[date][i])
                                                     ]
    data_list = list(data_with_metadata.items())
    data_list.sort(key=lambda y: y[0])
    trimmed_data_list = []
    for date, doc_dic in data_list:
        empty_sum = 0
        for x in doc_dic.values():
            if not x:
                empty_sum += 1
        if empty_sum == 1:
            trimmed_data_list.append((date, doc_dic))
    with open("all_annotations.txt", "w", encoding="utf8") as conll_f:
        for date, doc_dict in trimmed_data_list:
            for i, tok in enumerate(doc_dict["tokens"]):
                token_line = [tok]
                for j in range(3):
                    if doc_dict[j]:
                        if tok == "-DOCSTART-":
                            token_line.append("-X-")
                        elif tok:
                            token_line.append(doc_dict[j][i])
                        else:
                            token_line.append("")
                    else:
                        if tok == "-DOCSTART-":
                            token_line.append("-X-")
                        elif tok:
                            token_line.append("N/A")
                        else:
                            token_line.append("")
                token_str = " ".join(token_line)
                print(token_str, file=conll_f)


def main():
    # read in the properly encoded files
    annotations = [read_file(PATH + filename) for filename in FILES]
    make_conll(annotations)


if __name__ == "__main__":
    main()
