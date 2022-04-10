import jsonlines
import os
from typing import NamedTuple, Sequence, Any


class Mention(NamedTuple):
    """An immutable mention with an entity type and start/end indices.

    Like standard slicing operations, the start index is inclusive
    and the end index is inclusive. For example, if the tokens of
    a sentence are ["Brandeis", "University", "is", "awesome"],
    an ORG mention for the first two tokens would have a start
    index of 0 and an end index of 2. Note that the length of the
    mention is simply end - start."""

    entity_type: str
    start: int
    end: int


class AnnotatedReview:
    def __init__(self, characters: str, mentions: Sequence[Mention]) -> None:
        if not characters:
            raise ValueError("No tokens provided")
        # self.chars: tuple[str, ...] = tuple(characters)
        self.chars = characters
        self.mentions: tuple[Mention, ...] = tuple(mentions)

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f"AnnotatedSentence({self.chars}, {self.mentions})"

    def __eq__(self, other: Any) -> bool:
        return (
                isinstance(other, AnnotatedReview)
                and self.chars == other.chars
                and self.mentions == other.mentions
        )

    def __hash__(self) -> int:
        raise ValueError("Don't try to hash AnnotatedSentence")


def data(path: str) -> dict[int, AnnotatedReview]:
    annotated_reviews = {}
    with jsonlines.open(path) as file:
        for line in file.iter():
            mentions = [Mention(start=int(mention[0]), end=int(mention[1]), entity_type=mention[2]) for mention in
                        line["label"]]
            review = AnnotatedReview(characters=line["data"], mentions=mentions)
            annotated_reviews[line["id"]] = review
    return annotated_reviews


def entities(annotations: dict[int, AnnotatedReview]) -> None:
    # TODO: Change to sets to see unique mentions
    mentions = {"EST": [], "TYPE": [], "LOC": [], "DISH": [], "FOOD": [], "CUISINE": [], "DIET": []}
    for review in annotations.values():
        for mention in review.mentions:
            mentions[mention.entity_type].append(review.chars[mention.start: mention.end])
    for entity_type, mentions in mentions.items():
        print(entity_type + ": " + str(len(mentions)))
        # print(entity_type)
        # print(len(mentions))
        # print(len(set(mentions)))
        # print(mentions)
        # print()


if __name__ == '__main__':
    # TODO: Argument parser for paths
    batch = data(path=os.path.join("annotated_data", "june_week1.jsonl"))
    entities(annotations=batch)
