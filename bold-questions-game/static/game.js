const socket = io();
let room = "";
let name = "";
let timerInterval;

// ====== CONNECTION STATUS ======
socket.on("connect", () => {
    document.getElementById("status").innerText = "🟢 متصل بالسيرفر";
    document.getElementById("status").className = "status online";
});

socket.on("disconnect", () => {
    document.getElementById("status").innerText = "🔴 الاتصال انقطع";
    document.getElementById("status").className = "status offline";
});

// ====== ROOM ======

function createRoom(){
    name = document.getElementById("name").value;
    if(!name) return alert("اكتب اسمك");
    socket.emit("create_room");
}

socket.on("room_created", (code)=>{
    room = code;
    document.getElementById("roomCode").innerText = "كود الغرفة: " + code;
    socket.emit("join_room", {room: room, name: name});
});

function joinRoom(){
    room = document.getElementById("roomInput").value;
    name = document.getElementById("name").value;
    if(!room || !name) return alert("اكتب الاسم وكود الغرفة");
    socket.emit("join_room", {room: room, name: name});
}

// ====== QUESTION ======

function newQuestion(){
    let level = document.getElementById("level").value;
    socket.emit("new_question", {room: room, level: level});
    startTimer(20);
}

socket.on("question", (q)=>{
    document.getElementById("questionBox").innerText = q;
});

// ====== PLAYERS ======

function addPoint(){
    socket.emit("add_point", {room: room, name: name});
}

socket.on("update_players", (players)=>{
    let html = "";
    for(let p in players){
        html += `<div>${p} : ${players[p]}</div>`;
    }
    document.getElementById("players").innerHTML = html;
});

// ====== CHAT ======

function sendChat(){
    let msg = document.getElementById("chatInput").value;
    if(!msg) return;
    socket.emit("chat", {room: room, name: name, msg: msg});
    document.getElementById("chatInput").value = "";
}

socket.on("chat", (data)=>{
    document.getElementById("chatBox").innerHTML +=
        `<div><b>${data.name}:</b> ${data.msg}</div>`;
});

socket.on("system_message", (msg)=>{
    document.getElementById("chatBox").innerHTML +=
        `<div class="system">${msg}</div>`;
});

// ====== TIMER ======

function startTimer(seconds){
    clearInterval(timerInterval);
    let time = seconds;
    timerInterval = setInterval(()=>{
        document.getElementById("timer").innerText = "⏳ " + time;
        time--;
        if(time < 0) clearInterval(timerInterval);
    },1000);
}

// ====== LEADERBOARD ======

function saveScores(){
    socket.emit("save_scores", {room: room});
}

socket.on("top_players", (data)=>{
    let html = "";
    data.forEach(p=>{
        html += `<div>${p[0]} : ${p[1]}</div>`;
    });
    document.getElementById("topPlayers").innerHTML = html;
});