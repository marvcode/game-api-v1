#Hangman Game API
####*FullStack Web Developer Nanodegree Project 4*

###Game Description:
Hangman is a simple guessing game that many of us played as children. Each game begins with a random hidden word puzzle.  At the start of the game, the player only knows how many letters are in the word puzzle he/she is attempting to solve.  During game play, the player guesses letters, one at a time, attempting to fill in the puzzle.  Points are awarded for correct letter guesses.  Guesses that are incorrect are tallied as a miss.  If a player has 6 misses, the game is immediately over and the points accumulated during that game are lost.  However, if a player solves the puzzle by filling in all the letters, the score of the game is added to the player's lifetime total score which cant be lost.

When creating a game, the user may choose the challenge level of the puzzle by designating a Level 1 or Level 2 game.  Level 2 games have puzzles of greater than 6 characters. 


##Instructions for Game Play  
###1. Create a username
To get started with Hangman, you must first create a username for yourself.  Each user will create their own username and provide an email address for the user.   

`/create_user`  end point

*Example:*
`POST https://mf-game-api-v1.appspot.com/_ah/api/gameadmin/v1/create_user?email=me%40gmail.com&user_name=username`

*Response::*

`200 OK`

headers
```
{
"accepted": true,
"cause_code": "0",
"resp_info": "This will create a new 'username' user per request."
}
```

###2. Create Puzzles for the database
Next, you must make sure there are plenty of puzzles in the database.  Please note that any registered user in the datastore can add puzzles to the datastore.  You must use the `/add_puzzle` endpoint as follows:

`/add_puzzle` endpoint

*Example: This user test9 adding the word 'plate' to the puzzle database...*  
`POST https://mf-game-api-v1.appspot.com/_ah/api/gameadmin/v1/add_puzzle?puzzle=plate&user_name=test9`

Response:

`200 OK`


*headers*

```  
{  
"accepted": true,   
"cause_code": "0",  
"resp_info": "New puzzle PLATE added to datastore. "
}
```

For ideas on a source for random puzzles use this resource to generate random words.: http://www.desiquintans.com/noungenerator?count=1 

Also, here is a sample word database to get you started:  
- Brick  
- Japan 
- Coffin  
- Missile
- Profession
- Ship

###3. Create a Game
Next, its time to create a game.  When creating a game, you need to decide the challenge level by designating a level parameter as part of the request.  Level 1 represents puzzle words up to 6 characters long.  Level 2 puzzles represent puzzle words greater than 6 characters long. You must use the `/create_game` endpoint as follows:

`/create_game` endpoint

*Example: This user "test9" creating a new level 1 game...*  
`POST https://mf-game-api-v1.appspot.com/_ah/api/gameadmin/v1/create_game?level=1&user_name=test9`  
Response:  
`200 OK`   
*headers:*
```
{
 "accepted": true,
 "cause_code": "0",
 "current": "_____",
 "game_id": "7JEN",
 "miss_history": "",
 "num_guesses": "0",
 "num_misses": "0",
 "resp_info": "Creating a new game for test9 specified in request.",
 "word_size": "5"
}
```
###4. Start playing... Guessing Letters.
Finally, to play hangman, simply choose a game and start trying to solve the puzzle.  The API endpoint that will be used during game play is `/guess_letter`.  <b>Note</b>: The guess can only be one single alpha character.  Also, it is important to remember that the guess letter request must contain a username and game_id that are listed in the database as a specific game.  <br>
The `/guess_letter` function checks to make sure that the username matches the `game_id` provided before the guess is considered valid. 

`/guess_letter` endpoint

*Example: This user "test9" guessing the letter 'd' on game ID '7JEN' to guess add the word 'plate' to the puzzle database...*  
`POST https://mf-game-api-v1.appspot.com/_ah/api/hangman/v1/guess_letter?game_id=7JEN&guess=d&user_name=test9`  
Response::  
`200 OK`  
*headers:*  

```
{
 "accepted": true,
 "cause_code": "0",
 "current": "_____",
 "game_active": "1",
 "game_id": "7JEN",
 "guess_history": "D",
 "miss_history": "D",
 "num_guesses": "1",
 "num_misses": "1",
 "resp_info": "Guess incorrect! ",
 "score": "0",
 "word_size": "5"
}
```


