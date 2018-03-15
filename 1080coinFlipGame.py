# coding:utf8

import random

def get_guess(string=''):
    if string:
        print(string)

    while True:
        print('Guess the coin toss! Enter heads or tails:')
        guess = input()
        if guess in ('heads', 'tails'):
            break
    return guess

mapping = {0: 'tails', 1: 'heads'}

guess = get_guess()
toss = mapping[random.randint(0, 1)]  # fix: toss = random.randint(0, 1)
if toss == guess:
    print('You got it!')
else:
    guess = get_guess('Nope! Guess again!')  # fix: guesss = input()
    if toss == guess:
        print('You got it!')
    else:
        print('Nope. You are really bad at this game.')
