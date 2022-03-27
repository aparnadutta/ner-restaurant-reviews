import spacy
from spacy.tokens import DocBin
from spacy.util import filter_spans
from tqdm import tqdm
import json


def load_data(json_filepath: str) -> dict:
    with open(json_filepath, 'r') as f:
        return json.load(f)


# TODO: After initializing model, create a config file using this command:
#       python -m spacy init fill-config base_config.cfg config.cfg
#   Then, start training with this command:
#       python -m spacy train config.cfg --output ./ --paths.train ./training_data.spacy --paths.dev ./training_data.spacy --gpu-id 0

class NERModel:
    def __init__(self, train_filepath):
        self.training_data = load_data(train_filepath)
        self.model = spacy.blank("en")  # load a new spacy model
        self.doc_bin = DocBin()  # create a DocBin object

        for training_example in tqdm(self.training_data['annotations']):
            text = training_example['text']
            labels = training_example['entities']
            doc = self.model.make_doc(text)
            ents = []
            for start, end, label in labels:
                span = doc.char_span(start, end, label=label, alignment_mode="contract")
                if span is None:
                    print("Skipping entity")
                else:
                    ents.append(span)
            filtered_ents = filter_spans(ents)
            doc.ents = filtered_ents
            self.doc_bin.add(doc)

        self.doc_bin.to_disk("training_data.spacy")  # save the docbin object


if __name__ == "__main__":
    train_filepath = ""
    model = NERModel(train_filepath)