###Score Keeping  
During game play, a user is awarded +10 points for each correct letter guessed.  Zero points are taken off for any incorrect letters guessed.  A user gets to bank points earned during game <b>only</b> if user completes the word puzzle successfully and solves the puzzle.  If a user loses a game due to a "hung" hangman, then all points gathered in this game are lost, but does not affect already banked points.  The potential for total score for a game is thereby determined by the length of the puzzle.
As with standard Hangman rules, a user loses the game upon guessing a 6th incorrect letter. 

###Game Active State
Each game contains a property called `game_active`.  This property represents the current state of the game. This field as an integer value to represent 3 states of a game.

game_active<br>Status | meaning  
----------------|------------  
1|Active
2|Solved
3|Game Over (hung hangman)



###Reminder Notifications
Active game reminder emails will be sent out periodically.  *<b>Note: These email reminders will only be sent to users with active games in the system.*</b>  Users without active games in the system will not get these reminder emails.  For test purposes I have set the frequency of the reminders to once per 30 minutes.  This is configurable in the cron.yaml file.  In production, it is recommended that the value be set to once per 24 hour period to avoid excessive email traffic.

<br>
<br>
##API Documentation (Detailed description of each endpoint)
####GameAdminApi  
All functions begin with 'https://mf-game-api-v1.appspot.com/_ah/api/gameadmin/v1'.  This group of API functions are used for administrative functions to support game play.  Each function is detailed below:  

####/create_user  
<b>Description:</b> This function is used to create a new user into the database for the first time.  
<b>Usage:</b> `https://mf-game-api-v1.appspot.com/_ah/api/gameadmin/v1/create_user?email=email&user_name=user_name`	

<b>Supported Methods:</b> `POST`  
><b> Example</b>:<br>
Request:  
`POST https://mf-game-api-v1.appspot.com/_ah/api/gameadmin/v1/create_user?email=test9%40gmail.com&user_name=test9  `  
Response:  
`200 OK`   
Show headers -  
```  
{  
 "accepted": true,  
 "cause_code": "0",  
 "resp_info": "This will create a new test9 user per request."  
}
```    


Request<br>Parameter |Details
--------- |-------
user_name|*Define the new username being requested.*<br>Type:String, Order:1, Required=True
email|*Specify the email address of the associated user.*<br>Type:String, Order:2, Required:True <br><b>Note: '@' symbol must be URL encode, so change '@' to '%40'. Example: me%40mymail.com</b>  
<b>Response Parameters |<b>Details</b>
accepted|*Indicates that the request was legal or valid.*<br>This response field Type:Boolean, Order=1, Required=True  
cause_code|*Indicates why request was not accepted.  See definition list of Cause Codes below.*<br>Type:Integer, Order=2, Required=False
resp_info|*This is text field that helps provide additional information about the results of the request.*<br>Type:String, Order:13, Required=False


<br>
####/create_game  

<b>Description:</b>  This function is used to create a new game.  This function will generate a random 4 character game_id as well as choose a random puzzle from the puzzle database.  
<b>Usage:</b>
`https://mf-game-api-v1.appspot.com/_ah/api/gameadmin/v1/create_game?level=level&user_name=user_name`  
<b>Supported Methods:</b> `POST`  
><b> Example</b>:  
Request  
`POST https://mf-game-api-v1.appspot.com/_ah/api/gameadmin/v1/create_game?level=1&user_name=test1`  
Response:  
`200 OK`  
Show headers -  
```json
{  
 "accepted": true,  
 "cause_code": "0",  
 "current": "______",  
 "game_id": "Z4ED",  
 "miss_history": "",  
 "num_guesses": "0",  
 "num_misses": "0",  
 "resp_info": "Creating a new game for test1 specified in request.",  
 "word_size": "6"  
}
```  
 

