"use strict";

document.querySelector("#show-modal").addEventListener("click", (event)=>{
  document.querySelector(".room_create_modal").style.display = "block";
});

document.querySelector(".modal-default-button").addEventListener("click", (event)=>{
  document.querySelector(".room_create_modal").style.display = "none";
  let title = document.querySelector("#GameRoom_title").value;
  let capacity = Number(document.querySelector("#GameRoom_capacity").value);
  let password = document.querySelector("#GameRoom_password").value;
  let setup = document.querySelector("#GameRoom_setup").value;
  create_GameRoom(title, capacity, password, setup);
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

function create_GameRoom (title, capacity, password, setup) {
  Socket.emit('create_GameRoom', {
    'title': title,
    'password': password,
    'capacity': capacity,
    'setup': setup,
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
  let html = '';
  for (const [roomID, title] of Object.entries(room_list)) {
    html+='<tr><td>'+roomID+'</td><td>'+'<a href="#" id="room'+roomID+'">'+title+'</a></td></tr>';
  }
  tbody.innerHTML = html;
  for (const [roomID, title] of Object.entries(room_list)) {
    document.querySelector("#room"+roomID).addEventListener("click", ()=>{enter_GameRoom(Number(roomID))});
  }
});

Socket.on("multiple_login", (data)=>{
  alert("다른 곳에서 계정 접속이 시도되어 연결을 종료합니다.");
});

Socket.on("disconnect", (data)=>{
  alert("서버와의 연결이 종료되었습니다.");
});
