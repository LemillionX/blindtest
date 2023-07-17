
let socket = io();

let SONG_TIMEOUT;

$(document).ready(function() {
    $('#join-form').submit(function(event) {
        event.preventDefault();
        let username = $('#username').val();
        let token = $('#token').val();
        socket.emit('register', {username: username, token: token});
        $('#join-form').hide();
    });

    $('#playButton').click(function(){
        socket.emit('play_song');
    });

    $('#startButton').click(function(){
        socket.emit('start_game');
    });

    $('#againButton').click(function(){
        socket.emit('start_game');
        $("#game-panel").show();
        $("#again").hide();
    });

    $('#answerButton').click(function(){
        let answer = $('#answer').val();
        socket.emit('check_answer', {answer: answer});
    })

    $('#nextButton').click(function(){
        let song_container = document.getElementById("song-container")
        let video = document.getElementById("videoPlayer");
        if (song_container.style.opacity == 0){
            console.log("Let's see the answer");
            socket.emit('reveal_song');            
        } else {
            console.log("Moving on to the next song")
            video.pause();
            clearTimeout(SONG_TIMEOUT);
            song_container.style.opacity = 0;
            let song_name = document.getElementById("song-title");
            song_name.innerHTML = '';
            socket.emit('load_next_song');
        }

    })

});

socket.on('song_revealed', function(song){
    let song_container = document.getElementById("song-container")
    let video = document.getElementById("videoPlayer");
    let song_name = document.getElementById("song-title");
    song_name.innerHTML = song['name']
    video.src = song.src;
    video.currentTime = song.start;
    clearTimeout(SONG_TIMEOUT);
    video.play();
    song_container.style.opacity = 100;
    SONG_TIMEOUT = setTimeout(function(){video.pause();}, song.duration*1000);
});


socket.on('game_started', function(route){
    window.location.href=route;
    $("#game-panel").show();
    $("#again").hide();
    console.log("Game is starting...");
});

socket.on('message', function(data) {
    $('#messages').append('<li>' + data + '</li>')
});

socket.on('participants', function(data) {
    $('#participants').empty();
    data.participants.forEach(element => {
        $('#participants').append('<li>' + element + '</li>');
    });
});

socket.on('user_joined', function(data){
    $('#participants').append('<li>' + data.username + '</li>');
});

socket.on('show_start_button', function(){
    $('#start-form').show();
});

socket.on('song_playing', function(song) {
    let audio = document.getElementById("videoPlayer");
    audio.src = song.src;
    audio.currentTime = song.start;
    clearTimeout(SONG_TIMEOUT);
    audio.play();
    SONG_TIMEOUT = setTimeout(function(){audio.pause();}, song.duration*1000);
});

socket.on('game_ended', function(){
    let song_container = document.getElementById("song-container");
    song_container.style.opacity = 0;

    $("#game-panel").hide();
    $("#again").show();
});