import json
from typing import Any

import spacy
from collections import defaultdict
from data_process_utils import match_meta, get_date, encode_bio
from unidecode import unidecode

# FILES = ["aparna_annotations.jsonl", "june_annotations.jsonl", "ayla_annotations.jsonl"]
FILES = ["aparna_annotations.jsonl", "edit_june.jsonl", "edit_ayla.jsonl"]
PATH = "../data/raw_annotations/"
METAFILE = "../data/raw_data/cleaned_reviews.json"

DOCSTART = "-DOCSTART- -X- -X- O\n"

nlp = spacy.load("en_core_web_sm")


# converts the char-level mentions to tok-level mentions for each document in the list of docs
def char_to_tokens(annotator_docs: list[dict]) -> list[dict]:
    # dataset = sorted(annotators_docs, key=lambda x: x['id'])

    mention_lists = []

    for document in annotator_docs:
        text = document["data"]
        doc = nlp(text)
        tok_char_indices = [token.idx for token in doc]

        doc_tokens = [token for token in doc]
        document["tokens"] = doc_tokens
        char2tok = {
            tok_char_indices[num_toks]: num_toks
            for num_toks in range(len(tok_char_indices))
        }

        mentions = document["label"]

        # dict that maps sent_id to a tuple of (sentence, mentions)
        sent_id_to_sent = {
            sent_id: (sent, []) for sent_id, sent in enumerate(doc.sents)
        }

        sent_to_sent_id = {sent: sent_id for sent_id, sent in enumerate(doc.sents)}

        for mention in mentions:
            start, end, entity_type = mention
            entity = text[start:end]

            if entity[0] == " ":
                start += 1
                entity = entity[1:]
            ment_tokens = entity.split()
            length = len(ment_tokens)

            if start not in char2tok:
                if start - 1 in char2tok:
                    start = start - 1
                elif start + 1 in char2tok:
                    start = start + 1
                else:
                    break

            tok_start = char2tok[start]
            tok_end = tok_start + length
            ment_span = (tok_start, tok_end, entity_type)

            this_ments_sent = doc_tokens[tok_start].sent
            sent_id_for_this_mention = sent_to_sent_id[this_ments_sent]

            # indexing into 1 to get the list of mentions
            sent_id_to_sent[sent_id_for_this_mention][1].append(ment_span)

        sent_list = sorted(sent_id_to_sent.items(), key=lambda x: x[0])

        sent_mentions: list[tuple[Any, Any]] = [
            (sent, ments) for _, (sent, ments) in sent_list
        ]
        document["sent_mentions"] = sent_mentions
        mention_lists.append(sent_mentions)

    return annotator_docs


# def make_conll(annotations, out_path):
def make_conll(filepaths: list[str], out_path):
    def read_file(filepath: str):
        path_prefix = "../data/raw_annotations/"
        annotated_docs: list[dict] = []
        with open(path_prefix + filepath, "r", encoding="utf8") as f:
            for doc_line in f:
                data = json.loads(doc_line)
                data["data"] = unidecode(data["data"])
                annotated_docs.append(data)
        return annotated_docs

    three_list_of_dicts: list[list[dict]] = [read_file(f) for f in filepaths]

    metadata = []

    with open(METAFILE, encoding="utf8") as f:  # read in file with metadata
        for line in f:
            metadata = json.loads(line)

    orig_id_to_date = {(md["id"], get_date(md["review_url"])) for md in metadata}
    sorted_dates = sorted(orig_id_to_date, key=lambda y: y[1])
    sorted_dates = [sd[0] for sd in sorted_dates]

    data_with_metadata = defaultdict(
        # the value for each anno_id is a list of sentences containing conll tags
        lambda: defaultdict(dict, {k: [] for k in (0, 1, 2, "tokens")})
    )

    # for each annotator's list of annotated docs, match the documents and write them in conll format
    for annotator_id, annotation in enumerate(three_list_of_dicts):
        # dictionary mapping sent_id to sentence, mentions
        tok_level_anno = char_to_tokens(annotation)

        for (
            doc
        ) in tok_level_anno:  # annotation: list of dictionaries (each dict is one doc)
            meta_doc = match_meta(doc, metadata)
            doc_id = meta_doc["id"]

            sents = [[tok.text for tok in sentence] for sentence, _ in doc["sent_mentions"]]
            all_sent_tags = [encode_bio(sentence, mentions) for sentence, mentions in doc["sent_mentions"]]

            data_with_metadata[doc_id]["tokens"] = sents
            data_with_metadata[doc_id][annotator_id] = all_sent_tags

    data_list = [(orig_id, data_with_metadata[orig_id]) for orig_id in sorted_dates]

    with open(out_path, "w", encoding="utf8") as conll_f:
        for document_id, doc_dict in data_list:
            print(DOCSTART, file=conll_f)
            for sent_id, sent in enumerate(doc_dict["tokens"]):
                for tok_id, tok in enumerate(sent):
                    if tok != " ":
                        token_line = [tok]
                        for ann_id in range(3):
                            if doc_dict[ann_id]:
                                token_line.append(doc_dict[ann_id][sent_id][tok_id])
                            else:
                                token_line.append("None")
                        token_line = " ".join(token_line)
                        print(token_line, file=conll_f)
                print("", file=conll_f)  # print a newline after each sentence


def main():
    make_conll(FILES, "../all_annotations.txt")


if __name__ == "__main__":
    main()
