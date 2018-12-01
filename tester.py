from autocomplete_engines import LetterAutocompleteEngine, SentenceAutocompleteEngine, MelodyAutocompleteEngine
from prefix_tree import SimplePrefixTree, CompressedPrefixTree
from typing import Union
import string
import random
import math
import csv
from autocomplete_engines import SentenceAutocompleteEngine, LetterAutocompleteEngine


def sorted_test(tree) -> bool:
    last_weight = tree.subtrees[0].weight if len(tree.subtrees) > 0 else 0
    valid = True
    for subtree in tree.subtrees:
        if subtree.weight > last_weight:
            valid = False
        last_weight = subtree.weight
        sub_valid = sorted_test(subtree)
        if not sub_valid:
            valid = False
    return valid


def compressed_test_inactive(tree) -> bool:
    num_non_leaves = len([x for x in tree.subtrees if not x.is_leaf()])
    num_leaves = len(tree.subtrees) - num_non_leaves
    if num_leaves > 0 or num_non_leaves >= 2 or tree.is_leaf():
        valid = True
    else:
        valid = False
    for subtree in tree.subtrees:
        sub_valid = compressed_test(subtree)
        if not sub_valid:
            valid = False
    return valid


def compressed_test(tree) -> bool:
    num_non_leaves = len([x for x in tree.subtrees if not x.is_leaf()])
    num_leaves = len(tree.subtrees) - num_non_leaves
    valid = True
    if num_leaves == 0 and num_non_leaves < 2 and not tree.is_leaf():
        valid = False
    for subtree in tree.subtrees:
        sub_valid = compressed_test(subtree)
        if not sub_valid:
            valid = False
    return valid


def same_value_subtree_test(tree) -> bool:
    valid = True
    for subtree in tree.subtrees:
        if subtree.value == tree.value:
            valid = False
            print(f"Current Value: {tree.value}")
            for subtree in tree.subtrees:
                print(f"Subtree value: {subtree.value}")
        if not same_value_subtree_test(subtree):
            valid = False
    return valid


