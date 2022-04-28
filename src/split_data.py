# I want to split to make from previous index to current index when i hit a docstart and I am above 1000 lines
import os

DIRECTORY = 'annotations_split'


def main():
    with open("all_annotations_replace_none.txt", "r") as read_file:
        start_index, end_index = 0, 0
        for i, line in enumerate(read_file):
            if line.startswith("-DOCSTART-"):
                end_index = i
            if end_index - start_index > 1000:
                start_index = end_index
            with open(f"{DIRECTORY}/annotation_{str(start_index + 1)}.txt", "a") as write_file:
                write_file.write(line)


if __name__ == '__main__':
    os.makedirs(DIRECTORY)
    main()
