"use strict";

Vue.component("modal", {
  template: "#modal-template"
});

let main = new Vue({
  el: "#main",
  data: {
    showModal: false,
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
}
document.querySelector("#leave_GameRoom_button").addEventListener("click", confirm_leave_GameRoom);

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
  main.inLobby = false;
});

Socket.on('leave_GameRoom_success', (data)=>{
  main.inLobby = true;
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
