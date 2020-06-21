import random
import re
import string
import json
import unidecode
import numpy as np
from autocorrect import Speller

spell = Speller(lang='en')

f = open("params.json")
params = json.load(f)
f.close()

contractions = params["contractions"]
alphabet_string = params["alphabet_string"]
alphabet_sz = params["alphabet_sz"]
n = params["n"]
min_val = np.finfo(float).eps


# this is the first step: picking a starting point
def select_sigma(alphabet):
    # picks a random permutation of the alphabet
    alphabet = list(alphabet)
    random.shuffle(alphabet)
    return ''.join(alphabet)


# encrypts a message using the cipher
def encode(plaintext, sigma, alphabet):
    # sigma: {a,b,c,...} -> {hfaiduzhi}
    sigmaMap = dict(zip(alphabet, sigma))
    return ''.join(sigmaMap.get(char.lower(), char) for char in plaintext)


# decrypts the message
def decode(cipher_text, sigma, alphabet):
    # sigma^-1: {hfaiduzhi} -> {a,b,c,...}
    sigmaMap = dict(zip(sigma, alphabet))
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
def get_energy(decoded, transition_matrix):
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
