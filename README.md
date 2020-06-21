# codebreaker-web
Flask based web application for breaking a substitution cipher with MCMC

# Getting Started
To run the web app, run `python app.py`.  This will run the Flask server at http://127.0.0.1:5000/.

# How to use
Type in your cipher text and click `Break!`.  This starts the MCMC procedure to swap alphabets.  Since this probabilistic, you will unlikely retrieve the actual plaintext, however, at the end of the procedure, the result is intelligible and may just need to swap all `x's` with `s's` for example.

# How it works
The procedure is detailed in the Jupyter notebook, but the algorithm is based on this paper: https://math.uchicago.edu/~shmuel/Network-course-readings/MCMCRev.pdf
