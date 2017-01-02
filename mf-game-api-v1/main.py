# !/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ###################################################################
#
# Written by: Marvin Fuller
# date: November 2016
# App: Hangman API
#
# ##################################################################

import endpoints
import logging
from hang_models import *
from hang_funct import *
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.api import mail, app_identity
from google.appengine.ext import ndb
from protorpc import remote, messages, message_types
import random
import re
import string
import webapp2

#
# ###### API Definitions ##############################################
#
# GameAdmin API Definition
# ####################################################################


@endpoints.api(name='gameadmin', version='v1',
               description='API for Game Administrative functions')
class GameAdminApi(remote.Service):
    """GameAdmin API"""
    @endpoints.method(request_message=CREATE_USER_REQ,
                      response_message=GenericResp,
                      path='create_user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create new user endpoint"""
        # /create_user/<username>
        # check requested username for proper format
        if len(request.user_name) > 0:
            vuser = validate_name(request.user_name, request.email)
            acpt = vuser['acpt']
            rejCauseCode = vuser['rejCode']
            info = vuser['info']
        if vuser['acpt'] is True:
            # path if requested username was valid
            acpt = vuser['acpt']
            rejCauseCode = vuser['rejCode']
            info = vuser['info'] + "This will create a new "
            info = info + "{} user per request.".format(request.user_name)
            user = User(user_name=request.user_name,
                        email=request.email,
                        high_score=0,
                        tot_score=0)
            user.put()
        else:
            # path is requested user is already in database
            acpt = vuser['acpt']
            rejCauseCode = vuser['rejCode']
            info = vuser['info']
        return GenericResp(accepted=acpt,
                           cause_code=rejCauseCode,
                           resp_info=info)


    @endpoints.method(request_message=CREATE_GAME_REQ,
                      response_message=GenericResp,
                      path='create_game',
                      name='create_game',
                      http_method='POST')
    def create_game(self, request):
        """Create new game endpoint"""
        # /create_game/<username>/<level>
        # Check that provided user_name is valid
        # create a new game instance
        # persist new game info to datastore
        # respond back with game information in NewGameRespForm
        newCurrent = ''
        vuser = validate_user(request.user_name)
        acpt = vuser['acpt']
        rejCauseCode = vuser['rejCode']
        info = vuser['info']
        if vuser['acpt'] is True:
            # path for username is valid
            info = "Creating a new game for "
            info = info + "{} specified in request.".format(request.user_name)
            newGameID = id_generator()
            # go get a new random puzzle from datastiore
            newPuzzleWord = get_puzzle(request.level)
            newCurrent = "_" * newPuzzleWord['length']
            # add new game to datastore
            data = Game(game_id=newGameID,
                        user_name=str(request.user_name),
                        puzzle=newPuzzleWord['puzzle'],
                        level=newPuzzleWord['level'],
                        word_size=newPuzzleWord['length'],
                        num_guesses=0,
                        num_misses=0,
                        guess_history="",
                        miss_history="",
                        game_active=1,
                        current=newCurrent,
                        score=0)
            data.put()
        return GenericResp(accepted=acpt,
                           cause_code=rejCauseCode,
                           game_id=newGameID,
                           word_size=newPuzzleWord['length'],
                           num_guesses=0,
                           num_misses=0,
                           miss_history="",
                           current=newCurrent,
                           resp_info=info)

    @endpoints.method(request_message=GET_HIGH_SCORES_REQ,
                      response_message=GenericResp,
                      path='get_high_scores',
                      name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
        """Create get high scores endpoint"""
        # determine if a number of resuts parameter was requested
        # default number of results is 7
        if request.num_results:
            num_req = request.num_results
        # prepare response values
        acpt = True
        rejCauseCode = 0
        info = "Provide top {} highest user scores.".format(num_req)
        # query Games Kind for top # highest scores
        u = User.query().order(-User.high_score)
        usrHighs = u.fetch(num_req)
        # add each user to info string to be returned
        for usr in usrHighs:
            info = info + " {user_name:" + str(usr.user_name) + ";"
            info = info + 'email:' + str(usr.email) + ";"
            info = info + 'high_score:' + str(usr.high_score) + "; } "
        return GenericResp(accepted=acpt,
                           cause_code=rejCauseCode,
                           resp_info=info)

    @endpoints.method(request_message=message_types.VoidMessage,
                      response_message=GenericResp,
                      path='get_user_rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Create get user rankings endpoint"""
        acpt = True
        rejCauseCode = 0
        info = "This will provide top 10 users by total scores. "
        # query Games Kind for top 7 highest scores
        u = User.query().order(-User.tot_score)
        usrTot = u.fetch(10)
        # add each user to info string to be returned
        for usr in usrTot:
            info = info + ' {user_name:' + str(usr.user_name) + ";"
            info = info + 'email:' + str(usr.email) + ";"
            info = info + 'high_score:' + str(usr.tot_score) + "; } "
        return GenericResp(accepted=acpt,
                           cause_code=rejCauseCode,
                           resp_info=info)

    @endpoints.method(request_message=GET_USER_GAMES_REQ,
                      response_message=GenericResp,
                      path='get_user_games',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Create get user games endpoint"""
        vuser = validate_user(request.user_name)
        acpt = vuser['acpt']
        rejCauseCode = vuser['rejCode']
        info = vuser['info']
        if vuser['acpt'] is True:
            # path for username is valid
            info = "Listing active games for user "
            info = info + "{}.".format(request.user_name)
            # query Games Kind for entities with user = requested user
            g = Game.query(Game.user_name == request.user_name).\
                order(-Game.score)
            usrGames = g.fetch()
            # prepare & format game list
            for game in usrGames:
                info = info + ' {game_id: ' + str(game.game_id) + ";"
                info = info + 'level: ' + str(game.level) + ";"
                info = info + 'score: ' + str(game.score) + ";"
                info = info + 'active: ' + str(game.game_active) + ";"
                info = info + 'current: ' + str(game.current) + ";"
                info = info + 'miss_history:  ' + str(game.miss_history) + ";"
                info = info + 'num_misses: ' + str(game.num_misses) + ";"
                info = info + 'word_size: ' + str(game.word_size) + ";} "
        else:
            # Path if user name from request is invalid (does not exist)
            info = info + "{};"
        return GenericResp(accepted=acpt,
                           cause_code=rejCauseCode,
                           resp_info=info)

    @endpoints.method(request_message=ADD_PUZZLE_REQ,
                      response_message=GenericResp,
                      path='add_puzzle',
                      name='add_puzzle',
                      http_method='POST')
    def add_puzzle(self, request):
        """Add a new puzzle word to puzzle database"""
        # return acpt, rejcausecode, info
        vuser = validate_user(request.user_name)
        acpt = vuser['acpt']
        rejCauseCode = vuser['rejCode']
        info = vuser['info']
        if vuser['acpt'] is True:
            # path for username is valid
            info = "Adding new puzzle to database."
            # Add new puzzle to datastore
            # check does word already exist in db
            # convert all characters to upper case
            # count length of word submitted and store into length value
            # determine level based on length and store level into db
            if Puzzle.query(Puzzle.puzzle == request.puzzle.upper()).get():
                # Path if puzzle submited is already in datastore
                acpt = False
                rejCauseCode = 4  # requested puzzle already exists
                info = "Requested puzzle already exists."
            else:
                # Path if puzzle submitted is good (not in database)
                # convert new puzzle word to all upper case
                new_puzzle = request.puzzle.upper()
                newWordSize = len(new_puzzle)
                # determine puzzle level based on length of puzzle
                newWordLevel = 1
                if newWordSize > 6:
                    newWordLevel = 2
                # add new puzzle to datastore
                data = Puzzle(puzzle=new_puzzle,
                              length=newWordSize,
                              level=newWordLevel)
                data.put()
                info = "New puzzle {} added to datastore. ".format(new_puzzle)
        return GenericResp(accepted=acpt,
                           cause_code=rejCauseCode,
                           resp_info=info)


# ###########################################################################
# HangmanAPi API Definition for game play
# ###########################################################################
@endpoints.api(name='hangman', version='v1',
               description='API for simple hangman game')
class HangmanApi(remote.Service):
    """Hangman Game API"""
    @endpoints.method(request_message=CANCEL_GAME_REQ,
                      response_message=GenericResp,
                      path='cancel_game',
                      name='cancel_game',
                      http_method='DELETE')
    def cancel_game(self, request):
        """Cancel existing game endpoint"""
        vuser = validate_user(request.user_name)
        acpt = vuser['acpt']
        rejCauseCode = vuser['rejCode']
        info = vuser['info']
        if vuser['acpt'] is True:
            # path for username is valid
            # validate game-id
            g = Game.query(ndb.AND(Game.game_id == request.game_id,
                                   Game.user_name == request.user_name)).get()
            if g:
                # path if requested game_id is valid
                info = info + "Canceling requested game:"
                info = info + "{} ".format(request.game_id)
                # delete game from datastore
                g.key.delete()
            else:
                # path if no game found with requested game_id & user_name
                acpt = False
                rejCauseCode = 2  # invalid game ID
                info = info + " Could not find game reuested:"
                info = info + "{} ".format(request.game_id)
                info = info + "owned by username "
                info = info + "{}".format(request.user_name)
        return GenericResp(accepted=acpt,
                           cause_code=rejCauseCode,
                           resp_info=info)

    @endpoints.method(request_message=GET_GAME_HISTORY_REQ,
                      response_message=GenericResp,
                      path='get_game_history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """ Provides current status and histroy of game requested"""
        # try to find a game with requested username and game ID
        g = Game.query(ndb.AND(
              Game.game_id == request.game_id,
              Game.user_name == request.user_name)).get()
        if g:
            acpt = True
            rejCauseCode = 0
            info = "Game details for game {}".format(request.game_id)
        else:
            # path if game query returns none indicating no game exists with
            # requested user
            acpt = False
            rejCauseCode = 6  # User name and game ID mismatch
            info = 'No game exists with requested user & game ID'
            return GenericResp(accepted=acpt,
                               cause_code=rejCauseCode,
                               resp_info=info)
        return GenericResp(accepted=acpt,
                           cause_code=rejCauseCode,
                           resp_info=info,
                           game_id=request.game_id,
                           word_size=g.word_size,
                           num_guesses=g.num_guesses,
                           num_misses=g.num_misses,
                           guess_history=g.guess_history,
                           miss_history=g.miss_history,
                           game_active=g.game_active,
                           score=g.score,
                           current=g.current)

    @endpoints.method(request_message=GUESS_LETTER_REQ,
                      response_message=GenericResp,
                      path='guess_letter',
                      name='guess_letter',
                      http_method='POST')
    def guess_letter(self, request):
        """Guess a letter endpoint"""
        # /guess_letter/<username>/<game_id>/<guess>
        # First validate user
        vuser = validate_user(request.user_name)
        acpt = vuser['acpt']
        rejCauseCode = vuser['rejCode']
        info = vuser['info']
        if vuser['acpt'] is True:
            # path for username is valid
            # Validate guess:
            guess = request.guess.upper()
            v_guess = validate_guess(request.user_name, request.game_id, guess)
            if v_guess['valid']:
                # path if guess is valid or legal
                p_guess = process_guess(request.user_name,
                                        request.game_id,
                                        guess)
                info = info + p_guess['info']
            else:
                # path if guess is not valid
                acpt = v_guess['valid']
                rejCauseCode = v_guess['rejCode']
                info = v_guess['info']
        else:
            # path if user in request is not valid
            acpt = False
            rejCauseCode = 1  # No Such user exists
            info = "user name is INVALID"
        # query for updated info for this specific game
        g = Game.query(ndb.AND(
            Game.game_id == request.game_id,
            Game.user_name == request.user_name)).get()
        # if correct, update score, update current, check for solve
        # if solve, then respond with solved message, add score to total score
        # if miss, update miss count, check for game over
        # if game over, terminate game active state,
        return GenericResp(accepted=acpt,
                           cause_code=rejCauseCode,
                           resp_info=info,
                           game_id=request.game_id,
                           word_size=g.word_size,
                           num_guesses=g.num_guesses,
                           num_misses=g.num_misses,
                           guess_history=g.guess_history,
                           miss_history=g.miss_history,
                           game_active=g.game_active,
                           score=g.score,
                           current=g.current)


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        '''Send a reminder email to Users with Active games via email.'''
        '''Called every hour using a cron job'''
        # email_from = 'alerts@marvsprojectsite.net'
        app_id = app_identity.get_application_id()
        email_from = 'noreply@{}.appspotmail.com'.format(app_id)
        subject = 'This is an email reminder about your Hangman Games!'
        body_head = "This is a reminder that you still have active Hangman"
        body_head = body_head + " games waiting for you to finish."
        body_head = body_head + "  Below is a list of active games with"
        body_head = body_head + "  the current score.                  "
        body_foot = "  We hope you enjoy the game!"
        body_foot = body_foot + "   Thanks for playing. "
        body_foot = body_foot + "           "
        usr_set = set()
        game_list = {}
        # Query for Active games
        activeGames = Game.query(Game.game_active == 1).fetch()
        for game in activeGames:
            # establish a set of unique users that need email reminders
            # using a set() to avoid duplicates since some user may have
            # multiple active games
            usr = User.query(User.user_name == game.user_name).get()
            usr_set.add(usr.user_name)
            # check to see if a user is already in the game list
            if game.user_name in game_list:
                # path if user is already in game list, just update
                # game_id & corresponding score
                game_list[game.user_name]['game_id'].\
                    append((game.game_id, game.score))
            else:
                # path if user not previously added to game list
                game_list[game.user_name] = \
                 {'email': usr.email, 'game_id': [(game.game_id, game.score)]}
        # prepare to send the necessary emails
        for user in usr_set:
            # each user in usr_set should get an email
            body_details = "Username = " + str(user) + "    "
            email_to = str(game_list[user]['email'])
            for id in game_list[user]['game_id']:
                body_details = body_details + "Game ID = " + str(id[0]) + "  "
                body_details = body_details + "Score = " + str(id[1]) + ".   "
            body = body_head + body_details + body_foot
            mail.send_mail(email_from, email_to, subject, body)

        self.response.write(
            "<html><body><p><h1>Reminders Processed!</h1></p></body></html>")


api = endpoints.api_server([GameAdminApi, HangmanApi])

app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail)], debug=True)