Request<br>Parameter |Details
--------- |-------
user_name|*Define the username being requested.*<br>Type:String, Order:1, Required=True
level|*Specify the challenge level of the requested game.  Where 1=puzzles with 6 characters or less and level=2 represents puzzles with greater than 6 characters.*<br>Type:String, Order:2, Required:True <br>
<b>Response Parameters |<b>Details</b>
accepted|*Indicates that the request was legal or valid.*<br>This response field Type:Boolean, Order=1, Required=True  
cause_code|*Indicates why request was not accepted.  See definition list of Cause Codes below.*<br>Type:Integer, Order=2, Required=False
game_id|*Indicates the game_id corresponding to the request.*<br>Type:String, Order:3, Required=False
word_size|*Indicates the size of the puzzle word for the game specified.*<br>Type:Integer, Order:4, Required=False
num_guesses|*Indicates the total number of guesses for the game specified.*<br>Type:Integer, Order:5, Required=False
num_misses|*Indicates the number of misses for the game specified.  Note that missing 6 guesses is a loss and the game ends.*<br>Type:Integer, Order:6, Required=False
miss_history|*Indicates the missed guess history for the game specified in the order of that the guesses were made. *<br>Type:String, Order:8, Required=False
current|*Indicates the current status of the puzzle.  This string shows correct guesses filled in and undiscovered letters represented by an underscore '_'. *<br>Type:String, Order:11, Required=False
resp_info|*This is text field that helps provide additional information about the results of the request.*<br>Type:String, Order:13, Required=False


<br>  
####/get\_high_scores  
<b>Description:</b>  This administrative function provides a list of the highest recorded single game scores in the database.  With this function, thyou may specify a a number of results to be returned.  If no specific number of results are requested the function will default to the top 7 highest scores.  <br> 
<b>Usage:</b> https://mf-game-api-v1.appspot.com/_ah/api/gameadmin/v1/get_high_scores?num_results=num_requested  
<b>Supported Methods:</b> `GET`  
><b> Example</b>:  
Request  
`GET https://mf-game-api-v1.appspot.com/_ah/api/gameadmin/v1/get_high_scores?num_results=4`  
Response:  
`200 OK`  
Show headers -  
```
{
 "accepted": true,
 "cause_code": "0",
 "resp_info": "Provide top 4 highest user scores. {user_name:mf3949;email:me@gmail.com;high_score:120; }  {user_name:test8;email:test8@gmail.com;high_score:110; }  {user_name:test4;email:test4@gmail.com;high_score:90; }  {user_name:test1;email:test1@gmail.com;high_score:80; } "
}  
``` 


Request<br>Parameter |Details
--------- |-------
num_requested|*Enter a value here to specify how many results to be returned.*<br>   Type:Integer, Order:1, Required:False
<b>Response Parameters |<b>Details</b>
accepted|*Indicates that the request was legal or valid.*<br>This response field Type:Boolean, Order=1, Required=True  
cause_code|*Indicates why request was not accepted.  See definition list of Cause Codes below.*<br>Type:Integer, Order=2, Required=False
resp_info|*This is text field that helps provide additional information about the results of the request.*<br>Type:String, Order:13, Required=False


<br>
####/get\_user_rankings  
<b>Description:</b>  This administrative function provides a list of the top 10 lifetime scores recorded in the database.  The results are in order of ranking from highest to lowest.  
<b>Usage:</b> https://mf-game-api-v1.appspot.com/_ah/api/gameadmin/v1/get_user_rankings  
<b>Supported Methods:</b> `GET`  
><b> Example</b>:  
Request
`GET https://mf-game-api-v1.appspot.com/_ah/api/gameadmin/v1/get_user_rankings`  
Response:  
`200 OK`  
Show headers -
```
{
 "accepted": true,
 "cause_code": "0",
 "resp_info": "This will provide top 10 users by total scores.  {user_name:test6;email:test6@gmail.com;high_score:500; }  {user_name:test4;email:test4@gmail.com;high_score:480; }  {user_name:test9;email:test9@gmail.com;high_score:380; }  {user_name:test2;email:test2@gmail.com;high_score:360; }  {user_name:test8;email:test8@gmail.com;high_score:350; }  {user_name:mf3949;email:me@gmail.com;high_score:280; }  {user_name:test1;email:test1@gmail.com;high_score:270; }  {user_name:test7;email:test7@gmail.com;high_score:250; }  {user_name:test3;email:test3@gmail.com;high_score:120; } "
}
``` 


Request<br>Parameter |Details
--------- |-------
none|*no required request parameters.*
<b>Response Parameters</b> |<b>Details</b>
accepted|*Indicates that the request was legal or valid.*<br>This response field Type:Boolean, Order=1, Required=True  
cause_code|*Indicates why request was not accepted.  See definition list of Cause Codes below.*<br>Type:Integer, Order=2, Required=False
resp_info|*This is text field that helps provide additional infomation about the results of the request.*<br>Type:String, Order:3, Required=False


