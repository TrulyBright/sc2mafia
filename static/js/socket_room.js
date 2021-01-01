'use strict';

function updateScroll () {
  let chatBox = document.querySelector('#messages');
  chatBox.scrollTop = chatBox.scrollHeight;
}

function addchat(message, color='orange') {
  let chatLog = document.getElementById('messages');
  let chat = document.createElement('li');
  chat.innerHTML = '<span style="color:' + color + '">' + message + '</span>';
  chatLog.appendChild(chat);
  updateScroll();
}

function send_message(event) {
  event.preventDefault();
  let chatInput = document.querySelector('#chat')
  let message = chatInput.value;
  Socket.emit('message', message);
  chatInput.value = '';
};

Socket.on('event', (data)=> {
  console.log(data);
  switch (data['type']) {
    case 'message':
      addchat(data['who']+': '+data['message'], 'white');
      break;
    case 'enter':
      addchat(data['who']+'님이 입장했습니다.');
      break;
    case 'leave':
      addchat(data['who']+'님이 퇴장했습니다.');
      break;
    case 'newhost':
      addchat(data['who']+'님이 방장이 되었습니다.');
      break;
    case 'game_over':
      addchat('게임이 끝났습니다. 승자들은 '+data['winner']+' 등입니다.');
      break;
    case 'role':
      addchat('당신의 직업은 '+data['role']+'입니다.');
      break;
    case 'state':
      switch (data['state']) {
        case 'MORNING':
          addchat('날이 밝았습니다.');
          break;
        case 'DISCUSSION':
          addchat('토론 시간입니다.');
          break;
        case 'DEFENSE':
          addchat('변론 시간입니다. '+data['who']+'님, 당신의 무죄를 주장하세요.')
          break;
        case 'VOTE':
          addchat('투표 시간입니다. "/투표 닉네임"을 입력하여 투표하세요. 명령어를 다시 입력하면 투표가 취소됩니다.');
          break;
        case 'VOTE_EXECUTION':
          addchat(data['who']+'님에게 사형을 선고하고 싶다면 "/유죄", 아니라면 "/무죄"를 입력하세요.');
          break;
        case 'EVENING':
          addchat('저녁이 되었습니다.');
          break;
        case 'NIGHT':
          addchat('밤이 되었습니다.');
          break;
      }
      break;
    case 'vote':
      addchat(data['voter']+'님이 '+data['voted']+'님에게 투표했습니다.');
      break;
    case 'vote_execution':
      addchat(data['voter']+'님이 투표했습니다.');
      break;
    case 'vote_cancel':
      addchat(data['voter']+'님이 투표를 취소했습니다.');
      break;
    case 'visit':
      if (data['target2']) {
        addchat('오늘 밤 '+data['target1']+'님을 '+data['target2']+'님에게 가게 합니다.')
      } else {
        addchat('오늘 밤 '+data['target1']+'님을 방문합니다.');
      }
      break;
    case 'alert':
      if (data['alert']) {
        addchat('오늘 밤 경계를 섭니다.');
      } else {
        addchat('오늘 밤은 쉬기로 합니다.');
      }
      break;
    case 'sound':
      switch (data['sound']) {
        case '간수':
          addchat('감옥에서 처형을 집행하는 라이플 소리를 들었습니다.', 'red');
          break;
        case '퇴역군인':
          addchat('이 조용한 마을에서 누군가 싸우는 소리를 들을 수 있었습니다.', 'red');
          break;
        case '경호원':
          addchat('격렬한 총격전의 소리를 들었습니다.', 'red');
          break;
        case '자경대원':
          addchat('마을을 완전히 뒤흔드는 총성을 들었습니다.', 'red');
          break;
        case '비밀조합장':
          addchat('두개골이 부서지는 역겨운 소리를 들었습니다.', 'red');
          break;
        case '버스기사':
          addchat('누군가가 차에 치이는 소리를 들었습니다.', 'red');
          break;
        case '마피아 일원':
          addchat('거리에 총성이 울리는 것을 들었습니다.', 'red');
          break;
        case '연쇄살인마':
          addchat('살인사건의 비명소리를 들었습니다.', 'red');
          break;
        case '대량학살자':
          if (data["number_of_murdered"] > 1) {
            addchat("체인톱이 살을 갈아버리는 끔찍한 불협화음을 들었습니다.", "red")
          } else {
            addchat('소름 끼치는 비명이 뒤섞인 소리를 들었습니다.', 'red');
          }
          break;
        case '방화범':
          addchat('불이 타오르는 소리와 함께 운명을 저주하는 비명소리를 들을 수 있었습니다.', 'red');
          break;
        case '잠입자':
          addchat('둔탁한 소리에 의한 짧은 몸부림과 힘든 기침을 들었습니다.', 'red');
          break;
        case '변장자':
          addchat("둔탁한 '쿵' 소리와 함께 미세한 총소리를 간신히 들을 수 있었습니다.", 'red');
          break;
        case '자살':
          addchat('밤에 한 발의 총성을 들었습니다.', 'red');
          break;
        case '마녀':
          addchat('소름끼치는 웃음소리가 들립니다.', 'red');
          break;
      }
      break;
    case 'wear_vest':
      if (data['wear_vest']) {
        addchat('방탄조끼를 입었습니다.');
      } else {
        addchat('방탄조끼를 벗었습니다.');
      }
      break;
    case 'Witch_control_success':
      addchat('당신은 '+data['target1']+'님을 '+data['target2']+'님에게 가도록 조종했습니다.', 'Orchid');
      break;
    case 'controlled_by_Witch':
      addchat('마녀에게 조종당하고 있습니다!', 'Orchid');
      break;
    case 'blocked':
      addchat('아리따운 누군가가 당신에게 찾아왔습니다. 당신은 그녀와 황홀한 밤을 보냈습니다. 능력이 차단되었습니다.', 'magenta');
      break;
    case 'oiling_success':
      addchat('당신은 '+data['target1']+'님에게 기름을 묻혔습니다.');
      break;
    case 'someone_visited_to_Veteran':
      addchat('누군가가 경계 중인 당신을 찾아왔습니다. 당신은 그와 유익한 거래를 하기 위해 총을 꺼냅니다.');
      break;
    case 'visited_Veteran':
      if (data['with_Bodyguard']) {
        addchat('당신이 방문한 대상은 경계 중인 퇴역군인이었습니다! 당신은 경호원과 함께 그와 싸웠습니다.');
      } else {
        addchat('당신이 방문한 대상은 경계 중인 퇴역군인이었습니다!');
      }
      break;
    case 'fighted_with_Bodyguard':
      addchat('당신을 방문한 대상은 경호원이 호위하고 있었습니다! 당신은 그의 경호원과 싸웠습니다. 당신은 거의 죽을 뻔했습니다!');
      break;
    case 'almost_suicide':
      addchat('당신은 당신의 목을 조르려 했습니다. 당신은 거의 죽을 뻔 했습니다!');
      break;
    case 'check_result':
      switch (data['role']) {
        case '탐정':
          if (typeof data['result'] === 'object') {
            let crimeList = [];
            for (const [crime, did] of Object.entries(data['result'])) {
              if (did) {
                crimeList.push(crime);
              }
            }
            addchat('대상이 저지른 범죄:' + crimeList);
          } else { // 정확한 직업을 알 수 있는 경우
            addchat('대상의 직업은' + data['result'] + '입니다.');
          }
          break;
        case '형사':
          addchat('대상은 오늘 밤' + data['result'] + '님을 방문했습니다.');
          break;
        case '감시자':
          addchat('오늘 밤 ' + data['result'] + '님이 대상을 방문했습니다.');
          break;
        case '보안관':
          if (data['result']) {
            addchat('대상은 ' + data['result'] + '입니다!!!');
          } else {
            addchat('대상은 수상하지 않습니다.');
          }
          break;
      }
      break;
    case "spy_result":
      addchat("오늘 밤 "+data["team"]+" 중 한 명이 "+data["result"]+"님을 방문했습니다.");
      break;
    case 'dead':
      if (data['dead_while_guarding']) {
        addchat('당신은 '+data['attacker']+'에게서 대상을 지키고 대신 사망했습니다.', 'red');
      } else {
        addchat('당신은 '+data['attacker']+'에게 죽었습니다.', 'red');
      }
      break;
    case 'attacked':
      addchat('당신은 '+data['attacker']+'에게 공격당했습니다.', 'red');
      break;
    case 'healed':
      addchat('당신은 '+data['attacker']+'에게 공격당했습니다.', 'red');
      setTimeout(addchat('그러나 '+data['healer']+'가 당신을 살려주었습니다.', 'green'), 500);
      break;
    case 'bodyguarded':
      addchat('당신은 '+data['attacker']+'에게 공격당했습니다.', 'red');
      setTimeout(addchat('그러나 경호원이 당신을 보호해주었습니다.', 'green'), 500);
      break;
    case 'suicide':
      switch (data['reason']) {
        case '고의':
          addchat('당신은 자살했습니다.');
          break;
        case '어릿광대':
          addchat('당신은 어릿광대를 죽였다는 죄책감에 못이겨 자살했습니다.');
          break;
      }
      break;
    default:
      addchat(data);
  }
});
