import json
import tqdm
from typing import Iterable

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


def main():
    print("Reading in data from annotation files...")
    data = [read_file(PATH + x) for x in FILES]
    make_conll(data)


if __name__ == '__main__':
    main()
