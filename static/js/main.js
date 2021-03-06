import {addchat} from "/static/js/socket_room.js"
"use strict";
window.onbeforeunload = function () {
  return true;
};
window.onunload = function () {
  return true;
};
document.querySelector("#show-modal").addEventListener("click", (event)=>{
  document.querySelector(".room_create_modal").style.display = "block";
});

document.querySelector(".modal-default-button").addEventListener("click", (event)=>{
  let title = document.querySelector("#GameRoom_title").value;
  let capacity = Number(document.querySelector("#GameRoom_capacity").value);
  // let password = document.querySelector("#GameRoom_password").value;
  if (!title) {
    alert("방제가 있어야 합니다.");
  } else {
    create_GameRoom(title, capacity);
    document.querySelector(".room_create_modal").style.display = "none";
  }
});

document.querySelector(".close_room_setup_modal_button").addEventListener("click", (event)=>{
  document.querySelector(".room_create_modal").style.display = "none";
});

document.querySelector("#leave_GameRoom_button").addEventListener("click", confirm_leave_GameRoom);
document.querySelector("#start_button").addEventListener("click", (event)=>{
  Socket.emit("message", "/시작");
});
document.querySelector("#ready_button").addEventListener("click", (event)=>{
  Socket.emit("message", "/준비");
});


function enter_GameRoom (roomID) {
  Socket.emit('enter_GameRoom', {
    'roomID': roomID,
  });
};

function confirm_leave_GameRoom () {
  if (confirm("정말로 방을 나가시겠습니까?")) {
    leave_GameRoom();
  }
}

function leave_GameRoom (){
  Socket.emit('leave_GameRoom', {});
}

function create_GameRoom (title, capacity) {
  Socket.emit('create_GameRoom', {
    'title': title,
    // 'password': password,
    'capacity': capacity,
  });
};

Socket.on('enter_GameRoom_success', (roomID)=> {
  document.querySelector(".lobby-menu").style.display = "none";
  document.querySelector(".room_list_section").style.display = "none";
  document.querySelector(".room_section").style.display = "block";
});

Socket.on('leave_GameRoom_success', (data)=>{
  let chatLog = document.querySelector("#messages");
  chatLog.innerHTML = "";
  document.querySelector(".lobby-menu").style.display = "block";
  document.querySelector(".room_list_section").style.display = "block";
  document.querySelector(".room_section").style.display = "none";
});

Socket.on('failed_to_enter_GameRoom', (data)=>{
  switch (data['reason']) {
    case 'full':
      alert('방이 꽉 찼습니다.');
      break;
    case 'No such room':
      alert('그런 방이 없습니다.');
      break;
    default:
      console.log(data);
  }
});

Socket.on('room_list', (room_list)=> {
  console.log(room_list)
  let tbody = document.querySelector('.room_list tbody');
  tbody.innerHTML = "";
  for (const [roomID, title] of Object.entries(room_list)) {
    let tr = document.createElement("tr");
    let roomID_column = document.createElement("td");
    let title_column = document.createElement("td");
    let a = document.createElement("a");
    a.setAttribute("href", "#");
    a.setAttribute("id", `room${roomID}`);
    a.innerText = title;
    title_column.appendChild(a);
    roomID_column.innerText = roomID;
    tr.appendChild(roomID_column);
    tr.appendChild(title_column);
    tbody.appendChild(tr);
  }
  for (const [roomID, title] of Object.entries(room_list)) {
    document.querySelector(`#room${roomID}`).addEventListener("click", ()=>{enter_GameRoom(Number(roomID))});
  }
});

Socket.on("multiple_login", (data)=>{
  alert("다른 곳에서 계정 접속이 시도되어 연결을 종료합니다.");
});

Socket.on("disconnect", (data)=>{
  alert("서버와의 연결이 종료되었습니다.");
});

Socket.on("online_users", (data)=>{
  let list = document.querySelector(".online_users_list");
  list.innerHTML = "";
  for (let nickname of data) {
    let li = document.createElement("li");
    li.innerText = nickname;
    list.appendChild(li);
  }
});
