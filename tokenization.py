import json
import stanza
from typing import NamedTuple, List, Dict, Sequence

OUTSIDE = "O"
BEGIN = "B"
INSIDE = "I"
DELIM = "-"

PUNCT = {",", ".", ";", ")", ":"}

# TODO: if using stanza for the first time, uncomment this line
# stanza.download('en')
nlp = stanza.Pipeline(lang="en", processors="tokenize")


class Mention(NamedTuple):
    tag: str
    start: int
    end: int


def read_file(filename: str) -> dict:
    with open(filename, "r") as f:
        for line in f:
            data = json.loads(line)
    return data


# def encode_bio(tokens: list[tuple[str, int]], mentions: list[Mention]) -> list[str]:
#     """Outputs a list of the BIO tags"""
#     encoded_list = []
#     m_num = 0  # The index of the mention in the mentions list
#     for word, i in tokens:
#         if m_num < len(mentions):
#             current_mention = mentions[m_num]
#             if i == current_mention.start:
#                 encoded_list.append(BEGIN + DELIM + current_mention.tag)
#             elif current_mention.start < i < (current_mention.end - 1):
#                 encoded_list.append(INSIDE + DELIM + current_mention.tag)
#             elif i == (current_mention.end - 1):
#                 encoded_list.append(INSIDE + DELIM + current_mention.tag)
#                 m_num += 1
#             else:
#                 encoded_list.append(OUTSIDE)
#         else:
#             encoded_list.append(OUTSIDE)
#     return encoded_list


def encode_bio(tokens: Sequence[str], mentions: Sequence[Mention]) -> list[str]:
    labels = [OUTSIDE] * len(tokens)

    for entity_type, start, end in mentions:
        labels[start] = BEGIN + DELIM + entity_type
        for idx in range(start + 1, end):
            labels[idx] = INSIDE + DELIM + entity_type

    return labels


def create_tok_mention(
    label: tuple[str, str, str], tok_list: list[tuple[str, int, int]], text: str
) -> Mention:
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
            # print(text[start:end])
            # print(mention)
            return mention
        else:
            i += 1


class Token(NamedTuple):
    text: str
    start_char: int
    end_char: int
    idx: int


class CharLabel(NamedTuple):
    label: str
    start: int
    end: int


class SentenceBuilder:
    """
    Mutable class to build up a sentence and it's labels.
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.start_char = tokens[0].start_char
        self.end_char = tokens[-1].end_char
        self.char_labels: List[CharLabel] = []
        self.token_labels: List[Mention] = []

    def create_sentence_level_mentions(self):
        """
        In place creates token-level labels (Mentions) using char_labels and tokens.
        """
        # Build a map from character index to token
        char_to_token = {
            char_idx: None for char_idx in range(self.start_char, self.end_char)
        }
        for token in self.tokens:
            for token_char_idx in range(token.start_char, token.end_char):
                char_to_token[token_char_idx] = token
        # Lookup the tokens that are in the character offsets, deduplicate with set
        for char_label in self.char_labels:
            token_set = set()
            for char_label_idx in range(char_label.start, char_label.end):
                # TODO: if you want to handle these differently
                #   There's a chance docano and stanza have different
                #    understanding of character offsets
                if char_label_idx in char_to_token:
                    token_set.add(char_to_token[char_label_idx])
                else:
                    print(f"Warning: Mention {char_label} spans a sentence break")
                    print([token.text for token in self.tokens])
                    print("Sent offsets", self.start_char, self.end_char)
                    print("Continuing with a partial mention labeled\n")
            # Remove Nones from non token chars like whitespace and sort
            mention_tokens: List[Token] = sorted(
                [token for token in token_set if token is not None], key=lambda x: x.idx
            )
            if mention_tokens:
                self.token_labels.append(
                    Mention(
                        char_label.label,
                        mention_tokens[0].idx,
                        mention_tokens[-1].idx + 1,
                    )
                )

    def build(self):
        """
        Return immutable version of Mentions for a sentence.
        """
        return tuple(self.token_labels)


def tokens_from_spacy(tokenized_text) -> List[List[Token]]:
    sents = []
    for sent in tokenized_text.sentences:
        tokens = []
        for idx, token in enumerate(sent.tokens):
            tokens.append(Token(token.text, token.start_char, token.end_char, idx))
        sents.append(tokens)
    return sents


def sentence_level_mentions(
    sentence_tokens: List[List[Token]], labels: tuple[str, str, str]
):

    sent_builders = [SentenceBuilder(tokens) for tokens in sentence_tokens]
    char_idx_to_sent: Dict[int, SentenceBuilder] = {
        char_idx: sent_builder
        for sent_builder in sent_builders
        for char_idx in range(sent_builder.start_char, sent_builder.end_char)
    }

    for label in labels:
        start, end, tag = label
        char_label = CharLabel(tag, int(start), int(end))
        # Assume the char idx end of the label is in the sentence
        # If this fails try looking for the start index being in the sentence
        if char_label.end in char_idx_to_sent:
            char_idx_to_sent[char_label.end].char_labels.append(char_label)
        elif char_label.start in char_idx_to_sent:
            char_idx_to_sent[char_label.start].char_labels.append(char_label)
        else:
            print(
                f"Warning: Couldn't find a sentence for character based label: {CharLabel}\n"
            )

    for sent_builder in sent_builders:
        sent_builder.create_sentence_level_mentions()

    return [sent_builder.build() for sent_builder in sent_builders]


def process_annotations(annotation: dict) -> list[list[tuple[str, str]]]:
    """Changes mention types from character based to token based and
    outputs a list with the token, a space, and the tag"""
    encoded_text = []
    text, labels = annotation["data"], annotation["label"]
    labels.sort(key=lambda a: a[0])
    # text = text.encode("ascii", "replace").decode()
    tokenized_text = nlp(text)

    sentence_tokens = tokens_from_spacy(tokenized_text)
    mentions_by_sents = sentence_level_mentions(sentence_tokens, labels)

    # encoded_text = []
    # tok_list = []
    # index = 0
    # sentence_list = []
    # # print("*****************************")
    # # determine spans for each token in each sentence
    # for sentence in tokenized_text.sentences:
    #
    #     sentence_toks = []
    #     for tok in sentence.tokens:
    #         token_span = tok.text, tok.start_char, tok.end_char
    #         tok_list.append(token_span)
    #         sentence_toks.append((token_span[0], index))
    #         index += 1
    #     sentence_list.append(sentence_toks)
    #
    # mention_list = []
    # for label in labels:
    #     # for each mention, create a token based mention
    #     mention_list.append(create_tok_mention(label, tok_list, tokenized_text.text))

    # for sent_toks in sentence_list:
    #
    #     # TODO:
    #
    #     sentence_mentions = []
    #     # match the mentions to the sentences
    #     for mention in mention_list:
    #         if sent_toks[0][1] < mention.start < sent_toks[-1][1]:
    #             sentence_mentions.append(mention)

    for sent_tokens, sentence_mentions in zip(sentence_tokens, mentions_by_sents):
        sent_toks = [token.text for token in sent_tokens]
        # bio encode them
        labels = encode_bio(sent_toks, sentence_mentions)
        encoded_sent = []
        # make a list with all of the token-tag pairs for every token
        for token, label in zip(sent_toks, labels):
            encoded_sent.append((token, label))
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
