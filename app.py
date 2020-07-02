from flask import Flask, redirect, render_template, request, Response, url_for, stream_with_context
from run_metropolis import *

# for temporarily holding the built transition matrix in user's cache
app = Flask(__name__)


def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    # uncomment if you don't need immediate reaction
    rv.disable_buffering()
    return rv


@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        cipher_text = request.form["cipherText"]
        is_valid = validate_input_text(cipher_text)
        # validate the input text
        if is_valid:
            # run metropolis
            data = " "
            return render_template("index.html", data=run_metropolis(cipher_text));
        else:
            non_supported = "sorry, this cipher is not supported yet"
            return render_template("index.html", data=non_supported)
    else:
        return render_template("index.html", data=" ")


if __name__ == "__main__":
    app.run(debug=True)
