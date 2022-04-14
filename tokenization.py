import json
import sys
import stanza

OUTSIDE = '0'
BEGIN = 'B'
INSIDE = 'I'
DELIM = '_'

PUNCT = {',', '.', ';', ')', ':'}

nlp = stanza.Pipeline(lang='en', processors='tokenize')


class ReviewSpan:

    def __init__(self, begin, end, tag, sent, doc):
        self.tag = tag
        self.sent = sent
        rawspan = doc.text[int(begin): int(end) + 1]
        self.span = nlp(rawspan)
        self.start = -10000
        self.end = -10000
        self.re_mentionize()

    def re_mentionize(self):
        """Changes the character based mention to a token based one"""
        i = 0
        while i < len(self.sent.tokens):
            span_len = self.span.num_tokens
            match = True
            for x, y in zip(self.sent.tokens[i:i + span_len], self.span.sentences[0].tokens):
                if x.text != y.text:
                    match = False
            if match:
                self.start = i
                if self.span.sentences[0].tokens[-1].text in PUNCT:
                    self.end = i + span_len - 1
                    i = i + span_len - 1
                else:
                    self.end = i + span_len
                    i = i + span_len
            else:
                i += 1


def read_file(filename: str) -> dict:
    with open(filename, 'r') as f:
        for line in f:
            data = json.loads(line)
    return data


def encode_bio(tokens: list[str], mentions: list[ReviewSpan]) -> list[str]:
    """Outputs a list of the BIO tags"""
    encoded_list = []
    m_num = 0  # The index of the mention in the mentions list
    for i, word in enumerate(tokens):
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


def process_annotations(annotation: dict) -> list[tuple]:
    """Changes mention types from character based to token based and
    outputs a list with the token, a space, and the tag"""
    id, text, labels = annotation['id'], annotation['data'], annotation['label']
    tokenized_text = nlp(text)
    encoded_text = []
    end_sent = 0
    sents = []
    for sentence in tokenized_text.sentences:
        current_sent = []
        begin_sent = end_sent
        end_sent += len(sentence.text)
        tok_dict = dict()
        index = 0
        for tok in sentence.tokens:
            tok_dict[tok] = index
            index += 1
        for entity in labels:
            start, end, tag = entity
            if start >= begin_sent and end <= end_sent:
                new_ent = ReviewSpan(int(start), int(end), tag, sentence, tokenized_text)
                current_sent.append(new_ent)
        sents.append((sentence, current_sent))
    for sent in sents:
        text, mentions = sent
        bio_encoded = encode_bio(text.tokens, mentions)
        for x, y in zip(text.tokens, bio_encoded):
            encoded_text.append(x.text + " " + y)
        encoded_text.append("")
    return encoded_text


def main():
    filename = sys.argv[1]
    output_text = []
    with open(filename, 'r', encoding='utf8') as f:
        for line in f:
            annote = json.loads(line)
            encoded = process_annotations(annote)
            output_text.append(encoded)
    with open(filename[:-6] + '_tokenized.txt', 'w', encoding='utf8') as outf:
        for doc in output_text:
            for tok in doc:
                outf.write(tok + '\n')
            outf.write('\n')


if __name__ == '__main__':
    main()
