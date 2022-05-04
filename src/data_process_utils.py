from argparse import ArgumentParser
import jsonlines
import re

from typing import Sequence, Any
from doccano_transformer.datasets import NERDataset
from doccano_transformer.utils import read_jsonl


METAFILE = "raw_data/cleaned_reviews.json"


def read_file(filepath: str) -> Any:
    """Reads the doccano output file into a dataset in conll 2003 format"""
    dataset = read_jsonl(filepath=filepath, dataset=NERDataset, encoding="utf-8")
    return dataset.to_conll2003(tokenizer=str.split)


def change_encoding(inputfile: str, outputfile: str) -> None:
    """Makes sure the encoding is in utf8"""
    with open(inputfile, "r", encoding="iso-8859-1") as in_file:
        reader = jsonlines.Reader(in_file)
        objects = [obj for obj in reader.iter(type=dict)]

    with open(outputfile, "w", encoding="utf8") as outfile:
        writer = jsonlines.Writer(outfile)
        writer.write_all(objects)


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
