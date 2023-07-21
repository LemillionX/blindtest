# Blind Test mini-app
This project was made for fun and also as an opportunity to learn how to use ``Flask``.

## Structure
### Server
Server-side is handled in ``main.py``. There are three routes: <br>
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
You can use ``lst_songs.py`` to automatically build the file ``./static/songs/songs.json``. If you do so, you need to create a folder in ``./static/songs/`` entitled with the correct answers separated by ``-`` and to put all the corresponding songs in it.

```
/static/
├── songs/
│    ├── My Hero Academia-Boku no Hero Academia/
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
<li> Add a timer and a penalty system
<li> Trim answer to remove space at the beginning and at the end
<li> Enable `Enter` key for submission
<li> Remove user when the tab is closed/disconnected
<li> Add a time based score


### v0.1
Works using ``ngrok`` and ``localhost`` if there is no device with a slow interaction (e.g. web browser too slow to load) <br>
Caps don't matter <br>
No ``:`` or ``-`` will be lead to a valid answer if you use ``lst_songs.py`` to create your songlist <br>
Can submit multiple answer until you find the correct one <br>
