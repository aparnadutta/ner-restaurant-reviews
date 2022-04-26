import json
import jsonlines
from collections import defaultdict
from data_process_utils import (
                                read_file,
                                change_encoding,
                                match_meta,
                                )

FILES = ['aparna_week3.jsonl', 'june_week3.jsonl', 'ayla_week3_utf8.jsonl']
PATH = 'annotated_data/'
METAFILE = 'updated_data/cleaned_reviews.json'
DOCSTART = '-DOCSTART- -X- -X- O\n'


def make_conll(annotations):
    metadata = []
    with open(METAFILE, encoding='utf8') as f:  # read in file with metadata
        for line in f:
            metadata = json.loads(line)

    encoded_data = []
    data_with_metadata = dict(dict())

    for i, annotation in enumerate(annotations):
        for doc in annotation:
            meta_doc = match_meta(doc, metadata)
            date = meta_doc['date']
            if date not in set(data_with_metadata.keys()):
                data_with_metadata[date] = dict()
                data_with_metadata[date][0] = []
                data_with_metadata[date][1] = []
                data_with_metadata[date][2] = []
                data_with_metadata[date]['tokens'] = []
            for x in meta_doc['data'].split('\n'):
                if len(x.split()) > 1:
                    # print(x, x.split()[0], x.split()[-1])
                    data_with_metadata[date]['tokens'].append(x.split()[0])
                    data_with_metadata[date][i].append(x.split()[-1])
                else:
                    data_with_metadata[date]['tokens'].append(x)
                    data_with_metadata[date][i].append('')
            if data_with_metadata[date][i]:
                data_with_metadata[date]['tokens'] = data_with_metadata[date]['tokens'][:len(data_with_metadata[date][i])]
            # print(data_with_metadata[date]['tokens'])
            # print(data_with_metadata[date][0])
            # print(data_with_metadata[date][1])
            # print(data_with_metadata[date][2])
            # data_text = [x.split()[0] for x in meta_doc['data'].split('\n') if x else ]
            # data_with_metadata[date][i] = meta_doc

            # data_with_metadata[meta_doc['date']].append((i, meta_doc))
    data_list = list(data_with_metadata.items())
    data_list.sort(key=lambda y: y[0])
    trimmed_data_list = []
    for date, doc_dic in data_list:
        empty_sum = 0
        for x in doc_dic.values():
            if not x:
                empty_sum += 1
        if empty_sum == 1:
            trimmed_data_list.append((date, doc_dic))
    with open("all_annotations.txt", 'w', encoding='utf8') as conll_f:
        for date, doc_dict in trimmed_data_list:
            # print(date, doc_dict['tokens'], file=conll_f)
            # print(date, doc_dict[0], file=conll_f)
            # print(date, doc_dict[1], file=conll_f)
            # print(date, doc_dict[2], file=conll_f)
            # print(doc_dict['tokens'])
            for i, tok in enumerate(doc_dict['tokens']):
                # print(tok, file=conll_f)
                token_line = [tok]
                # if doc_dict[0]:
                #     print(doc_dict[0][i], file=conll_f)
                # if doc_dict[1]:
                #     print()
                #     print(doc_dict[1][i], file=conll_f)
                # if doc_dict[2]:
                #     print(doc_dict[2][i], file=conll_f)
                for j in range(3):
                    # print(doc_dict[j])
                    if doc_dict[j]:
                        # print(doc_dict[j][i], file=conll_f)
                        if tok == '-DOCSTART-':
                            token_line.append("-X-")
                        elif tok:
                            token_line.append(doc_dict[j][i])
                        else:
                            token_line.append("")
                    # elif doc_dict[j] and i < len(doc_dict[j]):
                    #     # print(i, tok, len(doc_dict[j]), doc_dict[j][i])
                    #     token_line.append(doc_dict[j][i])
                    else:
                        # print(doc_dict[j], file=conll_f)
                        if tok == '-DOCSTART-':
                            token_line.append('-X-')
                        elif tok:
                            token_line.append('N/A')
                        else:
                            token_line.append('')

                        # print(i, tok, doc_dict.keys(), token_line)
                # print(token_line, file=conll_f)
                token_str = ' '.join(token_line)
                print(token_str, file=conll_f)
    # #     document_data = dict()
    # #     for annotation in doc:
    # #         i, data = annotation
    # #         tok_list = []
    # #         for token in data.split('\n'):
    # #             if token != DOCSTART[:-2]:
    # #                 if token:
    # #                     tok_ = token.split()
    # #                     tok_list.append((tok_[0], tok_[-1]))
    # #         document_data[i] = tok_list
    # #     for annotator in range(3):
    # #         if


def main():
    # utf_encode = '_utf8.jsonl'
    # generate the names for the outfiles
    # outfiles = [filename[:6] + utf_encode for filename in FILES]
    # change the encoding for each file and create the properly encoded file
    # change_encoding(PATH+FILES[2], PATH+FILES[2][:-6] + utf_encode)
    # [change_encoding(PATH + infile, PATH + outfile) for infile, outfile in zip(FILES, outfiles)]
    # read in the properly encoded files
    annotations = [read_file(PATH + filename) for filename in FILES]
    # annotations.append(read_file(PATH+outfiles[2]))
    make_conll(annotations)


if __name__ == '__main__':
    main()