<br>
####/get\_user_games  
<b>Description:</b>  This administrative function provides a list of all the <b>active games</b> in the database for the user specified in the request.  
<b>Usage:</b> https://mf-game-api-v1.appspot.com/_ah/api/gameadmin/v1/get_user_games?user_name=user_name  
<b>Supported Methods:</b> `GET`  
><b> Example</b>:  
Request  
`GET https://mf-game-api-v1.appspot.com/_ah/api/gameadmin/v1/get_user_games?user_name=test2`  
Response:  
`200 OK`  
headers:  
```
{
 "accepted": true,
 "cause_code": "0",
 "resp_info": "Listing active games for user test2. {game_id: ILZ9;level: 2;score: 40;active: 1;current: _E__E__EE;miss_history:  ;num_misses: 0;word_size: 9;}  {game_id: G6K3;level: 1;score: 20;active: 1;current: _O_C_;miss_history:  E;num_misses: 1;word_size: 5;}  {game_id: BNZK;level: 1;score: 20;active: 1;current: _O__E;miss_history:  C;num_misses: 1;word_size: 5;}  {game_id: C534;level: 1;score: 0;active: 1;current: _____;miss_history:  ;num_misses: 0;word_size: 5;}  {game_id: 3Y8L;level: 2;score: 0;active: 1;current: ___________;miss_history:  ;num_misses: 0;word_size: 11;} "
}
```

Request<br>Parameter |Details
--------- |-------
user_name|*Define the username being requested.*<br>Type:String, Order:1, Required=True
<b>Response Parameters</b> |<b>Details</b>
accepted|*Indicates that the request was legal or valid.*<br>This response field Type:Boolean, Order=1, Required=True  
cause_code|*Indicates why request was not accepted.  See definition list of Cause Codes below.*<br>Type:Integer, Order=2, Required=False
resp_info|*This is text field that helps provide additional infomation about the results of the request.*<br>Type:String, Order:13, Required=False


<br>
####/add_puzzle  
<b>Description:</b>  This administrative function allows a user to add a word to the puzzle database.  The application will determine if the puzzle word qualifies as a Level 1 or 2 puzzle upon its first usage.  Once a puzzle word is added to the puzzle database, it could be randomly chosen for any user, not just the user who submitted it to the database.  
<b>Usage:</b> https://mf-game-api-v1.appspot.com/_ah/api/gameadmin/v1/add_puzzle?puzzle=puzzle&user_name=user_name  
<b>Supported Methods:</b> `POST`  
><b> Example</b>:  
Request  
`POST https://mf-game-api-v1.appspot.com/_ah/api/gameadmin/v1/add_puzzle?puzzle=plate&user_name=test1`  
Response:  
`200 OK`  
headers:  
```
{
 "accepted": true,
 "cause_code": "0",
 "resp_info": "New puzzle PLATE added to datastore. "
}
```


Request<br>Parameter |Details
--------- |-------
user_name|*Define the username being requested.*<br>Type:String, Order:1, Required=True
puzzle|*Specify the puzzle to be added to the puzzle database.*<br>Type:String, Order:2, Required:True
<b>Response Parameters</b> |<b>Details</b>
accepted|*Indicates that the request was legal or valid.*<br>This response field Type:Boolean, Order=1, Required=True  
cause_code|*Indicates why request was not accepted.  See definition list of Cause Codes below.*<br>Type:Integer, Order=2, Required=False
resp_info|*This is text field that helps provide additional infomation about the results of the request.*<br>Type:String, Order:13, Required=False


<br>
<br>


###HangmanApi  
All functions begin with 'https://mf-game-api-v1.appspot.com/_ah/api/hangman/v1'. This group of API functions are specific to a single game and for game play. Each function is detailed below:

