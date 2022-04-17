import json
import tqdm

from match_with_metadata import match_meta
from tokenization import process_annotations

FILES = ['aparna_week2.jsonl', 'june_week2.jsonl', 'ayla_week2.jsonl']  # change to week 3 when ayla finishes annotation
PATH = 'annotated_data/'
METAFILE = 'updated_data/cleaned_reviews.json'


def read_file(filename: str) -> dict:
    data = []
    with open(filename, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    return data


def make_conll(annotations: list[list[dict]]) -> None:
    print("Adding Metadata...")
    reviews = dict()
    metadata_file = read_file(METAFILE)[0]
    metadata = [r for r in metadata_file if int(r['id']) < 90]
    for d in metadata:
        reviews[d['id']] = [None, None, None]
    for i, persons_data in enumerate(annotations):
        for x in persons_data:
            meta = match_meta(x, metadata)
            reviews[meta['id']][i] = meta
    print("Tokenizing...")
    all_reviews = []
    for r_id, annotes in tqdm.tqdm(reviews.items()):
        if any(annotes):
            encoded = []
            for d in annotes:
                if d:
                    processed = process_annotations(d)
                    encoded.append(processed)
                    tokens = []
                    for s in processed:
                        slist = []
                        for x, _ in s:
                            slist.append(x)
                        tokens.append(slist)
                else:
                    encoded.append(None)
            conll_review = []
            lengths = [len(y) for y in encoded if y]
            review_len = min(lengths)
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
                for j, token in enumerate(token_sent[:sent_len]):
                    line = [token]
                    for e in e_sents:
                        if e:
                            line.append(e[j][1])
                        else:
                            line.append('None')
                    line.append('\n')
                    sentence.append(' '.join(line))
                conll_review.append(sentence)
        all_reviews.append((r_id, conll_review))
    print("Creating CONLL file...")
    with open('all_annotations.txt', 'w', encoding='utf8') as out_f:
        for r_id, doc in all_reviews:
            out_f.write(f"# DOC {r_id} \n")
            for sent in doc:
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
