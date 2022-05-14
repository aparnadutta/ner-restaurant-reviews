DOCSTART = "-DOCSTART-"
OUTSIDE = "O"
DELIM = " "
EMPTY = "None"


def load_all_documents(in_filepath) -> list[list[str]]:
    all_docs = []
    num_docs = 0

    with open(in_filepath, "r") as input_file:
        doc = []

        for line in input_file:
            if line != "\n":
                tok, tag = line.strip().split(" ")
                if tok == DOCSTART:
                    if num_docs > 0:
                        all_docs.append(doc)
                    num_docs += 1
                    doc = [DOCSTART + DELIM + OUTSIDE]
                else:
                    doc.append(DELIM.join((tok, tag)))
            else:
                doc.append("")
        if len(doc) > 1:
            all_docs.append(doc)
    return all_docs


def write_splits(documents: list[list[str]]):
    train = documents[0:70]
    dev = documents[70:80]
    test = documents[80:90]

    def write_file(filename, data_split):
        with open(filename, "w") as out_f:
            for doc in data_split:
                for line in doc:
                    out_f.write(line + "\n")

    write_file("../data/final_data_splits/train.txt", train)
    write_file("../data/final_data_splits/dev.txt", dev)
    write_file("../data/final_data_splits/test.txt", test)


if __name__ == '__main__':
    docs = load_all_documents("../data/adjudicated_annotations.txt")
    write_splits(docs)