####/get\_game\_history  
<b>Description:</b>  This function will provide details about the active games games in the database for the username specified in the request.  This is the best function available to get all the game details.     
<b>Usage:</b> https://mf-game-api-v1.appspot.com/_ah/api/hangman/v1/get_game_history?game_id=game_id&user_name=user_name  
<b>Supported Methods:</b> `GET`  
><b> Example</b>:  
Request  
`GET https://mf-game-api-v1.appspot.com/_ah/api/hangman/v1/get_game_history?game_id=G6K3&user_name=test2`  
Response:  
`200 OK`  
Show headers -  
```
{
 "accepted": true,
 "cause_code": "0",
 "current": "_O_C_",
 "game_active": "1",
 "game_id": "G6K3",
 "guess_history": "EOC",
 "miss_history": "E",
 "num_guesses": "3",
 "num_misses": "1",
 "resp_info": "Game details for game G6K3",
 "score": "20",
 "word_size": "5"
}
```

Request<br>Parameter |Details
--------- |-------
user_name|*Define the username being requested.*<br>Type:String, Order:1, Required=True
game_id|*Define the game_id about which the details are being requested.*<br>Type:String, Order:2, Required:True
<b>Response Parameters</b> |<b>Details</b>
accepted|*Indicates that the request was legal or valid.*<br>This response field Type:Boolean, Order=1, Required=True  
cause_code|*Indicates why request was not accepted.  See definition list of Cause Codes below.*<br>Type:Integer, Order=2, Required=False
game_id|*Indicates the game_id corresponding to the request.*<br>Type:String, Order:3, Required=False
word_size|*Indicates the size of the puzzle word for the game specified.*<br>Type:Integer, Order:4, Required=False
num_guesses|*Indicates the total number of guesses for the game specified.*<br>Type:Integer, Order:5, Required=False
num_misses|*Indicates the number of misses for the game specified.  Note that missing 6 guesses is a loss and the game ends.*<br>Type:Integer, Order:6, Required=False
guess_history|*Indicates the over guess history for the game specified in the order of that the guesses were made.*<br>Type:String, Order:7, Required=False
miss_history|*Indicates the missed guess history for the game specified in the order of that the guesses were made. *<br>Type:String, Order:8, Required=False
game_active|*Indicates the current state of the game. This field as an integer value to represent the 3 possible states of a game. For this value, 1=Active, 2=Solved, 3=Game Over (hung hangman).*<br>Type:Integer, Order:9, Required=False
current|*Indicates the current status of the puzzle.  This string shows correct guesses filled in and undiscovered letters represented by an underscore '_'. *<br>Type:String, Order:11, Required=False
score|*Indicates the current score of the game specified. If the puzzle is successfully solved, this score is added to the user's toal lifetime score.  However, if the game is lost by a hung hangman (6 missed guesses), then this score is reset to zero and forfeited.*<br>Type:Integer, Order:12, Required=False
resp_info|*This is text field that helps provide additional infomation about the results of the request.*<br>Type:String, Order:13, Required=False


####/guess_letter  
<b>Description:</b>  This function is the primary game play function.  This function allows the user to guess a single letter for one of their own specified puzzles.  The `user_name` and `game_id` must correspond to a game in the database for the guess to be considered valid.  This function will return the results of the guess and the full details of the status of the game.  
<b>Usage:</b> https://mf-game-api-v1.appspot.com/_ah/api/hangman/v1/guess_letter?game_id=game_id&guess=guess&user_name=user_name  
<b>Supported Methods:</b> `POST`  
><b> Example</b>:  
Request  
`POST https://mf-game-api-v1.appspot.com/_ah/api/hangman/v1/guess_letter?game_id=ILZ9&guess=e&user_name=test2`  
Response:  
`200 OK`  
Show headers -  
```
{
 "accepted": true,
 "cause_code": "0",
 "current": "_E__E__EE",
 "game_active": "1",
 "game_id": "ILZ9",
 "guess_history": "E",
 "miss_history": "",
 "num_guesses": "1",
 "num_misses": "0",
 "resp_info": "Guess Correct! ",
 "score": "40",
 "word_size": "9"
}
``` 


