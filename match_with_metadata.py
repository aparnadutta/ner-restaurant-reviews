import json
import sys
import re

from typing import Sequence

# BAD_STRINGS = ['Follow NYT Food on Twitter and NYT Cooking on Instagram , Facebook , YouTube and Pinterest . Get regular updates from NYT Cooking, with recipe suggestions, cooking tips and shopping advice .',
#                'Follow NYT Food on Twitter and NYT Cooking on Instagram , Facebook and Pinterest . Get regular updates from NYT Cooking, with recipe suggestions, cooking tips and shopping advice .']


def get_date(url: str) -> int:
    """Extracts date out of the url with regex"""
    pattern = re.compile(r"\/(\d{4})\/(\d{2})\/(\d{2})\/")
    url_date = pattern.search(url).group(0)
    date = int(url_date[1:5] + url_date[6:8] + url_date[9:11])
    return date


def match_meta(annotated: dict, meta: Sequence[dict]) -> dict:
    data = annotated['data']
    for mdict in meta:
        if data[10:20] == mdict['review_text'][10:20]:
            annotated['url'] = mdict['review_url']
            annotated['date'] = get_date(mdict['review_url'])
            annotated['rec_dishes'] = mdict['rec_dishes']
            annotated['id'] = int(mdict['id'])
            # annotated['data'].replace(BAD_STRINGS[0], '')  # doesn't work, to fix later?
            # annotated['data'].replace(BAD_STRINGS[1], '')
            return annotated
    raise NameError("No matches in file")


# def main():
#     filename = sys.argv[1]
#     with open('updated_data/cleaned_reviews.json', 'r', encoding='utf8') as metaf:
#         for line in metaf:
#             metadata_list = json.loads(line)
#     with open('annotated_data/' + filename, 'r', encoding='utf8') as f:
#         for line in f:
#             review = json.loads(line)
#             review_with_meta = match_meta(review, metadata_list)
#
#
# if __name__ == '__main__':
#     main()
