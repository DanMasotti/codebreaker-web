from flask import Flask, redirect, render_template, request
from flask_caching import Cache
from run_metropolis import *
import json
from collections import Counter
import numpy as np
from itertools import product

# in production, params and corpus would be stored on a db
f = open("params.json")
params = json.load(f)
f.close()

f = open("cleaned_corpus.txt")
cleaned_corpus = f.read()
f.close()

alphabet_string = params["alphabet_string"]
alphabet = list(alphabet_string)
alphabet_sz = len(alphabet)
n = params["n"]
min_val = np.finfo(float).eps

# for temporarily holding the built transition matrix in user's cache
cache = Cache()
app = Flask(__name__)
app.config['CACHE_TYPE'] = 'simple'
cache.init_app(app)


@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        cipher_text = request.form["cipherText"]
        is_valid = validate_input_text(cipher_text)
        # validate the input text
        if is_valid:
            transition_matrix = build_transition_matrix(cleaned_corpus)
            decoded = run_metropolis(cipher_text, transition_matrix)
            decoded = spell_check(decoded)
            return render_template("index.html", data=decoded)
        else:
            non_supported = "sorry, this cipher is not supported yet"
            return render_template("index.html", data=non_supported)
    else:
        return render_template("index.html")


"""
    Purpose: approximate the probability transitions in true English, that reason
    I use cache instead of helper method is to give users the option to change
    the size of n
    In: large corpus for approximating true langauge, params
    Out: transition matrix, stored on the user's cache
"""


@cache.cached(timeout=36000, key_prefix="build_transition_matrix")
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


if __name__ == "__main__":
    app.run(debug=True)
