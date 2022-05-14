# NER for Restaurant Reviews

## Set Up Virtual Environment

```commandline
$ python3 -m venv ner-reviews
$ source ner-reviews/bin/activate
(ner-reviews) $ pip3 install -r requirements.txt
```
If you prefer [`conda`](https://docs.conda.io/en/latest/miniconda.html): 
```commandline
$ conda create -n ner-reviews python=3.9
$ conda activate ner-reviews
(ner-reviews) $ pip3 install -r requirements.txt
```

## Data

### [`html_reviews`](data/html_reviews)
This directory contains the HTML files for New York Times food reviews.
It includes [`url_list.txt`](data/html_reviews/url_list.txt) listing the corresponding URLs.

### [`raw_data`](data/raw_data)
This directory contains txt files for a processed dataset of New York Times food reviews.
It includes [`cleaned_reviews.json`](data/raw_data/cleaned_reviews.json) and [`edit_cleaned_reviews.json`](data/raw_data/edit_cleaned_reviews.json), which contain all of the processed food review data.
It includes [`unprocessed_URLs.txt`](data/raw_data/unprocessed_URLs.txt), listing any unprocessed URLs.

### [`tags.json`](data/tags.json)
This file contains entity types to import into an annotation tool.

### [`small_batch_annotation`](data/small_batch_annotation)
This directory contains the JSON files for the annotated data from the initial small batch annotation.

### [`annotated_data`](data/annotated_data)
This directory contains the JSON files for the annotated data, along with corresponding files that were corrected to remove encoding issues.

### [`all_annotations.txt`](data/all_annotations.txt)
This file contains all annotations from all annotators in CONLL format.

### [`adjudicated_annotations.txt`](data/adjudicated_annotations.txt)
This file contains adjudicated annotations in CONLL format.

### [`final_data_splits`](data/final_data_splits)
This directory contains the train, dev, and test sets for the adjudicated annotations.


## Scripts 

### [`review_fetcher.py`](src/data_scraping/review_fetcher.py)
This script downloads food reviews from New York Times and stores them in [`html_reviews`](data/html_reviews).

### [`clean_data.py`](src/data_scraping/clean_data.py)
This script processes and cleans [`html_reviews`](data/html_reviews), and outputs [`raw_data`](data/raw_data).

### [`prepare_data.py`](src/data_scraping/prepare_data.py)
This script prepares [`raw_data`](data/raw_data) for annotation.

### [`fix_encoding_issue.py`](src/fix_encoding_issue.py)
This script fixes encoding issues in [`annotated_data`](data/annotated_data).

### [`data_process_pipeline.py`](src/data_process_pipeline.py)
This script accepts [`annotated_data`](data/annotated_data) and processes the data to output [`all_annotations.txt`](data/all_annotations.txt).

### [`data_process_utils.py`](src/data_process_utils.py)
This script includes additional functions to support [`data_process_pipeline.py`](src/data_process_pipeline.py).

### [`inter_annotator_agreement.py`](src/inter_annotator_agreement.py)
This script calculates inter-annotator agreement with the processed data in [`all_annotations.txt`](data/all_annotations.txt).

### [`adjudication.py`](src/adjudication.py)
This script runs adjudication to produce gold standard annotations and outputs [`adjudicated_annotations.txt`](data/adjudicated_annotations.txt).

### [`create_train_dev_test.py`](src/create_train_dev_test.py)
This script accepts [`adjudicated_annotations.txt`](data/adjudicated_annotations.txt) and splits the data into train, dev, and test sets.

### [`NER_restaurant_reviews.ipynb`](src/NER_restaurant_reviews.ipynb)
This script runs the model and experiments using [`final_data_splits`](data/final_data_splits).
