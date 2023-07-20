
let socket = io();

let SONG_TIMEOUT;

let GUESS_INTERVAL;
let HAS_STARTED_GUESSING = false;
let TIME_DISPLAY ="";
let HAS_FOUND = false;

function check_answer(){
    let answer = $('#answer').val();
    socket.emit('check_answer', {answer: answer});
}


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
        document.getElementById("answerButton").disabled = false;
        let answer = document.getElementById("answer");
        answer.disabled = false;
        answer.classList.remove('correct-answer');
        answer.classList.remove('wrong-answer');
        answer.value = '';
        $("#game-panel").show();
        $("#again").hide();
    });

    $('#answerButton').click(function(){
        check_answer();
    })

    $('#nextButton').click(function(){
        let song_container = document.getElementById("song-container")
        clearInterval(GUESS_INTERVAL);
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
    answer.classList.remove('correct-answer');
    answer.classList.remove('wrong-answer');
    answer.disabled = false;
    answer.value = '';
    document.getElementById("answerButton").disabled = false;
    HAS_STARTED_GUESSING = false;
    HAS_FOUND = false;
    clearInterval(GUESS_INTERVAL);
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
    document.getElementById("answerButton").disabled = true;
    let answer_input = document.getElementById("answer");
    answer_input.disabled = true;
    answer_input.classList.remove("wrong-answer");
    answer_input.classList.add('correct-answer');
    answer_input.value = answer_input.value + " "
    HAS_FOUND = true;
    clearInterval(GUESS_INTERVAL);
})

socket.on('wrong_answer', function(){
    let answer_input = document.getElementById("answer");

    if (!HAS_FOUND && parseInt(TIME_DISPLAY) <= 0 ){
        answer_input.disabled = true;
    }
    socket.emit('time_decreasing', {key:localStorage.getItem('CLIENT_KEY'), time:5});
    
    answer_input.classList.add('wrong-answer');
    answer_input.value = "";
})

socket.on('game_started', function(route){
    window.location.href=route;
    let answer = document.getElementById("answer")
    answer.classList.remove('correct-answer');
    answer.classList.remove('wrong-answer');
    answer.disabled = false;
    answer.value = '';
    $("#game-panel").show();
    $("#again").hide();
});

socket.on('participants', function(participants) {
    $('#participants').empty();
    for (let key in participants){
        let player = participants[key];
        let found_status;
        TIME_DISPLAY ="";

        if (HAS_STARTED_GUESSING) {
            TIME_DISPLAY = player.timer
        }

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
        $('#participants').append(`
            <li>
                <div class="player">
                    <div class="username"> ${player.username} </div>
                    <div class="score"> Score: ${player.score} </div> 
                    <div id='${key}-timer'> Time left: ${TIME_DISPLAY} s </div>
                    <div> ${found_status}</div>
                </div>
            </li>`);
    }
});

socket.on('user_joined', function(data){
    $('#participants').append('<li>' + data.username + '</li>');
    localStorage.setItem('CLIENT_KEY', data.key);
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
    if (!HAS_STARTED_GUESSING){
        HAS_STARTED_GUESSING = true;
        decrease_time(1);
        console.log("Timer starts now !");
    }
});

socket.on('game_ended', function(){
    let song_container = document.getElementById("song-container");
    song_container.style.opacity = 0;
    document.getElementById("videoPlayer").pause();
    $("#game-panel").hide();
    $("#again").show();
});

function decrease_time(timestep){
    clearInterval(GUESS_INTERVAL);
    GUESS_INTERVAL = setInterval(function(){
        let current_timer = document.getElementById(`${localStorage.getItem('CLIENT_KEY')}-timer`);
        if (parseInt(TIME_DISPLAY) == 0 ){
            console.log("Timer ended !");
            current_timer.innerHTML = `Time left: ${TIME_DISPLAY} s`;
            document.getElementById("answer").disabled = true;
            clearInterval(GUESS_INTERVAL);
            check_answer();
        } else {
            console.log('Time is decreasing...');
            socket.emit('time_decreasing', {key:localStorage.getItem('CLIENT_KEY'), time:timestep});
        }
    }, 1000);
}
