def main():
    with open("all_annotations.txt", "r") as file1, open(
        "all_annotations_replace_none.txt", "w"
    ) as file2:
        for line in file1:
            file2.write(line.replace("N/A", "O"))


if __name__ == "__main__":
    main()
