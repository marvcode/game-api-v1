# ###################################################################
#
# Written by: Marvin Fuller
# date: November 2016
# App: Hangman API
#
# ##################################################################
import endpoints
import logging
from google.appengine.ext import ndb
from hang_models import *
from protorpc import remote, messages, message_types
import random
import string
import webapp2

# ###############################################################
# helper functions


def findOccurences(s, ch):
    return [i for i, letter in enumerate(s) if letter == ch]


def get_new_current(current, puzzle, guess):
    '''Create a new current based on correct guess'''
    # This function focuses on string manipulation
    # Create a list of all the occurences of the guess
    ptrlist = findOccurences(puzzle, guess)
    hit_count = len(ptrlist)
    # update current value to new value with guessed letters
    temp_puz = list(current)
    for i in ptrlist:
        temp_puz[i] = guess
    new_current = "".join(temp_puz)
    return {'new_current': new_current,
            'hit_count': hit_count}


def id_generator(size=4, chars=string.ascii_uppercase + string.digits):
    ''' Create a random game id of 4 characters. Verify not previously used'''
    need_id = True
    while need_id is True:
        rand_id = ''.join(random.choice(chars) for _ in range(size))
        # check to make sure this new rand_id does not exist in datastore
        if Game.query(Game.game_id == rand_id).get():
            need_id = True
        else:
            need_id = False
    return rand_id


def get_puzzle(level):
    ''' generate a new game by generating a random game id, '''
    # generate random game_id
    # 1. fetch all keys keys = Model.query().fetch(keys_only=True)
    # 2. grab a random key key = random.sample(keys, 1)[0]
    # 3. get the entity: return key.get().
    # of course this could be easily extended to support ranges of entities
    puzzle_keys = Puzzle.query()\
                        .filter(Puzzle.level == level)\
                        .fetch(keys_only=True)
    # random.sample(population, k)
    rand_key = random.sample(puzzle_keys, 1)[0]
    final = rand_key.get()
    return {'puzzle': final.puzzle,
            'length': final.length,
            'level': final.level}


def validate_user(user):
    ''' accept the argument of a username and validate
         that it exists in the datastore.'''
    #
    uchek = User.query().filter(User.user_name == user).get()
    # set response values
    if uchek:
        acpt = True
        rejCauseCode = 0
        info = ""
    else:
        acpt = False
        rejCauseCode = 1  # invalid username
        info = "Invalid user name: {} in request".format(user)
    return {'acpt': acpt,
            'rejCode': rejCauseCode,
            'info': info}


def validate_guess(user_name, game_id, guess):
    ''' this function checks guess for validity'''
    # 1.determine if legal guess, correct, or miss
    # check for valid character (A-Z)
    # check for Length of guess (single character only)
    if (len(guess) == 1) and (guess.isalpha()):
        # path if length and only letters are valid
        guess = guess.upper()
        vld = True
        rejCauseCode = 0
        info = 'Alpha & Length checks valid'
        try:
            g = Game.query(ndb.AND(
                  Game.game_id == game_id,
                  Game.user_name == user_name,
                  Game.game_active == 1)).get()
            # check if guess is already in guess history list
            if g.guess_history:
                # path if guess history exists
                if guess in str(g.guess_history):
                    vld = False
                    rejCauseCode = 5  # guess already in guess history
                    info = 'guess already in guess history'
        except:
            # path if game query returns none indicating no game exists with
            # requested user
            vld = False
            rejCauseCode = 6  # User name and game ID mismatch
            info = 'No game exists with requested user & game ID'
    else:
        # path if guess length and only letters are NOT valid
        vld = False
        rejCauseCode = 7  # Value provided for Guess is invalid
        info = 'Value provided for Guess is invalid'
    return {'valid': vld,
            'rejCode': rejCauseCode,
            'info': info}


def process_guess(user_name, game_id, guess):
    ''' function assumes guess is valid & prcesses database items for guess'''
    # guess has been previously validated for length and alpha
    info = ''
    # query for this specific game
    g = Game.query(ndb.AND(
                  Game.game_id == game_id,
                  Game.user_name == user_name)).get()
    # Increment number of guesses &update items in database
    g.num_guesses = g.num_guesses + 1
    g.guess_history = g.guess_history + guess
    g.put()
    # check is guess correct or a miss
    if guess in str(g.puzzle):
        # path if guess is correct
        # Update update score, update current, check for solve
        guess_correct = True
        info = 'Guess Correct! '
        new_current = get_new_current(g.current, g.puzzle, guess)
        g.current = new_current['new_current']
        g.score = g.score + (new_current['hit_count'] * 10)
        g.put()
        # check for 'solved'
        if '_' not in g.current:
            # path if puzzle solved
            g.game_active = 2  # 2 = solved
            g.put()
            # add score from this game to user's total score
            u = User.query(User.user_name == user_name).get()
            u.tot_score = u.tot_score + g.score
            if g.score > u.high_score:
                u.high_score = g.score
            u.put()
            info = info + \
                'Solved! {} points added to your total'.format(g.score)
    else:
        # path if guess is incorrect
        # update miss count
        guess_correct = False
        info = 'Guess incorrect! '
        g.num_misses = g.num_misses + 1
        g.miss_history = g.miss_history + guess
        g.put()
        # check for game over
        if g.num_misses >= 6:
            # game over path
            g.game_active = 3  # 3= Game Over
            g.score = 0  # reset score for this game to zero
            g.put()
            info = info + 'Game Over!'
    return {'correct': guess_correct,
            'active': g.game_active,
            'info': info}
