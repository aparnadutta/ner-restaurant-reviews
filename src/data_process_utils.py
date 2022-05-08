from argparse import ArgumentParser
import jsonlines
import re

from typing import Sequence, Any
from doccano_transformer.datasets import NERDataset
from doccano_transformer.utils import read_jsonl


METAFILE = "raw_data/cleaned_reviews.json"
BEGIN = "B"
INSIDE = "I"
OUTSIDE = "O"
DELIM = "-"


def read_file(filepath: str) -> Any:
    """Reads the doccano output file into a dataset in conll 2003 format"""
    dataset = read_jsonl(filepath=filepath, dataset=NERDataset, encoding="utf-8")
    return dataset.to_conll2003(tokenizer=str.split)


def encode_bio(spacy_sent: Sequence[str], mentions: Sequence[tuple]) -> list[str]:
    # sent_length = spacy_sent.end - spacy_sent.start
    sent = [tok.text for tok in spacy_sent]
    sent_length = len(sent)
    token_offset = spacy_sent.start
    labels = [OUTSIDE] * sent_length
    for mention in mentions:
        ment_start, ment_end, ment_type = mention

        doc_mention = spacy_sent[0].doc[ment_start:ment_end]
        ment_start = ment_start - token_offset
        ment_end = ment_end - token_offset

        assert ment_start >= 0, f"Bad mention start: {ment_start}"
        assert ment_end > 0, f"Bad mention end: {ment_end}"
        assert ment_start <= ment_end, f"Bad mention indices, start: {ment_start}, end: {ment_end}\n Mention: {mention}\n Sentence: {sent}"
        assert ment_start < sent_length, f"Mention start greater than sent_len, start: {ment_start}, sent_len: {sent_length}"
        assert ment_end <= sent_length, f"Mention end greater than sent_len, end: {ment_end}, sent_len: {sent_length} \n Mention: {mention}\n Sentence: {sent}\nDoc_mention: {doc_mention}"

        labels[ment_start] = BEGIN + DELIM + ment_type
        for i in range(ment_start + 1, ment_end):
            labels[i] = INSIDE + DELIM + ment_type
    return labels


def get_date(url: str) -> int:
    """Extracts date out of the url with regex"""
    pattern = re.compile(r"\/(\d{4})\/(\d{2})\/(\d{2})\/")
    url_date = pattern.search(url).group(0)
    date = int(url_date[1:5] + url_date[6:8] + url_date[9:11])
    return date


def match_meta(annotated: dict, meta: Sequence[dict]) -> dict:
    data = annotated["data"]
    for mdict in meta:
        if data[1:20] == mdict["review_text"][1:20]:
            annotated["url"] = mdict["review_url"]
            annotated["date"] = get_date(mdict["review_url"])
            annotated["rec_dishes"] = mdict["rec_dishes"]
            annotated["id"] = int(mdict["id"])
            return annotated
    raise NameError("No matches in file")
