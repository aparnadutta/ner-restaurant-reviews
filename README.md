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

### [`annotated_data`](data/annotated_data)

### [`final_data_splits`](data/final_data_splits)

### [`html_reviews`](data/html_reviews)

### [`raw_data`](data/raw_data)

### [`small_batch_annotation`](data/small_batch_annotation)

### [`adjudicated_annotations.txt`](data/adjudicated_annotations.txt)

### [`all_annotations.txt`](data/all_annotations.txt)

### [`tags.json`](data/tags.json)



## Scripts 

### [`clean_data.py`](src/data_scraping/clean_data.py)

### [`prepare_data.py`](src/data_scraping/prepare_data.py)

### [`review_fetcher.py`](src/data_scraping/review_fetcher.py)

### [`adjudication.py`](src/adjudication.py)

### [`create_train_dev_test.py`](src/create_train_dev_test.py)

### [`data_process_pipeline.py`](src/data_process_pipeline.py)

### [`data_process_utils.py`](src/data_process_utils.py)

### [`doccano_transformer_examples.py`](src/doccano_transformer_examples.py)

### [`fix_encoding_issue.py`](src/fix_encoding_issue.py)

### [`inter_annotator_agreement.py`](src/inter_annotator_agreement.py)

### [`NER_restaurant_reviews.ipynb`](src/NER_restaurant_reviews.ipynb)

### [`run_seqscore.py`](src/run_seqscore.py)



