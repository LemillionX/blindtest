# Blind Test mini-app
This project was made for fun and also as an opportunity to learn how to use <a href="https://flask.palletsprojects.com/en/2.3.x/"> Flask </a>.

## In-Game
### Launching
Run ``./src/main.py <port> `` to launch the app on the port ``<port>``. Then access the URL of the app. You should land on the index page where you can enter the room:
<div style="text-align:center">
    <img src=./img/index.png width="400">
</div>

### Waiting room
The first player to enter the room is the host. He will be in charge of starting the game, playing songs and skipping to the next song. Wait for all the players to enter the room before starting the game.
<div style="text-align:center">
    <img src=./img/room.png width="400">
</div>

### Guessing
Once the host pushed the <b> Play Song </b> button, the song starts playing and all the players can try to guess the media where the song comes from (or the title of the song, depending on your definition in the ``./static/songs/songs.json`` file, cf. section [Structure](#structure) for more details). A message will display to indicate if a player has found or not the answer.
<div style="text-align:center">
    <img src=./img/guess.png width="400">
    <img src=./img/submit.png width="400">
</div>

### Moving on 
The song is revealed when the host first click on the <b> Next Song </b> button. All the players cannot submit any answer anymore. Then, the host has to click again on <b> Next Song </b> button to load the next song, and we start the [Guessing](#guessing) step again. At the end of the game, the host can restart a new one.
<div style="text-align:center">
    <img src=./img/reveal.png width="400">
    <img src=./img/restart.png width="400">
</div>


## Structure
### Server
Server-side is handled in ``main.py``. 
You need to add a file ``config.json`` to define a ``SECRET_KEY`` and an ``IP_ADDRESS`` for the server.
```
{
    "SECRET_KEY": "your_secret_key",
    "IP_ADDRESS": "127.0.0.1"
}
```
There are three routes: <br>
 ``/``: the ``index.html`` route that asks confirmation for entering the ``/room/`` route <br>
``room``: the form to type the username and to join the game <br>
``game``: the game itself where you can submit answer <br>

### Client
Client-side is handled in the ``./static`` folder. Put your songs files in ``./static/songs/`` and add a file ``./static/songs/songs.json`` where you list all the songs as the following:
```
{
    'songs': [
        {
            'src': "./static/songs/your_song_a.mp4",
            'answer': ["valid_answer_a1", "valid_answer_a2"]
        }, 
        {
            'src': "./static/songs/your_song_b.mp4",
            'answer': ["valid_answer_b1"]
        },
    ]
}

```
### Building song list 
You can use ``lst_songs.py`` to automatically build the file ``./static/songs/songs.json``. If you do so, you need to create a folder in ``./static/songs/`` entitled with the correct answers separated by ``_`` and to put all the corresponding songs in it. You can use either ``.mp3`` or ``.mp4`` files.

```
/static/
├── songs/
│    ├── My Hero Academia_Boku no Hero Academia/
│    │       ├── mha_opening1.mp4 
│    │       ├── mha_opening2.mp4 
│    ├── The Simpson/
│    │       ├── the simpson op1 [HD].mp4
│    ├── songs.json
├── css/
├── js/
├── medias/
```

## Updates
### TO DO
<li> Fix blocking bug if timer of the last player is zero
<li> Add a channel where you can see all submitted answers if you have found 
<li> Add a time based score

### v0.3
Add song counter <br>
Add a metric to limit spelling mistakes' influence <br>
Replace ``-`` by ``_`` so that ``-`` can be used with ``lst_songs.py``<br>

### v0.2
Add a timer and a penalty system <br>
Trim answer to remove space at the beginning and at the end <br>
Enable `Enter` key for submission <br>
Remove user when the tab is closed/disconnected <br>
When using ``lst_songs.py``, you can now set a limit per anime <br>

### v0.1
Works using <a href="https://ngrok.com/"> ngrok </a> and ``localhost`` if there is no device with a slow interaction (e.g. web browser too slow to load) <br>
Caps don't matter <br>
No ``:``, ``-`` or ``.`` will lead to a valid answer if you use ``lst_songs.py`` to create your songlist <br>
Can submit multiple answer until you find the correct one <br>
