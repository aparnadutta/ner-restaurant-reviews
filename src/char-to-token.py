import json
import spacy
import re


def print_type(item):
    print(type(item))


def join_lines(filename):
    with open(filename, 'r', encoding='utf8') as f:
        data = [json.loads(line) for line in f]
        return data


def fix_with_regex(data: str) -> str:
    pattern = re.compile(r'[^\x00-\x7F]')
    data = re.sub(pattern, '_', data)
    return data


def char_to_tokens() -> dict:
    dataset = join_lines('../data/annotated_data/aparna_annotations.jsonl')
    dataset = sorted(dataset, key=lambda x: x['id'])

    nlp = spacy.load("en_core_web_sm")

    for sentence in dataset:
        ID = sentence['id']
        text = sentence['data']
        # print(text)
        text = fix_with_regex(text)
        # print(text)
        doc = nlp(text)
        # print(len(doc.text))
        # print(len(text))
        for sent in doc.sents:
            print(sent, '<end_sentence>')
        indices = [token.idx for token in doc]
        # [print(token.idx, token.text) for token in doc]

        # print(indices)
        sentence_tokens = [str(token) for token in doc]
        sentence['tokens'] = sentence_tokens
        char2tok = {indices[n]: n for n in range(len(indices))}
        # print(char2tok)
        # print(len(indices))
        mentions = sentence['label']
        token_level_mentions = []
        for mention in mentions:
            # print(mention)
            start, end, entity_type = mention
            entity = text[start:end]
            # print(etity)
            # print(doc.text[start:end])
            if entity[0] == ' ':
                start += 1
                entity = entity[1:]
            # print(entity)
            tokens = entity.split()
            # print(tokens)
            length = len(tokens)
            tok_start = char2tok[start]
            tok_end = tok_start + length
            token_level_mentions.append([tok_start, tok_end, entity_type])
        sentence['mentions'] = token_level_mentions
        # print(len(mentions), len(token_level_mentions))
        return dataset

with open('token_level.json', 'w', encoding='utf8') as file:
    json.dump(dataset, file, indent=4)
