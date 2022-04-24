from doccano_transformer.datasets import NERDataset
from doccano_transformer.utils import read_jsonl

dataset = read_jsonl(filepath='annotated_data/aparna_week3.jsonl', dataset=NERDataset, encoding='utf-8')

with open("aparna_conll.txt", "w") as file1:
    for x in dataset.to_conll2003(tokenizer=str.split):
        print(x['data'], file=file1)
