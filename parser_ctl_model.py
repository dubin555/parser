# -*- coding: utf-8 -*-

"""
__author__ = "Bin"
__license__ = "FSL"
"""

from config import CTL_KEY_WORDS, CTL_MODEL_FILES
from EasyORM import CtlModel
import sys


def read_ctl_model(ctl_model_file,key_words):
    key_words = key_words.split(",")
    exec_sql_queue = []
    with open(ctl_model_file) as f:
        for line in f:
            temp = scan_chain_to_json(line.strip(),key_words)
            scan_chain_model = CtlModel(get_sqlite_format(temp))
            scan_chain_model.save()
    return


def get_sqlite_format(json_data):
    for k,v in json_data.items():
        if isinstance(v,list):
            json_data[k] = ",".join(v)
        elif isinstance(v,bool):
            json_data[k] = 1 if v is True else 0
    for k,v in json_data.items():
        if isinstance(v,str):
            try:
                json_data[k] = int(v)
            except ValueError as e:
                pass
    return json_data


def key_word_with_content(key_word):
    return not key_word.startswith("[") and not key_word.endswith("]")


def scan_chain_to_json(scan_chain_line, key_words):
    res = {}
    key_word_index = 0
    stack = scan_chain_line.split(" ")
    while stack:
        with_content = key_word_with_content(key_words[key_word_index])
        key_word = key_words[key_word_index].strip("[]")
        next_key_word = key_words[key_word_index + 1].strip('[]') if key_word_index + 1 < len(key_words) else "HARD_TO_FIND"
        if with_content:
            if not res.get(key_word,None):
                res[key_word] = []
            try:
                while stack[0] != "-" + key_word:
                     stack.pop(0)
                stack.pop(0)
                res[key_word].append(stack.pop(0))
                key_word_index += 1
            except Exception as e:
                print("out of index1")
                sys.exit()
        else:
            try:
                while stack[0] != "-" + key_word:
                    if stack[0] == "-" + next_key_word:
                        key_word_index += 2
                        res[key_word] = False
                        res[next_key_word] = True
                        stack.pop(0)
                        break
                    else:
                        stack.pop(0)
                if stack[0] == "-" + key_word:
                    res[key_word] = True
                    key_word_index += 1
                    stack.pop(0)
            except Exception as e:
                print("out of index")
                sys.exit()
    return res

if __name__ == "__main__":
    read_ctl_model(CTL_MODEL_FILES, CTL_KEY_WORDS)




