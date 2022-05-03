DOCSTART = "-DOCSTART-"


def remove_newlines(in_path):
    path_prefix = "../data/final_data_splits/"
    inp_path = path_prefix+in_path
    out_path = path_prefix+"no_newline_"+in_path

    with open(inp_path, "r") as input_file, open(out_path, "w") as output_file:
        for line in input_file:
            if line != "\n":
                tok, lab = line.strip().split(" ")
                if tok == DOCSTART:
                    print("", file=output_file)
                    print(line, file=output_file)
                else:
                    print(line.strip(), file=output_file)


if __name__ == '__main__':
    remove_newlines("train.txt")
    remove_newlines("dev.txt")
    remove_newlines("test.txt")


