from flask import Flask, redirect, render_template, request
from flask_caching import Cache
from run_metropolis import *
import json
import numpy as np


# in production, params and corpus would be stored on a db
f = open("params.json")
params = json.load(f)
f.close()




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
            decoded = run_metropolis(cipher_text)
            decoded = spell_check(decoded)
            return render_template("index.html", data=decoded)
        else:
            non_supported = "sorry, this cipher is not supported yet"
            return render_template("index.html", data=non_supported)
    else:
        return render_template("index.html")







if __name__ == "__main__":
    app.run(debug=True)
