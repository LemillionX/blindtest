
let socket = io();

let timeOut;

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
    $('#startButton').show();
});

socket.on('song_playing', function(song) {
    let audio = document.getElementById("audioPlayer");
    audio.src = song.src;
    audio.currentTime = song.start;
    clearTimeout(timeOut);
    audio.play();
    timeOut = setTimeout(function(){audio.pause();}, song.duration*1000);
});