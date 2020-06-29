import random
import re
import string
import json
import unidecode
import numpy as np
from itertools import product
from collections import Counter
from autocorrect import Speller
import os

spell = Speller(lang='en')

f = open("params.json")
params = json.load(f)
f.close()

contractions = params["contractions"]
alphabet_string = params["alphabet_string"]
alphabet = list(alphabet_string)
alphabet_sz = params["alphabet_sz"]
n = params["n"]
min_val = np.finfo(float).eps


# this is the first step: picking a starting point
def select_sigma(current_alphabet):
    # picks a random permutation of the alphabet
    current_alphabet = list(current_alphabet)
    random.shuffle(current_alphabet)
    return ''.join(current_alphabet)


# encrypts a message using the cipher
def encode(plaintext, sigma, current_alphabet):
    # sigma: {a,b,c,...} -> {hfaiduzhi}
    sigmaMap = dict(zip(current_alphabet, sigma))
    return ''.join(sigmaMap.get(char.lower(), char) for char in plaintext)


# decrypts the message
def decode(cipher_text, sigma, current_alphabet):
    # sigma^-1: {hfaiduzhi} -> {a,b,c,...}
    sigmaMap = dict(zip(sigma, current_alphabet))
    return ''.join(sigmaMap.get(char.lower(), char) for char in cipher_text)


# this is how we move from one alphabet to the next
def swap_letters(alphabet_to_swap):
    # choose two random spots in the alphabet
    chosen_first_place = random.randint(0, alphabet_sz - 1)
    chosen_second_place = random.randint(0, alphabet_sz - 1)
    # make sure they're not equal
    while chosen_second_place == chosen_first_place:
        chosen_second_place = random.randint(0, alphabet_sz - 1)
    # because strings are immutable, need to make a list before accessing
    alphabet_to_swap = list(alphabet_to_swap)
    # swap
    first = alphabet_to_swap[chosen_first_place]
    second = alphabet_to_swap[chosen_second_place]
    alphabet_to_swap[chosen_second_place] = first
    alphabet_to_swap[chosen_first_place] = second
    # return new alphabet as a string
    result = ''.join(alphabet_to_swap)
    return result


# using the gibbs measure as energy function to minimize
def get_energy(decoded):
    transition_matrix = get_transition_matrix()
    # preallocate
    present_ngrams = np.empty(len(decoded), dtype=object)
    # make all the ngrams
    for i in range(len(decoded)):
        present_ngrams[i] = decoded[i:i + n]
    return -np.sum(np.log([transition_matrix.get(ngram, min_val) for ngram in present_ngrams]))


# makes corpus/input text cleaned
def clean_text(dirty_text):
    # remove accented characters
    valid_text = unidecode.unidecode(dirty_text)

    # expand any contractions
    contractions_re = re.compile('(%s)' % '|'.join(contractions.keys()))

    def replace(match):
        return contractions[match.group(0)]

    expanded_text = contractions_re.sub(replace, valid_text)

    # get rid of punctuation
    depunct_text = expanded_text.translate(str.maketrans('', '', string.punctuation))

    # get rid of numbers
    text = re.sub(r'[0-9]+', '', depunct_text)

    # make all lowercase
    text = text.lower()

    # get rid of huge spaces by splitting on word, then joining adding a space
    text = text.split()
    text = ' '.join(text)

    return text


def get_transition_matrix():
    if os.path.exists("transition_matrix.json"):
        f = open("transition_matrix.json")
        transition_matrix = json.load(f)
        f.close()
    else:
        with open("cleaned_corpus.txt") as f:
            cleaned_corpus = f.read()
        f.close()
        transition_matrix = build_transition_matrix(cleaned_corpus)
        with open("transition_matrix.json", "w") as write_file:
            json.dump(transition_matrix, write_file)

    return transition_matrix


"""
    Purpose: approximate the probability transitions in true English, that reason
    I use cache instead of helper method is to give users the option to change
    the size of n
    In: large corpus for approximating true langauge, params
    Out: transition matrix, stored on the user's cache
"""


def build_transition_matrix(corpus):
    corpus_sz = len(corpus)
    all_possible_ngrams = product(alphabet, repeat=n)
    # preallocate ngram list
    ngram_list = np.empty(corpus_sz, dtype=object)

    # get all the ngrams that are in the mined text
    for i in range(corpus_sz):
        ngram_list[i] = corpus[i:i + n]

    corpus_ngrams = set(ngram_list)
    ngram2freq = Counter(ngram_list)
    total_ngrams = sum(ngram2freq.values())

    # transition matrix Q as dictionary: Q[ngram] = p_hat(ngram)
    transition_matrix = {}

    for perm in enumerate(all_possible_ngrams):
        ngram = ''.join(list(perm[1]))

        # if the ngram is not absolute garbage, store it in Q
        if ngram in corpus_ngrams:
            # empirical probability
            transition_matrix[ngram] = (1 / total_ngrams) * (ngram2freq.get(ngram, min_val))
    return transition_matrix


# checks if the input text is alphanumeric
def validate_input_text(input_text):
    if all(char in string.ascii_letters + " " for char in input_text):
        return True
    else:
        return False


'''
at the end of MCMC we reach a local minimum which might need a single letter swap,
since we have no guarantees about how long MCMC would take to get it actually right,
it's easier to just autocorrect the text that is approximately correct
'''


def spell_check(misspelled_text):
    listed = misspelled_text.split()
    spelled_checked_list = []
    for misspelled_word in listed:
        spelled_checked_list.append(spell(misspelled_word))
    spelled_checked = " ".join(spelled_checked_list)
    return spelled_checked
