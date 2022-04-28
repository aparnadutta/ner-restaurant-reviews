import os

INPUT_DIRECTORY = "annotations_split"
OUTPUT_DIRECTORY = "adjudicated_data"


def run_seqscore():
    for root, dirs, files in os.walk(INPUT_DIRECTORY):
        for file in files:
            if file.endswith(".txt"):
                input_file = os.path.join(root, file)
                output_file = os.path.join(OUTPUT_DIRECTORY, file)
                command = f"time seqscore adjudicate {input_file} {output_file} --input-labels BIO"
                os.system(command)


if __name__ == '__main__':
    run_seqscore()