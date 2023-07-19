
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
        document.getElementById("answer").disabled = true;
        document.getElementById("answerButton").disabled = true;
        socket.emit('check_answer', {answer: answer});
    })

    $('#nextButton').click(function(){
        let song_container = document.getElementById("song-container")
        if (song_container.style.opacity == 0){
            socket.emit('reveal_song');            
        } else {
            socket.emit('load_next_song');
        }
    })
    
});

socket.on('next_song_loaded', function(){
    let song_container = document.getElementById("song-container")
    let video = document.getElementById("videoPlayer");
    video.pause();
    clearTimeout(SONG_TIMEOUT);
    song_container.style.opacity = 0;
    let song_name = document.getElementById("song-title");
    song_name.innerHTML = '';
    let answer = document.getElementById("answer")
    document.getElementById("answerButton").disabled = false;
    answer.disabled = false;
    answer.value = '';
    let answer_input = document.getElementById("answer");
    answer_input.classList.remove('correct-answer');
    answer_input.classList.remove('wrong-answer');
})

socket.on('song_revealed', function(song){
    document.getElementById("answer").disabled = true;
    document.getElementById("answerButton").disabled = true;
    
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


socket.on('correct_answer', function(){
    let answer_input = document.getElementById("answer");
    answer_input.classList.add('correct-answer');
    answer_input.value = answer_input.value + " "
})

socket.on('wrong_answer', function(){
    let answer_input = document.getElementById("answer");
    answer_input.classList.add('wrong-answer');
    answer_input.value = answer_input.value + " "
})

socket.on('game_started', function(route){
    window.location.href=route;
    $("#game-panel").show();
    $("#again").hide();
});

socket.on('message', function(data) {
    $('#messages').append('<li>' + data + '</li>')
});

socket.on('participants', function(participants) {
    $('#participants').empty();
    for (let key in participants){
        let player = participants[key];
        let found_status;
        switch (player.status) {
            case "has found":
                found_status = `<div style='color:green;'> ${player.status} </div>`;
                break;
            case "has not found":
                found_status = `<div style='color:red;'> ${player.status} </div>`;
                break;
            default:
                found_status = "";
        }
        $('#participants').append(`<li> <div class="player"> <div class="username"> ${player.username} </div> <div class="score"> Score: ${player.score} </div> ${found_status} </div> </li>`);
    }
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
    document.getElementById("videoPlayer").pause();
    $("#game-panel").hide();
    $("#again").show();
});