def autocomplete_test(tree, sentence: bool=False) -> bool:
    leaves = tree._get_all_leaves(None)
    for i in range(len(leaves) // 2):
        leaf = leaves[random.randint(0, len(leaves)-1)]
        phrase = leaf[0]
        if sentence:
            full_prefix = phrase.split(" ")
            prefix = full_prefix[:math.ceil(len(full_prefix) / 2)]
        else:
            prefix = phrase[:math.ceil(len(phrase) / 5)]
        complete = tree.autocomplete(list(prefix))
        if len(complete) == 0:
            print(f"Something went wrong with {prefix}")
        else:
            last_weight = complete.pop(0)[1]
            for next in complete:
                if next[1] > last_weight:
                    return False
    return True


def random_insert(tree: Union[CompressedPrefixTree, SimplePrefixTree]) -> list:
    all_strings = []
    for i in range(500):
        string_builder = ""
        for j in range(random.randint(5, 15)):
            string_builder += random.choice(string.ascii_letters)
        tree.insert(string_builder, random.randint(1, 100), list(string_builder))
        all_strings.append(string_builder)
    for elem in random.choices(all_strings, k=len(all_strings)//4):
        for i in range(random.randint(3, 10)):
            tree.insert(elem, random.randint(1, 100), list(elem))
    return all_strings


def random_delete(tree: Union[CompressedPrefixTree, SimplePrefixTree], prefixes: list, number: int) -> list:
    deleted_strings = []
    for i in range(number):
        to_delete = prefixes[random.randint(0, len(prefixes)-1)]
        tree.remove(list(to_delete))
        deleted_strings.append(to_delete)
    return deleted_strings


def file_insert(tree: Union[CompressedPrefixTree, SimplePrefixTree], file):
    with open(file, encoding='utf8') as f:
        for line in f:
            new_line = ""
            for ch in line:
                if ch.isalnum() or ch == " ":
                    new_line += ch
            new_line = new_line.lower()
            tree.insert(new_line, 1, list(new_line))


def get_tree_creator(weight_type: str, compressed: bool=True):
    if compressed:
        return lambda: CompressedPrefixTree(weight_type)
    else:
        return lambda: SimplePrefixTree(weight_type)


def gen_letter_tree(compressed, file):
    engine = LetterAutocompleteEngine({
        # NOTE: you should also try 'data/google_no_swears.txt' for the file.
        'file': file,
        'autocompleter': 'simple' if not compressed else "compressed",
        'weight_type': 'sum'
    })
    print(
        f"{'Simple' if not compressed else 'Compressed'} tree -\nSorted: {sorted_test(engine.autocompleter)}\nFully Compressed: {compressed_test(engine.autocompleter)}\nFree of SVS: {same_value_subtree_test(engine.autocompleter)}\n")
    return engine.autocompleter


def check_all_inserted_letter(compressed):
    def mapper(x):
        return x[0]
    file = 'data/lotr.txt'
    autocompleter = gen_letter_tree(compressed, file)
    correct = []
    incorrect = []
    wrong_count = 0
    right_count = 0
    with open(file, encoding='utf8') as f:
        for line in f:
            new_line = ""
            num_alnum = 0
            for ch in line:
                if ch.isalnum():
                    new_line += ch
                    num_alnum += 1
                if ch == " ":
                    new_line += ch
            if num_alnum > 0:
                new_line = new_line.lower()
                prefix = new_line[:math.ceil(len(new_line)/2)]
                choices = map(mapper, autocompleter.autocomplete(list(prefix)))
                if new_line not in choices:
                    incorrect.append(new_line)
                    wrong_count += 1
                else:
                    correct.append(new_line)
                    right_count += 1
                #print(f"Correct: {right_count}, Incorrect: {wrong_count}")
    return correct, incorrect, autocompleter


def gen_sentence_tree(compressed, file):
    engine = SentenceAutocompleteEngine({
        'file': file,
        'autocompleter': 'simple' if not compressed else "compressed",
        'weight_type': 'sum'
    })
    print(f"{'Simple' if not compressed else 'Compressed'} tree -\nSorted: {sorted_test(engine.autocompleter)}\nFully Compressed: {compressed_test(engine.autocompleter)}\nFree of SVS: {same_value_subtree_test(engine.autocompleter)}\n")
    return engine.autocompleter


def check_all_inserted_sentence(compressed):
    def mapper(x):
        return x[0]
    file = 'data/google_searches.csv'
    autocompleter = gen_sentence_tree(compressed, file)
    correct = []
    incorrect = []
    wrong_count = 0
    right_count = 0
    with open(file) as csvfile:
        reader = csv.reader(csvfile)
        for line in reader:
            sanit = ""
            for ch in line[0]:
                if ch.isalnum() or ch == " ":
                    sanit += ch
            if len(sanit) < 1:
                continue
            line = sanit.split(" ")
            prefix = line[:math.ceil(len(line)/2)]
            choices = map(mapper, autocompleter.autocomplete(prefix))
            if sanit not in choices:
                incorrect.append(sanit)
                wrong_count += 1
            else:
                correct.append(sanit)
                right_count += 1
            #print(f"Correct: {right_count}, Incorrect: {wrong_count}")
    return correct, incorrect, autocompleter


def print_tests(root):
    print(f"After single prefix insert - \nSorted: {sorted_test(root)}\nFully Compressed: {compressed_test(root)}\nFree of SVS: {same_value_subtree_test(root)}\n")


if __name__ == "__main__":
    import sys
    sys.setrecursionlimit(5000)

    compressed = True
    print("Starting tests")
    gen_root = get_tree_creator("average", compressed=compressed)

    root = gen_root()
    root.insert("hello world", 5, list("hello world"))
    print_tests(root)

    root = gen_root()
    inserted_strings = random_insert(root)
    print_tests(root)
    deleted_strings = random_delete(root, inserted_strings, 100)
    print_tests(root)
    print(f"Passes autocomplete test: {autocomplete_test(root)}")

    root = gen_root()
    file_insert(root, "data/common_words.txt")
    print_tests(root)

    print(f"Running LOTR letter autocompleter")
    correct, incorrect, engine = check_all_inserted_letter(compressed)
    gen_letter_tree(False, "data/lotr.txt")
    print(f"number of leaves: {len(engine._get_all_leaves(None))}")
    for i in range(len(incorrect)):
        print(f"Incorrect is: {incorrect[i]}")
        pass
    print(f"Passes autocomplete test: {autocomplete_test(engine)}")

    print(f"\n\nRunning Google Search sentence autocompleter")
    correct, incorrect, engine = check_all_inserted_sentence(compressed)
    gen_sentence_tree(False, "data/google_searches.csv")
    print(f"Number of leaves: {len(engine._get_all_leaves(None))}")
    for i in range(min(len(incorrect), 20)):
        print(f"Incorrect is: {incorrect[i]}")
        pass
    print(f"Passes autocomplete test: {autocomplete_test(engine, True)}")


