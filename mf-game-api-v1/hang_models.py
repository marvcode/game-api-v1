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
from protorpc import remote, messages, message_types
import webapp2

# Levels will be used as choices in the game model
levels = [1, 2]
# #################################################################
# ResourceContainer definitions for requests
#


CREATE_USER_REQ = endpoints.ResourceContainer(
                            user_name=messages.StringField(1),
                            email=messages.StringField(2)
                            )
CREATE_GAME_REQ = endpoints.ResourceContainer(
                            user_name=messages.StringField(1),
                            level=messages.IntegerField(2)
                            )
CANCEL_GAME_REQ = endpoints.ResourceContainer(
                            user_name=messages.StringField(1),
                            game_id=messages.StringField(2)
                            )
GET_HIGH_SCORES_REQ = endpoints.ResourceContainer(
                            num_results=messages.IntegerField(1,
                                                              required=False,
                                                              default=7)
                            )
GET_USER_GAMES_REQ = endpoints.ResourceContainer(
                            user_name=messages.StringField(1)
                            )
GET_GAME_HISTORY_REQ = endpoints.ResourceContainer(
                            user_name=messages.StringField(1),
                            game_id=messages.StringField(2)
                            )
GUESS_LETTER_REQ = endpoints.ResourceContainer(
                            user_name=messages.StringField(1),
                            game_id=messages.StringField(2),
                            guess=messages.StringField(3)
                            )
ADMIN_REQ = endpoints.ResourceContainer(
                            user_name=messages.StringField(1)
                            )
ADD_PUZZLE_REQ = endpoints.ResourceContainer(
                            user_name=messages.StringField(1),
                            puzzle=messages.StringField(2),
                            )


# #########################################################
# Define Game Response Forms
#


class GenericResp(messages.Message):
    """Define a response class that covers all request types."""
    accepted = messages.BooleanField(1, required=True)
    cause_code = messages.IntegerField(2, required=False)
    game_id = messages.StringField(3, required=False)
    word_size = messages.IntegerField(4, required=False)
    num_guesses = messages.IntegerField(5, required=False)
    num_misses = messages.IntegerField(6, required=False)
    guess_history = messages.StringField(7, required=False)
    miss_history = messages.StringField(8, required=False)
    game_active = messages.IntegerField(9, required=False)
    current = messages.StringField(11, required=False)
    score = messages.IntegerField(12, required=False)
    resp_info = messages.StringField(13, required=False)

# #########################################################
# Define Database Models
#


class User(ndb.Model):
    """User profile"""
    user_name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    high_score = ndb.IntegerProperty(required=False)
    tot_score = ndb.IntegerProperty(required=False)


class Game(ndb.Model):
    """Hangman Game object"""
    game_id = ndb.StringProperty(required=True)
    user_name = ndb.StringProperty(required=True)
    puzzle = ndb.StringProperty(required=True)
    level = ndb.IntegerProperty(required=True, choices=levels, default=1)
    word_size = ndb.IntegerProperty(required=True)
    num_guesses = ndb.IntegerProperty(required=True)
    num_misses = ndb.IntegerProperty(required=True)
    guess_history = ndb.StringProperty(required=True)
    miss_history = ndb.StringProperty(required=True)
    game_active = ndb.IntegerProperty(required=True, default=1)
    current = ndb.StringProperty(required=True)
    score = ndb.IntegerProperty(required=True)


class Puzzle(ndb.Model):
    puzzle = ndb.StringProperty(required=True)
    length = ndb.IntegerProperty(required=True)
    level = ndb.IntegerProperty(required=True)