Request<br>Parameter |Details
--------- |-------
user_name|*Define the username being requested.*<br>Type:String, Order:1, Required=True
game_id|*Define the game_id about which the details are being requested.*<br>Type:String, Order:2, Required:True
guess|*Specify the letter to be guessed for solving the puzzle.  Must be a single alpha character.*<br>Type:String, Order:3, Required:True
<b>Response Parameters</b> |<b>Details</b>
accepted|*Indicates that the request was legal or valid.*<br>This response field Type:Boolean, Order=1, Required=True  
cause_code|*Indicates why request was not accepted.  See definition list of Cause Codes below.*<br>Type:Integer, Order=2, Required=False
game_id|*Indicates the game_id corresponding to the request.*<br>Type:String, Order:3, Required=False
word_size|*Indicates the size of the puzzle word for the game specified.*<br>Type:Integer, Order:4, Required=False
num_guesses|*Indicates the total number of guesses for the game specified.*<br>Type:Integer, Order:5, Required=False
num_misses|*Indicates the number of misses for the game specified.  Note that missing 6 guesses is a loss and the game ends.*<br>Type:Integer, Order:6, Required=False
guess_history|*Indicates the over guess history for the game specified in the order of that the guesses were made.*<br>Type:String, Order:7, Required=False
miss_history|*Indicates the missed guess history for the game specified in the order of that the guesses were made. *<br>Type:String, Order:8, Required=False
game_active|*Indicates the current state of the game. This field as an integer value to represent the 3 possible states of a game. For this value, 1=Active, 2=Solved, 3=Game Over (hung hangman).*<br>Type:Integer, Order:9, Required=False
current|*Indicates the current status of the puzzle.  This string shows correct guesses filled in and undiscovered letters represented by an underscore '_'. *<br>Type:String, Order:11, Required=False
score|*Indicates the current score of the game specified. If the puzzle is successfully solved, this score is added to the user's toal lifetime score.  However, if the game is lost by a hung hangman (6 missed guesses), then this score is reset to zero and forfeited.*<br>Type:Integer, Order:12, Required=False
resp_info|*This is text field that helps provide additional infomation about the results of the request.*<br>Type:String, Order:13, Required=False


####/cancel_game  
<b>Description:</b>  This function is used to completely delete and cancel a game from the database regardless of the active state.  If a solved game is later deleted from the database using the `/cancel_game` function, the points gained from this game will not be removed from the user's lifetime total score.  This is considered a database cleanup function.    
<b>Usage:</b> https://mf-game-api-v1.appspot.com/_ah/api/hangman/v1/cancel_game?game_id=game_id&user_name=user_name  
<b>Supported Methods:</b> `DELETE`  
><b> Example</b>:  
Request  
`DELETE https://mf-game-api-v1.appspot.com/_ah/api/hangman/v1/cancel_game?game_id=C534&user_name=test2`  
Response:  
`200 OK`  
Show headers -
```
{
 "accepted": true,
 "cause_code": "0",
 "resp_info": "Canceling requested game:C534 "
}
```  
#

Request<br>Parameter |Details
--------- |-------
user_name|*Define the username being requested.*<br>Type:String, Order:1, Required=True
game_id|*Define the game_id about which the details are being requested.*<br>Type:String, Order:2, Required:True
<b>Response Parameters</b> |<b>Details</b>
accepted|*Indicates that the request was legal or valid.*<br>This response field Type:Boolean, Order=1, Required=True  
cause_code|*Indicates why request was not accepted.  See definition list of Cause Codes below.*<br>Type:Integer, Order=2, Required=False
resp_info|*This is text field that helps provide additional infomation about the results of the request.*<br>Type:String, Order:13, Required=False



<br>

##Notifications
###/Send\_Reminder\_Email  
<b>Description:</b>  This function is exclusively used as a cron job method which will email reminders only to users with active games in the system. Users without active games in the system will not get these reminder emails.  
<b>Usage:  No interaction with this API is needed. Reminder emails will be sent autonomously.</b>

https://mf-game-api-v1.appspot.com/crons/send_reminder<br>
<b>Supported Methods:</b> `GET`  
><b> Example</b>:  
Request:  
`GET https://mf-game-api-v1.appspot.com/crons/send_reminder`  
Response:  
`200 OK`  
Show headers -
```
{
 'Reminders Processed!'
}
```  

Request<br>Parameter |Details
--------- |-------
none|*no required request parameters.*
<b>Response Parameters</b> |<b>Details</b>
Response|'Reminders Processed!'  

<br>
##List of Cause Codes:
valid Cause Code:
   
Cause Code|Reason  
----------|------  
00|ok. Success  
01|No Such user exists  
02|No such game Exists  
03|Requested user name already exists  
04|Requested Puzzle already exists  
05|Guessed letter already in guess history  
06|User name and game ID mismatch  
07|Value provided for Guess is invalid  
08|undefined  
09|undefined  



