import json
import jsonlines
from collections import defaultdict
from data_process_utils import (
    read_file,
    change_encoding,
    match_meta,
    get_date
)

FILES = ["aparna_annotations.jsonl", "june_annotations.jsonl", "ayla_annotations.jsonl"]
PATH = "../data/annotated_data/"
METAFILE = "../data/raw_data/cleaned_reviews.json"
DOCSTART = "-DOCSTART-\t-X-\t-X-\tO\n"


def make_conll(annotations, out_path):
    metadata = []
    with open(METAFILE, encoding="utf8") as f:  # read in file with metadata
        for line in f:
            metadata = json.loads(line)
    data_with_metadata = defaultdict(lambda: defaultdict(dict, {k: [] for k in (0, 1, 2, "tokens")}))

    for annotator_id, annotation in enumerate(annotations):
        for doc in annotation:
            meta_doc = match_meta(doc, metadata)
            date = meta_doc["date"]
            for tok_tag_row in meta_doc["data"].split("\n"):
                if len(tok_tag_row.split()) > 1:   # if the line contains a token and tag
                    tok, _, _, tag = tok_tag_row.split()
                    data_with_metadata[date]["tokens"].append(tok)
                    data_with_metadata[date][annotator_id].append(tag)
                else:   # if the line is a DOCSTART or newline
                    data_with_metadata[date]["tokens"].append(tok_tag_row)
                    data_with_metadata[date][annotator_id].append("")   # append empty string to keep lists same length
            if data_with_metadata[date][annotator_id]:
                data_with_metadata[date]["tokens"] = data_with_metadata[date]["tokens"][: len(data_with_metadata[date][annotator_id])]

    data_list = list(data_with_metadata.items())
    data_list.sort(key=lambda y: y[0])
    trimmed_data_list = []
    for date, doc_dic in data_list:
        empty_sum = 0
        for val in doc_dic.values():
            if not val:
                empty_sum += 1
        if empty_sum == 1:
            trimmed_data_list.append((date, doc_dic))

    with open(out_path, "w", encoding="utf8") as conll_f:
        for date, doc_dict in trimmed_data_list:
            for i, tok in enumerate(doc_dict["tokens"]):
                if tok == "-DOCSTART-":
                    token_line = ["-DOCSTART-", "-X-", "-X-", "O"]
                else:
                    token_line = [tok]
                    for j in range(3):
                        if tok:
                            if doc_dict[j]:
                                token_line.append(doc_dict[j][i])
                            else:
                                token_line.append("N/A")
                token_str = " ".join(token_line)
                print(token_str, file=conll_f)


def main():
    # read in the properly encoded files
    annotated_files = [read_file(PATH + filename) for filename in FILES]
    make_conll(annotated_files, "../6_TEST_all_annotations.txt")


if __name__ == "__main__":
    main()
