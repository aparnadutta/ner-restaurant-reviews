from bs4 import BeautifulSoup
import re
import json
import os


# Extract the text of the review
def find_review(bs):
    # All reviews have the main text contained in paragraph elements of a
    # particular class

    tag_searches = [("p", re.compile("css-g5piaz evys1bk0"))]

    # patterns from original code (2018)
    # tag_searches = [('p', re.compile('css-xhhu0i e2kc3sl0')),
    #                 ('p', re.compile('story-body-text story-content')),
    #                 ('p', re.compile('css-1i0edl6'))]
    for (tag, regex) in tag_searches:
        result = bs.find_all(tag, {"class": regex})
        if len(result) > 0:
            review_text = ""
            for p in result:
                review_text += p.get_text()
            review_text = re.sub(r"\s+", " ", review_text)
            smart_double_quote = r"[\u201c\u201d\u201e\u201f\u2033\u2036]"
            review_text = re.sub(smart_double_quote, '"', review_text)
            review_text = re.sub(r"[\u2019]", "'", review_text)
            review_text = re.sub(r"\u2014", "--", review_text)
            return review_text
    # Return EMPTY if review text cannot be found
    return "EMPTY"


# Extract the rating from the review
def find_stars(bs):
    # Newer reviews have the rating set off from the story in special html tag.
    # Find those first
    tag_searches = [
        ("span", re.compile("ReviewFooter-stars")),
        ("div", re.compile("ReviewFooter-rating")),
        ("li", re.compile("critic-star-rating")),
        ("li", re.compile("critic-word-rating")),
    ]
    for (tag, regex) in tag_searches:
        result = bs.find_all(tag, {"class": regex})
        if len(result) > 0:
            text = result[0].get_text()
            stars = re.sub(r"\s+", " ", text).strip()
            if stars in ["Satisfactory", "Fair", "Poor"]:
                return stars
            else:
                return str(len(stars))

    # Older stories have the rating just sitting in a plain paragraph - search
    # separately for them
    direct_search = re.search("<p.*?>\s*★+\s*</p>", str(bs))
    if direct_search:
        just_stars = re.search("★+", direct_search.group()).group()
        return str(len(just_stars))
    if re.search("<p.*?>\s*[Ss]atisfactory\s*</p>", str(bs)):
        return "Satisfactory"
    if re.search("<p.*?>\s*[Ff]air\s*</p>", str(bs)):
        return "Fair"
    if re.search("<p.*?>\s*[Pp]oor\s*</p>", str(bs)):
        return "Poor"

    # Return 'NA' if a rating can't be found
    return "NA"


# Extract the number of recommended dishes in the review
def find_rec_dishes(bs):
    # Newer reviews have recommended dishes set off from the story in special
    # html tag.
    rec_dish_text = ""

    scripts = bs.find_all("script")
    for script in scripts:
        if "preloadedData" in script.text:
            jsonStr = script.text.split("=", 1)[
                1
            ].strip()  # remove "window.__preloadedData = "
            jsonStr = jsonStr.rsplit(";", 1)[0]  # remove trailing ;
            jsonStr = re.sub(re.compile("undefined"), '"undefined"', jsonStr)
            jsonStr = json.loads(jsonStr)

    for key, value in jsonStr["initialState"].items():
        try:
            if value["recommendedDishes"] != "":
                rec_dish_text = value["recommendedDishes"]
        except:
            continue

    # Return a list of recommended dishes.
    if ";" in rec_dish_text:
        rec_dish_list = re.split("; |\. ", rec_dish_text)
    else:
        rec_dish_list = re.split(",", rec_dish_text)

    if rec_dish_list == [""]:
        return 0  # Return 0 if recommended dish list can't be found
    else:
        return rec_dish_list


# Convert numeric price to price category - categories here are an approximate
# guess, there appears to be no official guide
def price_to_category(price):
    if price < 25:
        return 1
    elif price < 50:
        return 2
    elif price < 100:
        return 3
    else:
        return 4


# Extract the price rating in the review
def find_price(bs):
    # Newer reviews have price set off from the story in special html tag.
    tag_searches = [
        ("dd", "class", "price"),
        ("span", "itemprop", re.compile("[Pp]rice[Rr]ange")),
    ]
    price_text = ""
    for (tag, property, regex) in tag_searches:
        result = bs.find_all(tag, {property: regex})
        if len(result) > 0:
            price_text = result[0].get_text()
            break

    # Older articles have the price in a plain paragraph tag with the format
    # roughly like
    # <p> <strong> PRICES </strong> Appetizers $10 ... </p>
    if price_text == "":
        regex = re.compile(r"PRICES\s*</strong>(.*?)</p>", flags=re.DOTALL)
        price_text = re.search(regex, str(bs)).group(1)

    # Read price description and get the dollar sign rating
    # First, search for price that's of he form $, $$, $$$, etc
    dollar_regex = re.compile("(\$+)\s")
    dollarsigns = re.search(dollar_regex, price_text)
    if dollarsigns:
        return len(dollarsigns.group(1))
    else:
        # In this case, prices are described as "apps $5-17, entrees $45",
        # instead of with a summary rating. We extract the actual prices,
        # as integers, and guess at the price category from the largest price
        price_regex = re.compile("(?<=[-\$])[0-9]+")
        list_of_prices = re.findall(price_regex, price_text)
        if list_of_prices:
            max_price = max(map(int, list_of_prices))
            return price_to_category(max_price)
        else:
            return 0  # Return 0 if prices can't be found


# Simple function to read a review from disk and parse it using BeautifulSoup
def get_review(counter):
    with open("./updated_reviews/review" + str(counter) + ".html", "r") as file:
        parsed = BeautifulSoup(file, "html.parser", from_encoding="utf-8")
    return parsed


# Main loop to read all reviews obtained using the review_fetcher.py script
# TODO the HTML for ratings, prices, recommended foods has changed.
#  Do we need this? If so, we will need to figure out which html class they are in now.
if __name__ == "__main__":
    with open("../updated_reviews/url_list.txt", "r") as url_file:
        urls = json.load(url_file)

    cleaned_reviews = []
    unprocessed_URLS = []
    total = len(urls)

    for counter, review_url in enumerate(urls):
        # Progress Counter
        print("Completed {0:3d}/{1}".format(counter, total))
        parsed = get_review(counter)
        try:
            rec_dishes = find_rec_dishes(parsed)
        except json.decoder.JSONDecodeError:
            rec_dishes = []
        restaurant_info = {
            "id": counter,
            "review_url": review_url,
            "review_text": find_review(parsed),
            "rec_dishes": rec_dishes,
        }
        cleaned_reviews.append(restaurant_info)
        # else:
        #     print("NA review parse:\n", find_review(parsed))
        #     unprocessed_URLS.append(review_url)
    print("Completed {0:3d}/{0}".format(total))

    # There are still some articles for which we can't find a star rating.
    # The list of such articles is saved here. It ends up being short enough
    # to inspect by hand and see that none of these articles are real reviews
    # with stars
    os.makedirs("../updated_data", exist_ok=True)
    with open("../updated_data/unprocessed_URLs.txt", "w") as outfile:
        for url in unprocessed_URLS:
            outfile.write(url + "\n")

    # Save cleaned reviews for further analysis
    with open("../updated_data/cleaned_reviews.json", "w") as outfile:
        json.dump(cleaned_reviews, outfile)
