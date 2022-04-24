import json
from collections import defaultdict

import tqdm
from typing import Iterable, Dict, Tuple, List, Optional

from match_with_metadata import match_meta
from tokenization import process_annotations

FILES = ['aparna_week2.jsonl', 'june_week2.jsonl', 'ayla_week2.jsonl']  # change to week 3 when ayla finishes annotation
PATH = 'annotated_data/'
METAFILE = 'updated_data/cleaned_reviews.json'


def read_file(filename: str) -> dict:
    data = []
    with open(filename, 'r', encoding="ISO-8859-1") as f:
        for line in f:
            data.append(json.loads(line))
    return data


def make_conll(annotations: list[list[dict]]) -> None:
    print("Adding Metadata...")
    reviews = dict()
    metadata_file = read_file(METAFILE)[0]
    metadata = [r for r in metadata_file if int(r['id']) < 90]  # limit it to just the reviews we did
    for d in metadata:
        # make dict for looking up the reviews by id, with space to put annotation for each of us
        reviews[d['id']] = [None, None, None]
    for i, persons_data in enumerate(annotations):  # iterate over each persons annotation data (len(annotation) = 3)
        #  i = 0 is aparna, i = 1 is june, i = 2 is ayla
        for x in persons_data:
            meta = match_meta(x, metadata)
            reviews[meta['id']][i] = meta
    # create a file for the metadata
    print("Creating Metadata file: \'all_annotations_with_metadata.json\'")
    with open('all_annotations_with_metadata.json', 'w', encoding='utf-8') as f_out:
        json.dump(reviews, f_out)
    print("Tokenizing...")

    review_list = list(reviews.items())
    review_list.sort(key= lambda y: y[0], reverse=True)
    all_reviews = []
    conll_review = []
    for r_id, annotes in tqdm.tqdm(review_list):
        if any(annotes):
            encoded = []  # len(encoded) == 3
            for d in annotes:  # iterating through each annotators annotations
                if d:
                    processed: list[list] = process_annotations(d)  # list of sentences of tokens
                    encoded.append(processed)
                    tokens = []
                    # make a list of just the tokens
                    for s in processed:
                        slist = []
                        for x, _ in s:
                            slist.append(x)
                        tokens.append(slist)
                else:
                    encoded.append(None)
            conll_review = []
            # if there are length discrepancies (trailing whitespace, etc.), take the shortest one
            lengths = [len(y) for y in encoded if y]
            review_len = min(lengths)

            # iterate through the token list
            # print(len(tokens))
            for i, token_sent in enumerate(tokens[:review_len]):
                e_sents = []
                for e in encoded:
                    if e:
                        e_sents.append(e[i])
                    else:
                        e_sents.append(None)
                sent_lens = [len(x) for x in e_sents if x]
                sent_len = min(sent_lens)
                sentence = []
                # append the labels to the token list
                # print(len(token_sent))
                for j, token in enumerate(token_sent[:sent_len]):
                    line = [token]
                    for e in e_sents:
                        if e:
                            line.append(e[j][1])
                        else:
                            line.append('None')
                    line.append('\n')
                    sentence.append('\t'.join(line))
                conll_review.append(sentence)
        all_reviews.append((r_id, conll_review))
    print("Creating CONLL file...")
    with open('all_annotations.txt', 'w', encoding='utf8') as out_f:
        for r_id, doc in all_reviews:
            # print(r_id)
            out_f.write(f"-DOCSTART-\n")
            for sent in doc:
                # print(sent)
                for line in sent:
                    out_f.write(line)
                out_f.write('\n')
            out_f.write('\n')


def get_label(
        annotatorid_to_sentences: Dict[int, Optional[list[list[tuple[str, str]]]]],
        annotator_idx: int,
        sent_idx: int,
        token_idx: int
):
    if annotatorid_to_sentences[annotator_idx] is None:
        return None
    else:
        # 1 is the label in the token, label tuple
        # print(annotatorid_to_sentences[annotator_idx][sent_idx])
        # print(annotator_idx, sent_idx, token_idx)
        return annotatorid_to_sentences[annotator_idx][sent_idx][token_idx][1]


def join_annotations(
        annotatorid_to_sentences: Dict[int, Optional[list[list[tuple[str, str]]]]]
) -> List[List[Tuple[str, str, str, str]]]:
    assumed_sents = None
    ret = []
    for annotatorid in annotatorid_to_sentences:
        if annotatorid_to_sentences[annotatorid] is not None:
            assumed_sents = annotatorid_to_sentences[annotatorid]
            break
    if not assumed_sents:
        raise ValueError("All annotations are empty")
    for sent_idx, sent in enumerate(assumed_sents):
        joined_sent = []
        try:
            for token_idx, (token, _) in enumerate(sent):
                label0 = get_label(annotatorid_to_sentences, 0, sent_idx, token_idx)
                label1 = get_label(annotatorid_to_sentences, 1, sent_idx, token_idx)
                label2 = get_label(annotatorid_to_sentences, 2, sent_idx, token_idx)
                joined_sent.append((token, label0, label1, label2))
            ret.append(joined_sent)
        except IndexError:
            print(f"Token mismatch in sentence {sent}, skipping")
            continue
    return ret


def chesters_make_conll(annotations: list[list[dict]]) -> None:
    print("Adding Metadata...")
    reviews = dict()
    metadata_file = read_file(METAFILE)[0]
    metadata = [r for r in metadata_file if
                int(r['id']) < 90]  # limit it to just the reviews we did
    for d in metadata:
        # make dict for looking up the reviews by id, with space to put annotation for each of us
        reviews[d['id']] = [None, None, None]
    for i, persons_data in enumerate(
            annotations):  # iterate over each persons annotation data (len(annotation) = 3)
        #  i = 0 is aparna, i = 1 is june, i = 2 is ayla
        for x in persons_data:
            meta = match_meta(x, metadata)
            reviews[meta['id']][i] = meta
    # create a file for the metadata
    print("Creating Metadata file: \'all_annotations_with_metadata.json\'")
    with open('all_annotations_with_metadata.json', 'w', encoding='utf-8') as f_out:
        json.dump(reviews, f_out)
    print("Tokenizing...")

    review_list = list(reviews.items())
    review_list.sort(key=lambda y: y[0], reverse=True)
    # So this is a list where each item is tuple idx of article then list of None or dict of annotation
    docid_to_sentences = defaultdict(list)
    for docid, annotations in tqdm.tqdm(review_list):
        if any(annotations):
            annotatorid_to_sentences: Dict[int, Optional[list[list[tuple[str, str]]]]] = {}
            for annotator_id, annotation in enumerate(annotations):  # iterating through each annotators annotations
                if annotation:
                    annotatorid_to_sentences[annotator_id] = process_annotations(annotation)
                else:
                    annotatorid_to_sentences[annotator_id] = None
            joined_sents: List[List[Tuple[str, str, str, str]]] = join_annotations(annotatorid_to_sentences)
            docid_to_sentences[docid].append(joined_sents)

    with open('all_annotations.txt', 'w', encoding='utf8') as out_f:
        for docid in docid_to_sentences:
            print("-DOCSTART- O O O", file=out_f)
            print(file=out_f)
            for sentences in docid_to_sentences[docid]:
                for sent in sentences:
                    for token_and_labels in sent:
                        print(" ".join([str(item) for item in token_and_labels]), file=out_f)
                    print(file=out_f)


def main():
    print("Reading in data from annotation files...")
    data = [read_file(PATH + x) for x in FILES]
    # make_conll(data)
    chesters_make_conll(data)


if __name__ == '__main__':
    main()
