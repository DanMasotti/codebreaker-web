from helpers import *

max_iterations = params["max_iterations"]
beta = params["beta"]
alphabet_string = params["alphabet_string"]

'''
    Purpose: runs the metropolis algorithm to swap alphabet to decrease "energy"
    In: cipher text and the transition matrix
    Out: decoded text according to the scheme
'''


def run_metropolis(cipher_text):
    sigma = select_sigma(alphabet_string)
    decoded = decode(cipher_text, sigma, alphabet_string)
    energy_sigma = get_energy(decoded)

    curr_text = cipher_text
    iteration = 0

    while iteration <= max_iterations:

        tau = swap_letters(sigma)
        decoded = decode(curr_text, tau, alphabet_string)
        energy_tau = get_energy(decoded)
        delta_energy = energy_tau - energy_sigma

        if delta_energy < 0:
            # accept
            sigma = tau
            energy_sigma = energy_tau
            # if applying sigma to the current text retrieves the original ciphertext
            if encode(curr_text, sigma, alphabet_string) == cipher_text:
                # we're done
                return
        else:
            # reject: accept with prob exp(-beta*delta_V)
            p = np.exp(-beta * delta_energy)
            U = np.random.uniform(0, 1)
            if U <= p:
                sigma = tau
                energy_sigma = energy_tau

        iteration = iteration + 1

        yield decoded
