import json
from typing import Any

import spacy
from collections import defaultdict
from data_process_utils import change_encoding, match_meta, get_date
from unidecode import unidecode

FILES = ["aparna_annotations.jsonl", "june_annotations.jsonl", "ayla_annotations.jsonl"]
# FILES = ["aparna_annotations_fixed.jsonl", "june_annotations_fixed.jsonl", "ayla_annotations_fixed.jsonl"]
PATH = "../data/annotated_data/"
METAFILE = "../data/raw_data/cleaned_reviews.json"
DOCSTART = "-DOCSTART-\t-X-\t-X-\tO\n"

nlp = spacy.load("en_core_web_sm")


# converts the char-level mentions to tok-level mentions for each document in the list of docs
def char_to_tokens(annotator_docs: list[dict]) -> list[dict]:
    # dataset = sorted(annotators_docs, key=lambda x: x['id'])

    mention_lists = []

    for document in annotator_docs:
        text = document['data']
        doc = nlp(text)
        tok_char_indices = [token.idx for token in doc]

        doc_tokens = [token for token in doc]
        document['tokens'] = doc_tokens
        char2tok = {tok_char_indices[num_toks]: num_toks for num_toks in range(len(tok_char_indices))}

        mentions = document['label']
        token_level_mentions = []

        # dict that maps sent_id to a tuple of (sentence, mentions)
        sent_id_to_sent = {sent_id: (sent, []) for sent_id, sent in enumerate(doc.sents)}

        sent_to_sent_id = {sent: sent_id for sent_id, sent in enumerate(doc.sents)}

        for mention in mentions:
            start, end, entity_type = mention
            entity = text[start:end]

            if entity[0] == ' ':
                start += 1
                entity = entity[1:]
            ment_tokens = entity.split()
            length = len(ment_tokens)

            # TODO: try this, if it doesn't work, try -1, and +1 on either end
            if start not in char2tok:
                if start-1 in char2tok:
                    start = start-1
                elif start+1 in char2tok:
                    start = start+1

            tok_start = char2tok[start]
            tok_end = tok_start + length
            ment_span = (tok_start, tok_end, entity_type)

            this_ments_sent = doc_tokens[tok_start].sent
            sent_id_for_this_mention = sent_to_sent_id[this_ments_sent]

            # indexing into 1 to get the list of mentions, for appending to
            sent_id_to_sent[sent_id_for_this_mention][1].append(ment_span)
            # sent_id_to_ment[sent_id_for_this_mention].append(ment_span)

        sent_list = sorted(sent_id_to_sent.items(), key=lambda x: x[0])

        sent_mentions: list[tuple[Any, Any]] = [(sent, ments) for _, (sent, ments) in sent_list]

        document["sent_mentions"] = sent_mentions
        mention_lists.append(sent_mentions)
        #     token_level_mentions.append(ment_span)
        # document['mentions'] = token_level_mentions
    return annotator_docs


# def make_conll(annotations, out_path):
def make_conll(filepaths: list[str], out_path):
    def read_file(filepath: str):
        path_prefix = '../data/annotated_data/'
        annotated_docs: list[dict] = []
        with open(path_prefix + filepath, 'r', encoding='utf8') as f:
            for doc_line in f:
                data = json.loads(doc_line)
                data['data'] = unidecode(data['data'])
                annotated_docs.append(data)
        return annotated_docs

    three_list_of_dicts: list[list[dict]] = [read_file(f) for f in filepaths]

    # load the metadata from cleaned_reviews.json
    metadata = []

    # TODO: remove weird characters from metadata file,
    #  this is working for now bc first 20 chars don't have weird chars
    with open(METAFILE, encoding="utf8") as f:  # read in file with metadata
        for line in f:
            metadata = json.loads(line)

    # TODO: make a list of each of the tokens and their tags for each of the people
    orig_id_to_date = {(md["id"], get_date(md["review_url"])) for md in metadata}
    sorted_dates = sorted(orig_id_to_date, key=lambda y: y[1])
    sorted_dates = [sd[0] for sd in sorted_dates]

    data_with_metadata = defaultdict(
        # the value for each anno_id is the list of conll tags, of the same len as tokens
        lambda: defaultdict(dict, {k: [] for k in (0, 1, 2, "tokens")})
    )

    # for each annotator's list of annotated docs, match the documents and write them in conll format
    for annotator_id, annotation in enumerate(three_list_of_dicts):
        # ------------- insert ethan's code ---------------------
        # dictionary mapping sent_id to sentence, mentions
        tok_level_anno = char_to_tokens(annotation)

        for doc in tok_level_anno:  # annotation: list of dictionaries (each dict is one doc)
            meta_doc = match_meta(doc, metadata)
            doc_id = meta_doc["id"]

            for sentence, mentions in doc['sent_mentions']:
                cur_mention_id = 0

                for tok_id, token in enumerate(sentence):
                    data_with_metadata[doc_id]['tokens'].append(token)

                    # TODO: we want to go through each of the tokens, and if it is before the current mention,
                    #   then add O, if it's equal to start, add B-tag, if it's != start but within token boundaries,
                    #   add I-tag.
                    #   Add empty string for all at end of sentence
                    if tok_id




            # ------------- new code above ---------------------

            # for tok_tag_row in meta_doc["data"].split("\n"):
            #     if len(tok_tag_row.split()) > 1:  # if the line contains a token and tag
            #         tok, _, _, tag = tok_tag_row.split()
            #         data_with_metadata[doc_id]["tokens"].append(tok)
            #         data_with_metadata[doc_id][annotator_id].append(tag)
            #     else:  # if the line is a DOCSTART or newline
            #         data_with_metadata[doc_id]["tokens"].append(tok_tag_row)
            #         data_with_metadata[doc_id][annotator_id].append(
            #             ""
            #         )  # append empty string to keep lists same length
            # if data_with_metadata[doc_id][annotator_id]:
            #     data_with_metadata[doc_id]["tokens"] = data_with_metadata[doc_id][
            #                                                "tokens"
            #                                            ][: len(data_with_metadata[doc_id][annotator_id])]

    data_list = [(orig_id, data_with_metadata[orig_id]) for orig_id in sorted_dates]

    with open(out_path, "w", encoding="utf8") as conll_f:
        for date, doc_dict in data_list:
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
    # annotated_files = [read_file(PATH + filename) for filename in FILES]
    # make_conll(annotated_files, "../90_UPDATED_all_annotations_notfixed.txt")
    make_conll(FILES, "../90_UPDATED_all_annotations.txt")


if __name__ == "__main__":
    main()
