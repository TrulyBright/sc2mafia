"use strict";

Vue.component("modal", {
  template: "#modal-template"
});

Vue.component("lw-modal", {
  template: "#lw-modal-template"
});

let app = new Vue({
  el: "#main",
  data: {
    showModal: false,
    showLwModal: false,
    showSetupModal: false,
    showPlayerMenuModal: false,
    inLobby: true,
  }
});

let show_modal_button = document.querySelector('#show-modal');

show_modal_button.onclick = (event) => {
  let create_GameRoom_button = document.querySelector('.modal-default-button');
  create_GameRoom_button.onclick = (event) => {
    let title = document.querySelector('#GameRoom_title').value;
    let capacity = Number(document.querySelector('#GameRoom_capacity').value);
    let password = document.querySelector('#GameRoom_password').value;
    let setup = document.querySelector('#GameRoom_setup').value;
    create_GameRoom(title, capacity, password, setup);
  };
};

document.querySelector("#leave_GameRoom_button").addEventListener("click", confirm_leave_GameRoom);
document.querySelector("#start_button").addEventListener("click", (event)=>{
  Socket.emit("message", "/시작");
});
document.querySelector("#ready_button").addEventListener("click", (event)=>{
  Socket.emit("message", "/준비");
});
document.querySelector("#lw_button").addEventListener("click", (event)=>{
  Socket.emit("message", "/유언편집");
});
document.querySelector("#lw_submit").addEventListener("click", (event)=>{
  Socket.emit("message", "/유언편집 "+document.querySelector("#lw").value);
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
  app.inLobby = false;
});

Socket.on('leave_GameRoom_success', (data)=>{
  app.inLobby = true;
  let ul = document.querySelector("#messages");
  ul.innerHTML = "";
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

export { app };
