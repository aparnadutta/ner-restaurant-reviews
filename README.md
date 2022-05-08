# ner-restaurant-reviews
An annotated corpus of entities in NYT Restaurant Reviews.


* src/data_process_pipeline.py -> all_annotations.txt
* src/adjudication.py -> adjudicated_annotations.txt

IGNORE +  REMOVE
* src/replace_none.py -> all_annotations_replace_none.txt
* src/split_data.py -> annotations_split
* src/run_seqscore.py -> adjudicated_data

CLEAN (JUNE)
* Above (Seqscore adjudication scripts and files)
  * Remove replace_none.py
  * Remove run_seqscore.py
  * Remove split_data.py
  * Remove all_annotations_replace_none.txt
* Make folder for adjudication?
* Write inter_annotator_agreement.py
* readable_annotations.py?
* Move txt files to data?
* Change UPDATED_all_annotations name

TO DO
* Run Seqscore count and validate
* Find out how many documents overlap between each annotator