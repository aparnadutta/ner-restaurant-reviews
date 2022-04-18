import json
import stanza
from typing import NamedTuple

OUTSIDE = '0'
BEGIN = 'B'
INSIDE = 'I'
DELIM = '_'

PUNCT = {',', '.', ';', ')', ':'}

nlp = stanza.Pipeline(lang='en', processors='tokenize')


class Mention(NamedTuple):
    tag: str
    start: int
    end: int


def read_file(filename: str) -> dict:
    with open(filename, 'r') as f:
        for line in f:
            data = json.loads(line)
    return data


def encode_bio(tokens: list[tuple[str, int]], mentions: list[Mention]) -> list[str]:
    """Outputs a list of the BIO tags"""
    encoded_list = []
    m_num = 0  # The index of the mention in the mentions list
    for word, i in tokens:
        if m_num < len(mentions):
            current_mention = mentions[m_num]
            if i == current_mention.start:
                encoded_list.append(BEGIN + DELIM + current_mention.tag)
            elif current_mention.start < i < (current_mention.end - 1):
                encoded_list.append(INSIDE + DELIM + current_mention.tag)
            elif i == (current_mention.end - 1):
                encoded_list.append(INSIDE + DELIM + current_mention.tag)
                m_num += 1
            else:
                encoded_list.append(OUTSIDE)
        else:
            encoded_list.append(OUTSIDE)
    return encoded_list


def create_tok_mention(label: tuple[str, str, str], tok_list: list[tuple[str, int, int]], text: str) -> Mention:
    start, end, tag = label
    start, end = int(start), int(end)
    if text[end] in PUNCT:
        end = end - 1
    i = 0
    start_tok = 0
    while tok_list[i][1] <= start:
        if start <= tok_list[i][1] and not start_tok:
            start_tok = i
            i += 1
        elif not start_tok:
            i += 1
    for tok in tok_list[start_tok:]:
        if end <= tok[1]:
            end_tok = i - 1
            mention = Mention(tag, start_tok, end_tok)
            print(text[start:end])
            print(mention)
            return mention
        else:
            i += 1


def process_annotations(annotation: dict) -> list[list[tuple[str, str]]]:
    """Changes mention types from character based to token based and
    outputs a list with the token, a space, and the tag"""

    text, labels = annotation['data'], annotation['label']
    labels.sort(key=lambda a: a[0])
    text = text.encode('ascii', 'replace').decode()
    tokenized_text = nlp(text)
    encoded_text = []
    tok_list = []
    index = 0
    sentence_list = []
    print("*****************************")
    # determine spans for each token in each sentence
    for sentence in tokenized_text.sentences:
        sentence_toks = []
        for tok in sentence.tokens:
            token_span = tok.text, tok.start_char, tok.end_char
            tok_list.append(token_span)
            sentence_toks.append((token_span[0], index))
            index += 1
        sentence_list.append(sentence_toks)

    mention_list = []
    for label in labels:
        # for each mention, create a token based mention
        mention_list.append(create_tok_mention(label, tok_list, tokenized_text.text))
    for sent_toks in sentence_list:
        sentence_mentions = []
        # match the mentions to the sentences
        for mention in mention_list:
            if sent_toks[0][1] < mention.start < sent_toks[-1][1]:
                sentence_mentions.append(mention)
        # bio encode them
        bio_encoded = encode_bio(sent_toks, sentence_mentions)
        tokens = [a for a, b in sent_toks]  # get just the token text for the sentence
        encoded_sent = []
        # make a list with all of the token-tag pairs for every token
        for x, y in zip(tokens, bio_encoded):
            encoded_sent.append((x, y))
        encoded_text.append(encoded_sent)
    return encoded_text


# def main():
#     filename = sys.argv[1]
#     output_text = []
#     with open(filename, 'r', encoding='utf8') as f:
#         for line in f:
#             annote = json.loads(line)
#             encoded = process_annotations(annote)
#             output_text.append(encoded)
#     with open(filename[:-6] + '_tokenized.txt', 'w', encoding='utf8') as outf:
#         for doc in output_text:
#             for sent in doc:
#                 for tok in sent:
#                     outf.write(" ".join(tok) + '\n')
#                 outf.write('\n')
#             outf.write('\n')
#
#
# if __name__ == '__main__':
#     main()
