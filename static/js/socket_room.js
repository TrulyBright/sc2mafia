// TODO: will_execute_the_jailed 이벤트 받기
'use strict';
document.querySelector("#lw_button").addEventListener("click", (event)=>{
  Socket.emit("message", "/유언편집");
  document.querySelector(".lw_modal").style.display = "block";
});
document.querySelector("#lw_submit").addEventListener("click", (event)=>{
  Socket.emit("message", "/유언편집 "+document.querySelector("#lw").value);
  document.querySelector(".lw_modal").style.display = "none";
});
document.querySelector("#setup_button").addEventListener("click", (event)=>{
  Socket.emit("message", "/설정요청");
  document.querySelector(".setup_modal").style.display = "block";
});
document.querySelector("#setup-cancel").addEventListener("click", (event)=>{
  document.querySelector(".setup_modal").style.display = "none";
});
document.querySelector("#setup-submit").addEventListener("click", (event)=>{
  document.querySelector(".setup_modal").style.display = "none";
  let formation = [];
  for (let tr of document.querySelector("#setup_list tbody").children) {
    formation.push(tr.innerText);
  }
  Socket.emit("setup", {
    "formation": formation,
    "options": {
      "role_setting": {
        "시민": {
          "bulletproof": document.querySelector(".시민 input[name='bulletproof']").checked,
          "win_1v1": document.querySelector(".시민 input[name='win_1v1']").checked,
          "recruitable": document.querySelector(".시민 input[name='recruitable']").checked
        },
        "보안관": {
          "detect_mafia_and_triad": document.querySelector(".보안관 input[name='detect_mafia_and_triad']").checked,
          "detect_SerialKiller": document.querySelector(".보안관 input[name='detect_SerialKiller']").checked,
          "detect_Arsonist": document.querySelector(".보안관 input[name='detect_Arsonist']").checked,
          "detect_Cult": document.querySelector(".보안관 input[name=detect_Cult]").checked,
          "detect_MassMurderer": document.querySelector(".보안관 input[name='detect_MassMurderer']").checked
        },
        "탐정": {
          "detect_exact_role": document.querySelector(".탐정 input[name='detect_exact_role']").checked
        },
        "형사": {
          "ignore_detection_immune": document.querySelector(".형사 input[name='ignore_detection_immune']").checked
        },
        "감시자": {
          "ignore_detection_immune": document.querySelector(".감시자 input[name='ignore_detection_immune']").checked
        },
        "의사": {
          "knows_if_attacked": document.querySelector(".의사 input[name='knows_if_attacked']").checked,
          "prevents_cult_conversion": document.querySelector(".의사 input[name='prevents_cult_conversion']").checked,
          "knows_if_culted": document.querySelector(".의사 input[name='knows_if_culted']").checked,
          "WitchDoctor_when_converted": document.querySelector(".의사 input[name='WitchDoctor_when_converted']").checked
        },
        "기생": {
          "cannot_be_blocked": document.querySelector(".기생 input[name='cannot_be_blocked']").checked,
          "detects_block_immune_target": document.querySelector(".기생 input[name='detects_block_immune_target']").checked,
          "recruitable": document.querySelector(".기생 input[name='recruitable']").checked,
        },
        "간수": {
          "execution_chance": Number(document.querySelector(".간수 input[name='execution_chance']:checked").value),
        },
        "자경대원": {
          "kill_chance": Number(document.querySelector(".자경대원 input[name='kill_chance']:checked").value),
          "suicides_if_shot_town": document.querySelector(".자경대원 input[name='suicides_if_shot_town']").checked
        },
        "비밀조합원": {
          "promoted_if_alone": document.querySelector(".비밀조합원 input[name='promoted_if_alone']").checked
        },
        "비밀조합장": {
          "recruit_chance": Number(document.querySelector(".비밀조합장 input[name='recruit_chance']:checked").value),
        },
        "정보원": {},
        "버스기사": {},
        "검시관": {
          "discover_all_targets": document.querySelector(".검시관 input[name='discover_all_targets']").checked,
          "discover_lw": document.querySelector(".검시관 input[name='discover_lw']").checked,
          "discover_death_type": document.querySelector(".검시관 input[name='discover_death_type']").checked,
          "discover_visitor_role": document.querySelector(".검시관 input[name='discover_visitor_role']").checked,
        },
        "경호원": {
          "offense_level": Number(document.querySelector(".경호원 input[name='offense_level_Bodyguard']:checked").value),
          "unhealable": document.querySelector(".경호원 input[name='unhealable']").checked,
          "prevents_conversion": document.querySelector(".경호원 input[name='prevents_conversion']").checked,
        },
        "퇴역군인": {
          "alert_chance": Number(document.querySelector(".퇴역군인 input[name='alert_chance']:checked").value),
          "offense_level": Number(document.querySelector(".퇴역군인 input[name='offense_level_Veteran']:checked").value),
        },
        "시장": {
          "lose_extra_votes": document.querySelector(".시장 input[name='lose_extra_votes']").checked,
          "extra_votes": Number(document.querySelector(".시장 input[name='extra_votes_Mayor']:checked").value),
          "unhealable": document.querySelector(".시장 input[name='unhealable']").checked,
        },
        "원수": {
          "lynch_chance": Number(document.querySelector(".원수 input[name='lynch_chance']:checked").value),
          "executions_per_group": Number(document.querySelector(".원수 input[name='executions_per_group']:checked").value),
          "unhealable": document.querySelector(".원수 input[name='unhealable']").checked,
        },
        "포고꾼": {},
        "마피아 일원": {},
        "조언자": {
          "promoted_if_no_Godfather": document.querySelector(".조언자 input[name='promoted_if_no_Godfather']").checked,
          "detect_exact_role": document.querySelector(".조언자 input[name='detect_exact_role']").checked,
          "becomes_mafioso": document.querySelector(".조언자 input[name='becomes_mafioso']").checked,
        },
        "대부": {
          "defense_level": Number(document.querySelector(".대부 input[name='defense_level_Godfather']:checked").value),
          "cannot_be_blocked": document.querySelector(".대부 input[name='cannot_be_blocked']").checked,
          "detection_immune": document.querySelector(".대부 input[name='detection_immune']").checked,
          "killable_without_mafioso": document.querySelector(".대부 input[name='killable_without_mafioso']").checked,
          // "becomes_mafioso": document.querySelector(".대부 input[name='becomes_mafioso']").checked,
        },
        // "변장자": {
        //   "hide_target_role": document.querySelector(".변장자 input[name='hide_target_role']").checked,
        //   "becomes_mafioso": document.querySelector(".변장자 input[name='becomes_mafioso']").checked,
        // }
        "매춘부": {
          "cannot_be_blocked": document.querySelector(".매춘부 input[name='cannot_be_blocked']").checked,
          "detects_block_immune_target": document.querySelector(".매춘부 input[name='detects_block_immune_target']").checked,
          "becomes_mafioso": document.querySelector(".매춘부 input[name='becomes_mafioso']").checked,
        },
        "조작자": {
          "detection_immune": document.querySelector(".조작자 input[name='detection_immune']").checked,
          "becomes_mafioso": document.querySelector(".조작자 input[name='becomes_mafioso']").checked,
        },
        "관리인": {
          "sanitize_chance": Number(document.querySelector(".관리인 input[name='sanitize_chance_Janitor']:checked").value),
          "becomes_mafioso": document.querySelector(".관리인 input[name='becomes_mafioso']").checked,
        },
        "협박자": {
          "can_talk_during_trial": document.querySelector(".협박자 input[name='can_talk_during_trial']").checked,
          "becomes_mafioso": document.querySelector(".협박자 input[name='becomes_mafioso']").checked,
        },
        "납치범": {
          "can_jail_members": document.querySelector(".납치범 input[name='can_jail_members']").checked,
          "becomes_mafioso": document.querySelector(".납치범 input[name='becomes_mafioso']").checked,
        },
        "요원": {
          "nights_between_shadowings": Number(document.querySelector(".요원 input[name='nights_between_shadowings_Agent']:checked").value),
          "becomes_mafioso": document.querySelector(".요원 input[name='becomes_mafioso']").checked,
        },
        "잠입자": {
          "hide_chance": Number(document.querySelector(".잠입자 input[name='hide_chance_Beguiler']:checked").value),
          "target_is_notified": document.querySelector(".잠입자 input[name='target_is_notified']").checked,
          "can_hide_behind_member": document.querySelector(".잠입자 input[name='can_hide_behind_member']").checked,
          "becomes_mafioso": document.querySelector(".잠입자 input[name='becomes_mafioso']").checked,
        },
        "홍곤": {},
        "백지선": {
          "promoted_if_no_Dragonhead": document.querySelector(".백지선 input[name='promoted_if_no_Dragonhead']").checked,
          "detect_exact_role": document.querySelector(".백지선 input[name='detect_exact_role']").checked,
          "becomes_enforcer": document.querySelector(".백지선 input[name='becomes_enforcer']").checked,
        },
        "용두": {
          "defense_level": Number(document.querySelector(".용두 input[name='defense_level_Dragonhead']:checked").value),
          "cannot_be_blocked": document.querySelector(".용두 input[name='cannot_be_blocked']").checked,
          "detection_immune": document.querySelector(".용두 input[name='detection_immune']").checked,
          "killable_without_enforcer": document.querySelector(".용두 input[name='killable_without_enforcer']").checked,
        },
        // "밀고자": {},
        "간통범": {
          "cannot_be_blocked": document.querySelector(".간통범 input[name='cannot_be_blocked']").checked,
          "detects_block_immune_target": document.querySelector(".간통범 input[name='detects_block_immune_target']").checked,
          "becomes_enforcer": document.querySelector(".간통범 input[name='becomes_enforcer']").checked,
        },
        "위조꾼": {
          "detection_immune": document.querySelector(".위조꾼 input[name='detection_immune']").checked,
          "becomes_enforcer": document.querySelector(".위조꾼 input[name='becomes_enforcer']").checked,
        },
        "향주": {
          "sanitize_chance": Number(document.querySelector(".향주 input[name='sanitize_chance']:checked").value),
          "becomes_enforcer": document.querySelector(".향주 input[name='becomes_enforcer']").checked,
        },
        "침묵자": {
          "can_talk_during_trial": document.querySelector(".침묵자 input[name='can_talk_during_trial']").checked,
          "becomes_enforcer": document.querySelector(".침묵자 input[name='becomes_enforcer']").checked,
        },
        "심문자": {
          "can_jail_members": document.querySelector(".심문자 input[name='can_jail_members']").checked,
          "becomes_enforcer": document.querySelector(".심문자 input[name='becomes_enforcer']").checked,
        },
        "선봉": {
          "nights_between_shadowings": Number(document.querySelector(".선봉 input[name='nights_between_shadowings']:checked").value),
          "becomes_enforcer": document.querySelector(".선봉 input[name='becomes_enforcer']").checked,
        },
        "사기꾼": {
          "hide_chance": Number(document.querySelector(".사기꾼 input[name='hide_chance']:checked").value),
          "target_is_notified": document.querySelector(".사기꾼 input[name='target_is_notified']").checked,
          "can_hide_behind_member": document.querySelector(".사기꾼 input[name='can_hide_behind_member']").checked,
          "becomes_enforcer": document.querySelector(".사기꾼 input[name='becomes_enforcer']").checked,
        },
        "생존자": {
          "bulletproof_chance": Number(document.querySelector(".생존자 input[name='bulletproof_chance']:checked").value),
        },
        "기억상실자": {
          "revealed": document.querySelector(".기억상실자 input[name='revealed']").checked,
          "cannot_remember_town": document.querySelector(".기억상실자 input[name='cannot_remember_town']").checked,
          "cannot_remember_mafia_and_triad": document.querySelector(".기억상실자 input[name='cannot_remember_mafia_and_triad']").checked,
          "cannot_remember_killing_role": document.querySelector(".기억상실자 input[name='cannot_remember_killing_role']").checked,
        },
        "어릿광대": {
          "randomly_suicide": document.querySelector(".어릿광대 input[name='randomly_suicide']").checked,
        },
        "처형자": {
          "becomes_Jester": document.querySelector(".처형자 input[name='becomes_Jester']").checked,
          "target_is_town": document.querySelector(".처형자 input[name='target_is_town']").checked,
          "win_if_survived": document.querySelector(".처형자 input[name='win_if_survived']").checked,
          "defense_level": Number(document.querySelector(".처형자 input[name='defense_level_Executioner']:checked").value),
        },
        "마녀": {
          "can_control_self": document.querySelector(".마녀 input[name='can_control_self']").checked,
          "target_is_notified": document.querySelector(".마녀 input[name='target_is_notified']").checked,
          "WitchDoctor_when_converted": document.querySelector(".마녀 input[name='WitchDoctor_when_converted']").checked,
        },
        "회계사": {
          "can_audit_mafia": document.querySelector(".회계사 input[name='can_audit_mafia']").checked,
          "can_audit_triad": document.querySelector(".회계사 input[name='can_audit_triad']").checked,
          "can_audit_night_immune": document.querySelector(".회계사 input[name='can_audit_night_immune']").checked,
          "audit_chance": Number(document.querySelector(".회계사 input[name='audit_chance']:checked").value),
        },
        "판사": {
          "court_chance": Number(document.querySelector(".판사 input[name='court_chance']:checked").value),
          "nights_between_court": Number(document.querySelector(".판사 input[name='nights_between_court']:checked").value),
          "extra_votes": Number(document.querySelector(".판사 input[name='extra_votes']:checked").value),
        },
        "이교도": {
          "can_convert_night_immune": document.querySelector(".이교도 input[name='can_convert_night_immune']").checked,
          "nights_between_conversion": Number(document.querySelector(".이교도 input[name='nights_between_conversion']:checked").value),
        },
        "요술사": {
          "save_chance": Number(document.querySelector(".요술사 input[name='save_chance']:checked").value),
          "night_between_save": Number(document.querySelector(".요술사 input[name='night_between_save']:checked").value),
          "detection_immune": document.querySelector(".요술사 input[name='detection_immune']").checked,
        },
        "연쇄살인마": {
          "defense_level": Number(document.querySelector(".연쇄살인마 input[name='defense_level_SerialKiller']:checked").value),
          "kill_blocker": document.querySelector(".연쇄살인마 input[name='kill_blocker']").checked,
          "win_if_1v1_with_Arsonist": document.querySelector(".연쇄살인마 input[name='win_if_1v1_with_Arsonist']").checked,
          "detection_immune": document.querySelector(".연쇄살인마 input[name='detection_immune']").checked,
        },
        "대량학살자": {
          "defense_level": Number(document.querySelector(".대량학살자 input[name='defense_level_MassMurderer']:checked").value),
          "can_visit_self": document.querySelector(".대량학살자 input[name='can_visit_self']").checked,
          "nights_between_murder": Number(document.querySelector(".대량학살자 input[name='nights_between_murder']:checked").value),
          "detection_immune": document.querySelector(".대량학살자 input[name='detection_immune']").checked,
        },
        "방화범": {
          "offense_level": Number(document.querySelector(".방화범 input[name='offense_level']:checked").value),
          "defense_level": Number(document.querySelector(".방화범 input[name='defense_level']:checked").value),
          "fire_spreads": document.querySelector(".방화범 input[name='fire_spreads']").checked,
          "target_is_notified": document.querySelector(".방화범 input[name='target_is_notified']").checked,
          "douse_blocker": document.querySelector(".방화범 input[name='douse_blocker']").checked,
        },
        "모든 무작위직": {
          "excludes_killing_role": document.querySelector(".모든무작위직 input[name='excludes_killing_role']").checked,
          "excludes_mafia": document.querySelector(".모든무작위직 input[name='excludes_mafia']").checked,
          "excludes_triad": document.querySelector(".모든무작위직 input[name='excludes_triad']").checked,
          "excludes_neutral": document.querySelector(".모든무작위직 input[name='excludes_neutral']").checked,
          "excludes_town": document.querySelector(".모든무작위직 input[name='excludes_town']").checked,
        },
        "시민 무작위직": {
          "excludes_killing_role": document.querySelector(".시민무작위직 input[name='excludes_killing_role']").checked,
          "excludes_government": document.querySelector(".시민무작위직 input[name='excludes_government']").checked,
          "excludes_investigative": document.querySelector(".시민무작위직 input[name='excludes_investigative']").checked,
          "excludes_protective": document.querySelector(".시민무작위직 input[name='excludes_protective']").checked,
          "excludes_power": document.querySelector(".시민무작위직 input[name='excludes_power']").checked,
        },
        "시민 행정직": {
          "excludes_citizen": document.querySelector(".시민행정직 input[name='excludes_citizen']").checked,
          "excludes_mason": document.querySelector(".시민행정직 input[name='excludes_mason']").checked,
          "excludes_mayor_and_marshall": document.querySelector(".시민행정직 input[name='excludes_mayor_and_marshall']").checked,
          "excludes_masonleader": document.querySelector(".시민행정직 input[name='excludes_masonleader']").checked,
          "excludes_crier": document.querySelector(".시민행정직 input[name='excludes_crier']").checked,
        },
        "시민 조사직": {
          "excludes_coroner": document.querySelector(".시민조사직 input[name='excludes_coroner']").checked,
          "excludes_sheriff": document.querySelector(".시민조사직 input[name='excludes_sheriff']").checked,
          "excludes_investigator": document.querySelector(".시민조사직 input[name='excludes_investigator']").checked,
          "excludes_detective": document.querySelector(".시민조사직 input[name='excludes_detective']").checked,
          "excludes_lookout": document.querySelector(".시민조사직 input[name='excludes_lookout']").checked,
        },
        "시민 방어직": {
          "excludes_bodyguard": document.querySelector(".시민방어직 input[name='excludes_bodyguard']").checked,
          "excludes_doctor": document.querySelector(".시민방어직 input[name='excludes_doctor']").checked,
          "excludes_escort": document.querySelector(".시민방어직 input[name='excludes_escort']").checked,
        },
        "시민 살인직": {
          "excludes_veteran": document.querySelector(".시민살인직 input[name='excludes_veteran']").checked,
          "excludes_jailor": document.querySelector(".시민살인직 input[name='excludes_jailor']").checked,
          "excludes_bodyguard": document.querySelector(".시민살인직 input[name='excludes_bodyguard']").checked,
          "excludes_vigilante": document.querySelector(".시민살인직 input[name='excludes_vigilante']").checked,
        },
        "시민 능력직": {
          "excludes_veteran": document.querySelector(".시민능력직 input[name='excludes_veteran']").checked,
          "excludes_spy": document.querySelector(".시민능력직 input[name='excludes_spy']").checked,
          "excludes_jailor": document.querySelector(".시민능력직 input[name='excludes_jailor']").checked,
        },
        "마피아 무작위직": {
          "excludes_killing_role": document.querySelector(".마피아무작위직 input[name='excludes_killing_role']").checked,
        },
        "마피아 살인직": {
          "excludes_kidnapper": document.querySelector(".마피아살인직 input[name='excludes_kidnapper']").checked,
          "excludes_mafioso": document.querySelector(".마피아살인직 input[name='excludes_mafioso']").checked,
          "excludes_godfather": document.querySelector(".마피아살인직 input[name='excludes_godfather']").checked,
        },
        "마피아 지원직": {
          "excludes_blackmailer": document.querySelector(".마피아지원직 input[name='excludes_blackmailer']").checked,
          "excludes_kidnapper": document.querySelector(".마피아지원직 input[name='excludes_kidnapper']").checked,
          "excludes_consort": document.querySelector(".마피아지원직 input[name='excludes_consort']").checked,
          "excludes_consigliere": document.querySelector(".마피아지원직 input[name='excludes_consigliere']").checked,
          "excludes_agent": document.querySelector(".마피아지원직 input[name='excludes_agent']").checked,
        },
        "마피아 속임수직": {
          "excludes_framer": document.querySelector(".마피아속임수직 input[name='excludes_framer']").checked,
          "excludes_janitor": document.querySelector(".마피아속임수직 input[name='excludes_janitor']").checked,
          "excludes_beguiler": document.querySelector(".마피아속임수직 input[name='excludes_beguiler']").checked,
        },
        "삼합회 무작위직": {
          "excludes_killing_role": document.querySelector(".삼합회무작위직 input[name='excludes_killing_role']").checked,
        },
        "삼합회 살인직": {
          "excludes_interrogator": document.querySelector(".삼합회살인직 input[name='excludes_interrogator']").checked,
          "excludes_enforcer": document.querySelector(".삼합회살인직 input[name='excludes_enforcer']").checked,
          "excludes_dragonhead": document.querySelector(".삼합회살인직 input[name='excludes_dragonhead']").checked,
        },
        "삼합회 지원직": {
          "excludes_silencer": document.querySelector(".삼합회지원직 input[name='excludes_silencer']").checked,
          "excludes_interrogator": document.querySelector(".삼합회지원직 input[name='excludes_interrogator']").checked,
          "excludes_liaison": document.querySelector(".삼합회지원직 input[name='excludes_liaison']").checked,
          "excludes_administrator": document.querySelector(".삼합회지원직 input[name='excludes_administrator']").checked,
          "excludes_vanguard": document.querySelector(".삼합회지원직 input[name='excludes_vanguard']").checked,
        },
        "삼합회 속임수직": {
          "excludes_forger": document.querySelector(".삼합회속임수직 input[name='excludes_forger']").checked,
          "excludes_incensemaster": document.querySelector(".삼합회속임수직 input[name='excludes_incensemaster']").checked,
          "excludes_deceiver": document.querySelector(".삼합회속임수직 input[name='excludes_deceiver']").checked,
        },
        "중립 무작위직": {
          "excludes_killing_role": document.querySelector(".중립무작위직 input[name='excludes_killing_role']").checked,
          "excludes_evil": document.querySelector(".중립무작위직 input[name='excludes_evil']").checked,
          "excludes_benign": document.querySelector(".중립무작위직 input[name='excludes_benign']").checked,
        },
        "중립 살인직": {
          "excludes_serialkiller": document.querySelector(".중립살인직 input[name='excludes_serialkiller']").checked,
          "excludes_arsonist": document.querySelector(".중립살인직 input[name='excludes_arsonist']").checked,
          "excludes_massmurderer": document.querySelector(".중립살인직 input[name='excludes_massmurderer']").checked,
        },
        "중립 악": {
          "excludes_killing_role": document.querySelector(".중립악 input[name='excludes_killing_role']").checked,
          "excludes_cults": document.querySelector(".중립악 input[name='excludes_cults']").checked,
          "excludes_witch": document.querySelector(".중립악 input[name='excludes_witch']").checked,
          "excludes_judge": document.querySelector(".중립악 input[name='excludes_judge']").checked,
          "excludes_auditor": document.querySelector(".중립악 input[name='excludes_auditor']").checked,
        },
        "중립 선": {
          "excludes_survivor": document.querySelector(".중립선 input[name='excludes_survivor']").checked,
          "excludes_jester": document.querySelector(".중립선 input[name='excludes_jester']").checked,
          "excludes_executioner": document.querySelector(".중립선 input[name='excludes_executioner']").checked,
          "excludes_amnesiac": document.querySelector(".중립선 input[name='excludes_amnesiac']").checked,
        }
      },
      "time_setup": {
        "day_time": Number(document.querySelector(".day_time_slider").value),
        "night_time": Number(document.querySelector(".night_time_slider").value),
        "discussion_time": Number(document.querySelector(".discussion_time_slider").value),
        "court_time": Number(document.querySelector(".court_time_slider").value),
      },
      "select_setup": {
        "initial_state": document.querySelector(".select_setup select[name='initial_state']").value,
        "night_type": document.querySelector(".select_setup select[name='night_type']").value,
      },
      "checkbox_setup": {
        "whisper_allowed": document.querySelector(".checkbox_setup input[name='whisper_allowed']").checked,
        "use_discussion_time": document.querySelector(".checkbox_setup input[name='use_discussion_time']").checked,
        "pause_daytime": document.querySelector(".checkbox_setup input[name='pause_daytime']").checked,
        "use_defense_time": document.querySelector(".checkbox_setup input[name='use_defense_time']").checked,
      }
    }
  });
});

document.querySelector(".message_input_form").addEventListener("submit", send_message)
let now_playing = null;

function updateScroll () {
  let chatBox = document.querySelector('#messages');
  let scrolledToBottom = chatBox.scrollHeight-chatBox.clientHeight<=chatBox.scrollTop+35;
  if (scrolledToBottom) {
    chatBox.scrollTop = chatBox.scrollHeight;
  }
}
let blop = new Audio("/static/music/blop.mp3");

setInterval(updateScroll);

function addchat(message, color='orange', background_color=null) {
  let chatLog = document.getElementById('messages');
  let chat = document.createElement('li');
  let span = document.createElement("span");
  if (background_color) {
    chat.style.backgroundColor = background_color;
  }
  span.setAttribute("style", `color:${color}`);
  if (color=="orange") {
    span.innerHTML = message;
  } else {
    span.innerText = message;
  }
  chat.appendChild(span);
  chatLog.appendChild(chat);
  blop.play();
}

function send_message(event) {
  event.preventDefault();
  let chatInput = document.querySelector('#chat')
  let message = chatInput.value;
  if (message) {
    Socket.emit('message', message);
  }
  chatInput.value = '';
};

function colored(role_name) {
  let color = "";
  switch (role_name) {
    case "경호원":
      color = "00CC66";
      break;
    case "버스기사":
      color = "55CC11";
      break;
    case "시민":
      color = "33CC33";
      break;
    case "검시관":
      color = "00DD55";
      break;
    case "포고꾼":
      color = "66CC33";
      break;
    case "형사":
      color = "00FF44";
      break;
    case "의사":
      color = "00FF00";
      break;
    case "기생":
      color = "00FF00";
      break;
    case "탐정":
      color = "00FF66";
      break;
    case "간수":
      color = "66CC00";
      break;
    case "감시자":
      color = "44FF00";
      break;
    case "원수":
      color = "23EF32";
      break;
    case "비밀조합":
    case "비밀조합원":
      color = "00FF44";
      break;
    case "비밀조합장":
      color = "22FF77";
      break;
    case "시장":
      color = "44FF44";
      break;
    case "보안관":
      color = "00FF00";
      break;
    case "정보원":
      color = "66AA00";
      break;
    case "나무 그루터기":
      color = "00FF00";
      break;
    case "퇴역군인":
      color = "AAFF55";
      break;
    case "자경대원":
      color = "88CC00";
      break;
    case "판사":
      color = "BB6655";
      break;
    case "회계사":
      color = "bbcc88";
      break;
    case "요술사":
      color = "aa55ff";
      break;
    case "대량학살자":
      color = "bb4455";
      break;
    case "이교도":
      color = "bb44aa";
      break;
    case "기억상실자":
      color = "66ffcc";
      break;
    case "처형자":
      color = "aaccff";
      break;
    case "방화범":
      color = "ffaa00";
      break;
    case "마녀":
      color = "6622cc";
      break;
    case "어릿광대":
      color = "ffaaff";
      break;
    case "생존자":
      color = "ffff00";
      break;
    case "연쇄살인마":
      color = "ff00cc";
      break;
    case "잠입자":
      color = "bb3355";
      break;
    case "요원":
      color = "ff2244";
      break;
    case "납치범":
      color = "aa3333";
      break;
    case "변장자":
      color = "dd6644";
      break;
    case "협박자":
      color = "dd0000";
      break;
    case "관리인":
      color = "ff3333";
      break;
    case "조작자":
      color = "dd6600"
      break;
    case "조언자":
      color = "ff5533";
      break;
    case "매춘부":
      color = "ff0000";
      break;
    case "대부":
      color = "ff4488";
      break;
    case "마피아":
    case "마피아 일원":
      color = "cc0000";
      break;
    case "사기꾼":
      color = "6969BB";
      break;
    case "선봉":
      color = "697aff";
      break;
    case "심문자":
      color = "4a62aa";
      break;
    case "밀고자":
      color = "6295dd";
      break;
    case "침묵자":
      color = "2c58dd";
      break;
    case "향주":
      color = "5b84ff";
      break;
    case "위조꾼":
      color = "2c95dd";
      break;
    case "백지선":
      color = "5b99ff";
      break;
    case "간통범":
      color = "3366ff";
      break;
    case "용두":
      color = "9f8eff";
      break;
    case "삼합회":
    case "홍곤":
      color = "2851cc";
      break;
  }
  return `<span style='color:#${color}'>${role_name}</span>`;
};

function swap_audio(audio_name) {
  switch (audio_name) {
    case "court_normal":
      if (now_playing) {
        now_playing.pause();
      }
      now_playing = new Audio("/static/music/Ace Attorney - Court Suite 3.mp3");
      now_playing.play();
      addchat("음악 재생: 역전재판 주제곡 - Court Suite 3");
      break;
    case "court_with_lynch":
      if (now_playing) {
        now_playing.pause();
      }
      now_playing = new Audio("/static/music/Phoenix Wright Ace Attorney OST - Pressing Pursuit Cornered.mp3");
      now_playing.play();
      addchat("음악 재생: 역전재판 주제곡 - Pressing Pursuit Cornered");
      break;
    case "mayor_normal":
      if (now_playing) {
        now_playing.pause();
      }
      now_playing = new Audio("/static/music/Hail to the Chief.mp3");
      now_playing.play();
      addchat("음악 재생: 미국 대통령 헌정곡");
      break;
    case "marshall_normal":
      if (now_playing) {
        now_playing.pause();
      }
      if (Math.random()>=0.5) {
        now_playing = new Audio("/static/music/National Anthem of USSR.mp3");
        now_playing.play();
        addchat("음악 재생: 소련 국가");
      } else {
        now_playing = new Audio("/static/music/National Anthem of North Korea Instrumental.mp3");
        now_playing.play();
        addchat("음악 재생: 북한 국가");
      }
      break;
    default:
      addchat(data["music"]);
  }
}

Socket.on("player_list", (data)=>{
  console.log(data);
  let player_list = document.querySelector(".player_list");
  player_list.innerHTML = "";
  if (data["inGame"]) {
    for (let player of data["player_list"]) {
      let nickname = player[0];
      let alive = player[1];
      let role = player[2];
      let div = document.createElement("div");
      let del = document.createElement("del");
      let a = document.createElement("a");
      a.setAttribute("href", "#");
      a.innerHTML = nickname + (role ? " | " + colored(role) : "");
      if (!alive) {
        del.appendChild(a);
        div.appendChild(del);
      } else {
        div.appendChild(a);
      }
      player_list.appendChild(div);
    }
  } else {
    for (let player of data["player_list"]) {
      let nickname = player[0];
      let readied = player[1];
      let div = document.createElement("div");
      let a = document.createElement("a");
      a.setAttribute("href", "#");
      a.innerHTML = nickname;
      if (readied) {
        a.style.backgroundColor = "#6B6B84";
      }
      div.appendChild(a);
      player_list.appendChild(div);
    }
  }
});

Socket.on('event', (data)=> {
  console.log(data);
  switch (data['type']) {
    case "will_start":
      addchat("게임이 "+data["in"]+"초 후에 시작됩니다...");
      break;
    case "simulation":
      for (let line of data["result"]) {
        let slot = line[0];
        let role = line[1];
        addchat(`${slot}번 칸: ${colored(role)}`);
      }
      break;
    case "formation":
      addchat("===직업 구성 시작===");
      for (let line of data["formation"]) {
        if (line.includes(" ") && line!="마피아 일원") {
          addchat(`${colored(line.split(" ")[0])} ${line.split(" ")[1]}`);
        } else {
          addchat(`${colored(line)}`);
        }
      }
      addchat("===직업 구성 끝 ===");
      break;
    case "setup":
      if (!data["setup"]) {
        break;
      }
      document.querySelector("#setup_list tbody").innerHTML = "";
      for (let role_name of data["setup"]["formation"]) {
        if (role_name.includes(" ") && role_name!="마피아 일원") {
          if (role_name.includes("시민")) {
            role_name = role_name.replace("시민", colored("시민"));
          } else if (role_name.includes("마피아")) {
            role_name = role_name.replace("마피아", colored("마피아"));
          } else if (role_name.includes("삼합회")) {
            role_name = role_name.replace("삼합회", colored("삼합회"));
          } else if (role_name.includes("중립")) {
            role_name = role_name.replace("중립", colored("중립"));
          }
        } else {
          role_name = colored(role_name)
        }
        let tr = document.createElement("tr");
        tr.innerHTML = "<a href='#'>"+role_name+"</a>";
        tr.addEventListener("click", function () {
          document.querySelector("#setup_list tbody").removeChild(this);
        });
        document.querySelector("#setup_list tbody").appendChild(tr);
      }
      document.querySelector(".시민 input[name='bulletproof']").checked=data["setup"]["options"]["role_setting"]["시민"]["bulletproof"];
      document.querySelector(".시민 input[name='win_1v1']").checked=data["setup"]["options"]["role_setting"]["시민"]["win_1v1"];
      document.querySelector(".보안관 input[name='detect_mafia_and_triad']").checked=data["setup"]["options"]["role_setting"]["보안관"]["detect_mafia_and_triad"];
      document.querySelector(".보안관 input[name='detect_SerialKiller']").checked=data["setup"]["options"]["role_setting"]["보안관"]["detect_SerialKiller"];
      document.querySelector(".보안관 input[name='detect_Arsonist']").checked=data["setup"]["options"]["role_setting"]["보안관"]["detect_Arsonist"];
      document.querySelector(".보안관 input[name=detect_Cult]").checked=data["setup"]["options"]["role_setting"]["보안관"]["detect_Cult"];
      document.querySelector(".의사 input[name='knows_if_attacked']").checked=data["setup"]["options"]["role_setting"]["의사"]["knows_if_attacked"];
      document.querySelector(".의사 input[name='prevents_cult_conversion']").checked=data["setup"]["options"]["role_setting"]["의사"]["prevents_cult_conversion"];
      document.querySelector(".의사 input[name='knows_if_culted']").checked=data["setup"]["options"]["role_setting"]["의사"]["knows_if_culted"];
      document.querySelector(".기생 input[name='cannot_be_blocked']").checked=data["setup"]["options"]["role_setting"]["기생"]["cannot_be_blocked"];
      document.querySelector(".기생 input[name='detects_block_immune_target']").checked=data["setup"]["options"]["role_setting"]["기생"]["detects_block_immune_target"];
      document.querySelector(".기생 input[name='recruitable']").checked=data["setup"]["options"]["role_setting"]["기생"]["recruitable"];
      document.querySelector(`.간수 input[name='execution_chance'][value="${data['setup']['options']['role_setting']['간수']['execution_chance']}"`).checked = true;
      document.querySelector(`.자경대원 input[name='kill_chance'][value="${data['setup']['options']['role_setting']['자경대원']['kill_chance']}"`).checked = true;
      document.querySelector(`.비밀조합장 input[name='recruit_chance'][value="${data['setup']['options']['role_setting']['비밀조합장']['recruit_chance']}"`).checked = true;
      document.querySelector(".검시관 input[name='discover_all_targets']").checked=data["setup"]["options"]["role_setting"]["검시관"]["discover_all_targets"];
      document.querySelector(".검시관 input[name='discover_lw']").checked=data["setup"]["options"]["role_setting"]["검시관"]["discover_lw"];
      document.querySelector(".검시관 input[name='discover_death_type']").checked=data["setup"]["options"]["role_setting"]["검시관"]["discover_death_type"];
      document.querySelector(".검시관 input[name='discover_visitor_role']").checked=data["setup"]["options"]["role_setting"]["검시관"]["discover_visitor_role"];
      document.querySelector(`.경호원 input[name='offense_level_Bodyguard'][value="${data['setup']['options']['role_setting']['경호원']['offense_level']}"`).checked = true;
      document.querySelector(".경호원 input[name='unhealable']").checked=data["setup"]["options"]["role_setting"]['경호원']["unhealable"];
      document.querySelector(".경호원 input[name='prevents_conversion']").checked=data["setup"]["options"]["role_setting"]['경호원']["prevents_conversion"];
      document.querySelector(`.퇴역군인 input[name='alert_chance'][value="${data['setup']['options']['role_setting']['퇴역군인']['alert_chance']}"`).checked = true;
      document.querySelector(`.퇴역군인 input[name='offense_level_Veteran'][value="${data['setup']['options']['role_setting']['퇴역군인']['offense_level']}"`).checked = true;
      document.querySelector(".시장 input[name='lose_extra_votes']").checked=data["setup"]["options"]["role_setting"]["시장"]["lose_extra_votes"];
      document.querySelector(`.시장 input[name='extra_votes_Mayor'][value="${data['setup']['options']['role_setting']['시장']['extra_votes']}"`).checked = true;
      document.querySelector(".시장 input[name='unhealable']").checked=data["setup"]["options"]["role_setting"]['시장']["unhealable"];
      document.querySelector(`.원수 input[name='lynch_chance'][value="${data['setup']['options']['role_setting']['원수']['lynch_chance']}"`).checked = true;
      document.querySelector(`.원수 input[name='executions_per_group'][value="${data['setup']['options']['role_setting']['원수']['executions_per_group']}"`).checked = true;
      document.querySelector(".원수 input[name='unhealable']").checked=data["setup"]["options"]["role_setting"]['원수']["unhealable"];
      document.querySelector(".조언자 input[name='promoted_if_no_Godfather']").checked=data["setup"]["options"]["role_setting"]["조언자"]["promoted_if_no_Godfather"];
      document.querySelector(".조언자 input[name='detect_exact_role']").checked=data["setup"]["options"]["role_setting"]["조언자"]["detect_exact_role"];
      document.querySelector(".조언자 input[name='becomes_mafioso']").checked=data["setup"]["options"]["role_setting"]["조언자"]["becomes_mafioso"];
      document.querySelector(`.대부 input[name='defense_level_Godfather'][value="${data['setup']['options']['role_setting']['대부']['defense_level']}"`).checked = true;
      document.querySelector(".대부 input[name='cannot_be_blocked']").checked=data["setup"]["options"]["role_setting"]['대부']["cannot_be_blocked"];
      document.querySelector(".대부 input[name='detection_immune']").checked=data["setup"]["options"]["role_setting"]['대부']["detection_immune"];
      document.querySelector(".대부 input[name='killable_without_mafioso']").checked=data["setup"]["options"]["role_setting"]['대부']["killable_without_mafioso"];
      // document.querySelector(".대부 input[name='becomes_mafioso']").checked=data["setup"]["options"]["role_setting"]['대부']["becomes_mafioso"];
      // document.querySelector(".변장자 input[name='hide_target_role']").checked=data["setup"]["options"]["role_setting"]["변장자"]["hide_target_role"];
      // document.querySelector(".변장자 input[name='becomes_mafioso']").checked=data["setup"]["options"]["role_setting"]["변장자"]["becomes_mafioso"];
      document.querySelector(".매춘부 input[name='cannot_be_blocked']").checked=data["setup"]["options"]["role_setting"]["매춘부"]["cannot_be_blocked"];
      document.querySelector(".매춘부 input[name='detects_block_immune_target']").checked=data["setup"]["options"]["role_setting"]["매춘부"]["detects_block_immune_target"];
      document.querySelector(".매춘부 input[name='becomes_mafioso']").checked=data["setup"]["options"]["role_setting"]["매춘부"]["becomes_mafioso"];
      document.querySelector(".조작자 input[name='detection_immune']").checked=data["setup"]["options"]["role_setting"]["조작자"]["detection_immune"];
      document.querySelector(".조작자 input[name='becomes_mafioso']").checked=data["setup"]["options"]["role_setting"]["조작자"]["becomes_mafioso"];
      document.querySelector(`.관리인 input[name='sanitize_chance_Janitor'][value="${data['setup']['options']['role_setting']['관리인']['sanitize_chance']}"`).checked = true;
      document.querySelector(".관리인 input[name='becomes_mafioso']").checked=data["setup"]["options"]["role_setting"]['관리인']["becomes_mafioso"];
      document.querySelector(".협박자 input[name='can_talk_during_trial']").checked=data["setup"]["options"]["role_setting"]["협박자"]["can_talk_during_trial"];
      document.querySelector(".협박자 input[name='becomes_mafioso']").checked=data["setup"]["options"]["role_setting"]["협박자"]["becomes_mafioso"];
      document.querySelector(".납치범 input[name='can_jail_members']").checked=data["setup"]["options"]["role_setting"]["납치범"]["can_jail_members"];
      document.querySelector(".납치범 input[name='becomes_mafioso']").checked=data["setup"]["options"]["role_setting"]["납치범"]["becomes_mafioso"];
      document.querySelector(`.요원 input[name='nights_between_shadowings_Agent'][value="${data['setup']['options']['role_setting']['요원']['nights_between_shadowings']}"`).checked = true;
      document.querySelector(".요원 input[name='becomes_mafioso']").checked=data["setup"]["options"]["role_setting"]['요원']["becomes_mafioso"];
      document.querySelector(`.잠입자 input[name='hide_chance_Beguiler'][value="${data['setup']['options']['role_setting']['잠입자']['hide_chance']}"`).checked = true;
      document.querySelector(".잠입자 input[name='target_is_notified']").checked=data["setup"]["options"]["role_setting"]['잠입자']["target_is_notified"];
      document.querySelector(".잠입자 input[name='can_hide_behind_member']").checked=data["setup"]["options"]["role_setting"]['잠입자']["can_hide_behind_member"];
      document.querySelector(".잠입자 input[name='becomes_mafioso']").checked=data["setup"]["options"]["role_setting"]['잠입자']["becomes_mafioso"];
      document.querySelector(".백지선 input[name='promoted_if_no_Dragonhead']").checked=data["setup"]["options"]["role_setting"]["백지선"]["promoted_if_no_Dragonhead"];
      document.querySelector(".백지선 input[name='detect_exact_role']").checked=data["setup"]["options"]["role_setting"]["백지선"]["detect_exact_role"];
      document.querySelector(".백지선 input[name='becomes_enforcer']").checked=data["setup"]["options"]["role_setting"]["백지선"]["becomes_enforcer"];
      document.querySelector(`.용두 input[name='defense_level_Dragonhead'][value="${data['setup']['options']['role_setting']['용두']['defense_level']}"`).checked = true;
      document.querySelector(".용두 input[name='cannot_be_blocked']").checked=data["setup"]["options"]["role_setting"]['용두']["cannot_be_blocked"];
      document.querySelector(".용두 input[name='detection_immune']").checked=data["setup"]["options"]["role_setting"]['용두']["detection_immune"];
      document.querySelector(".용두 input[name='killable_without_enforcer']").checked=data["setup"]["options"]["role_setting"]['용두']["killable_without_enforcer"];
      document.querySelector(".간통범 input[name='cannot_be_blocked']").checked=data["setup"]["options"]["role_setting"]["간통범"]["cannot_be_blocked"];
      document.querySelector(".간통범 input[name='detects_block_immune_target']").checked=data["setup"]["options"]["role_setting"]["간통범"]["detects_block_immune_target"];
      document.querySelector(".간통범 input[name='becomes_enforcer']").checked=data["setup"]["options"]["role_setting"]["간통범"]["becomes_enforcer"];
      document.querySelector(".위조꾼 input[name='detection_immune']").checked=data["setup"]["options"]["role_setting"]["위조꾼"]["detection_immune"];
      document.querySelector(".위조꾼 input[name='becomes_enforcer']").checked=data["setup"]["options"]["role_setting"]["위조꾼"]["becomes_enforcer"];
      document.querySelector(`.향주 input[name='sanitize_chance'][value="${data['setup']['options']['role_setting']['향주']['sanitize_chance']}"`).checked = true;
      document.querySelector(".향주 input[name='becomes_enforcer']").checked=data["setup"]["options"]["role_setting"]['향주']["becomes_enforcer"];
      document.querySelector(".침묵자 input[name='can_talk_during_trial']").checked=data["setup"]["options"]["role_setting"]["침묵자"]["can_talk_during_trial"];
      document.querySelector(".침묵자 input[name='becomes_enforcer']").checked=data["setup"]["options"]["role_setting"]["침묵자"]["becomes_enforcer"];
      document.querySelector(".심문자 input[name='can_jail_members']").checked=data["setup"]["options"]["role_setting"]["심문자"]["can_jail_members"];
      document.querySelector(".심문자 input[name='becomes_enforcer']").checked=data["setup"]["options"]["role_setting"]["심문자"]["becomes_enforcer"];
      document.querySelector(`.선봉 input[name='nights_between_shadowings'][value="${data['setup']['options']['role_setting']['선봉']['nights_between_shadowings']}"`).checked = true;
      document.querySelector(".선봉 input[name='becomes_enforcer']").checked=data["setup"]["options"]["role_setting"]['선봉']["becomes_enforcer"];
      document.querySelector(`.사기꾼 input[name='hide_chance'][value="${data['setup']['options']['role_setting']['사기꾼']['hide_chance']}"`).checked = true;
      document.querySelector(".사기꾼 input[name='target_is_notified']").checked=data["setup"]["options"]["role_setting"]['사기꾼']["target_is_notified"];
      document.querySelector(".사기꾼 input[name='can_hide_behind_member']").checked=data["setup"]["options"]["role_setting"]['사기꾼']["can_hide_behind_member"];
      document.querySelector(".사기꾼 input[name='becomes_enforcer']").checked=data["setup"]["options"]["role_setting"]['사기꾼']["becomes_enforcer"];
      document.querySelector(`.생존자 input[name='bulletproof_chance'][value="${data['setup']['options']['role_setting']['생존자']['bulletproof_chance']}"`).checked = true;
      document.querySelector(".기억상실자 input[name='revealed']").checked=data["setup"]["options"]["role_setting"]["기억상실자"]["revealed"];
      document.querySelector(".기억상실자 input[name='cannot_remember_town']").checked=data["setup"]["options"]["role_setting"]["기억상실자"]["cannot_remember_town"];
      document.querySelector(".기억상실자 input[name='cannot_remember_mafia_and_triad']").checked=data["setup"]["options"]["role_setting"]["기억상실자"]["cannot_remember_mafia_and_triad"];
      document.querySelector(".기억상실자 input[name='cannot_remember_killing_role']").checked=data["setup"]["options"]["role_setting"]["기억상실자"]["cannot_remember_killing_role"];
      document.querySelector(".어릿광대 input[name='randomly_suicide']").checked=data["setup"]["options"]["role_setting"]["어릿광대"]["randomly_suicide"];
      document.querySelector(".처형자 input[name='becomes_Jester']").checked=data["setup"]["options"]["role_setting"]["처형자"]["becomes_Jester"];
      document.querySelector(".처형자 input[name='target_is_town']").checked=data["setup"]["options"]["role_setting"]["처형자"]["target_is_town"];
      document.querySelector(".처형자 input[name='win_if_survived']").checked=data["setup"]["options"]["role_setting"]["처형자"]["win_if_survived"];
      document.querySelector(`.처형자 input[name='defense_level_Executioner'][value="${data['setup']['options']['role_setting']['처형자']['defense_level']}"`).checked = true;
      document.querySelector(".마녀 input[name='can_control_self']").checked=data["setup"]["options"]["role_setting"]["마녀"]["can_control_self"];
      document.querySelector(".마녀 input[name='target_is_notified']").checked=data["setup"]["options"]["role_setting"]["마녀"]["target_is_notified"];
      document.querySelector(".마녀 input[name='WitchDoctor_when_converted']").checked=data["setup"]["options"]["role_setting"]["마녀"]["WitchDoctor_when_converted"];
      document.querySelector(".회계사 input[name='can_audit_mafia']").checked=data["setup"]["options"]["role_setting"]["회계사"]["can_audit_mafia"];
      document.querySelector(".회계사 input[name='can_audit_triad']").checked=data["setup"]["options"]["role_setting"]["회계사"]["can_audit_triad"];
      document.querySelector(".회계사 input[name='can_audit_night_immune']").checked=data["setup"]["options"]["role_setting"]["회계사"]["can_audit_night_immune"];
      document.querySelector(`.회계사 input[name='audit_chance'][value="${data['setup']['options']['role_setting']['회계사']['audit_chance']}"`).checked = true;
      document.querySelector(`.판사 input[name='court_chance'][value="${data['setup']['options']['role_setting']['판사']['court_chance']}"`).checked = true;
      document.querySelector(`.판사 input[name='nights_between_court'][value="${data['setup']['options']['role_setting']['판사']['nights_between_court']}"`).checked = true;
      document.querySelector(`.판사 input[name='extra_votes'][value="${data['setup']['options']['role_setting']['판사']['extra_votes']}"`).checked = true;
      document.querySelector(".이교도 input[name='can_convert_night_immune']").checked=data["setup"]["options"]["role_setting"]["이교도"]["can_convert_night_immune"];
      document.querySelector(`.이교도 input[name='nights_between_conversion'][value="${data['setup']['options']['role_setting']['이교도']['nights_between_conversion']}"`).checked = true;
      document.querySelector(`.요술사 input[name='save_chance'][value="${data['setup']['options']['role_setting']['요술사']['save_chance']}"`).checked = true;
      document.querySelector(`.요술사 input[name='night_between_save'][value="${data['setup']['options']['role_setting']['요술사']['night_between_save']}"`).checked = true;
      document.querySelector(".요술사 input[name='detection_immune']").checked=data["setup"]["options"]["role_setting"]['요술사']["detection_immune"];
      document.querySelector(`.연쇄살인마 input[name='defense_level_SerialKiller'][value="${data['setup']['options']['role_setting']['연쇄살인마']['defense_level']}"`).checked = true;
      document.querySelector(".연쇄살인마 input[name='kill_blocker']").checked=data["setup"]["options"]["role_setting"]['연쇄살인마']["kill_blocker"];
      document.querySelector(".연쇄살인마 input[name='win_if_1v1_with_Arsonist']").checked=data["setup"]["options"]["role_setting"]['연쇄살인마']["win_if_1v1_with_Arsonist"];
      document.querySelector(".연쇄살인마 input[name='detection_immune']").checked=data["setup"]["options"]["role_setting"]['연쇄살인마']["detection_immune"];
      document.querySelector(`.대량학살자 input[name='defense_level_MassMurderer'][value="${data['setup']['options']['role_setting']['대량학살자']['defense_level']}"`).checked = true;
      document.querySelector(".대량학살자 input[name='can_visit_self']").checked=data["setup"]["options"]["role_setting"]['대량학살자']["can_visit_self"];
      document.querySelector(`.대량학살자 input[name='nights_between_murder'][value="${data['setup']['options']['role_setting']['대량학살자']['nights_between_murder']}"`).checked = true;
      document.querySelector(".대량학살자 input[name='detection_immune']").checked=data["setup"]["options"]["role_setting"]['대량학살자']["detection_immune"];
      document.querySelector(`.방화범 input[name='offense_level'][value="${data['setup']['options']['role_setting']['방화범']['offense_level']}"`).checked = true;
      document.querySelector(`.방화범 input[name='defense_level'][value="${data['setup']['options']['role_setting']['방화범']['defense_level']}"`).checked = true;
      document.querySelector(".방화범 input[name='fire_spreads']").checked=data["setup"]["options"]["role_setting"]['방화범']["fire_spreads"];
      document.querySelector(".방화범 input[name='target_is_notified']").checked=data["setup"]["options"]["role_setting"]['방화범']["target_is_notified"];
      document.querySelector(".방화범 input[name='douse_blocker']").checked=data["setup"]["options"]["role_setting"]['방화범']["douse_blocker"];
      document.querySelector(".모든무작위직 input[name='excludes_killing_role']").checked=data["setup"]["options"]["role_setting"]["모든 무작위직"]["excludes_killing_role"];
      document.querySelector(".모든무작위직 input[name='excludes_mafia']").checked=data["setup"]["options"]["role_setting"]["모든 무작위직"]["excludes_mafia"];
      document.querySelector(".모든무작위직 input[name='excludes_triad']").checked=data["setup"]["options"]["role_setting"]["모든 무작위직"]["excludes_triad"];
      document.querySelector(".모든무작위직 input[name='excludes_neutral']").checked=data["setup"]["options"]["role_setting"]["모든 무작위직"]["excludes_neutral"];
      document.querySelector(".모든무작위직 input[name='excludes_town']").checked=data["setup"]["options"]["role_setting"]["모든 무작위직"]["excludes_town"];
      document.querySelector(".시민무작위직 input[name='excludes_killing_role']").checked=data["setup"]["options"]["role_setting"]["시민 무작위직"]["excludes_killing_role"];
      document.querySelector(".시민무작위직 input[name='excludes_government']").checked=data["setup"]["options"]["role_setting"]["시민 무작위직"]["excludes_government"];
      document.querySelector(".시민무작위직 input[name='excludes_investigative']").checked=data["setup"]["options"]["role_setting"]["시민 무작위직"]["excludes_investigative"];
      document.querySelector(".시민무작위직 input[name='excludes_protective']").checked=data["setup"]["options"]["role_setting"]["시민 무작위직"]["excludes_protective"];
      document.querySelector(".시민무작위직 input[name='excludes_power']").checked=data["setup"]["options"]["role_setting"]["시민 무작위직"]["excludes_power"];
      document.querySelector(".시민행정직 input[name='excludes_citizen']").checked=data["setup"]["options"]["role_setting"]["시민 행정직"]["excludes_citizen"];
      document.querySelector(".시민행정직 input[name='excludes_mason']").checked=data["setup"]["options"]["role_setting"]["시민 행정직"]["excludes_mason"];
      document.querySelector(".시민행정직 input[name='excludes_mayor_and_marshall']").checked=data["setup"]["options"]["role_setting"]["시민 행정직"]["excludes_mayor_and_marshall"];
      document.querySelector(".시민행정직 input[name='excludes_masonleader']").checked=data["setup"]["options"]["role_setting"]["시민 행정직"]["excludes_masonleader"];
      document.querySelector(".시민행정직 input[name='excludes_crier']").checked=data["setup"]["options"]["role_setting"]["시민 행정직"]["excludes_crier"];
      document.querySelector(".시민조사직 input[name='excludes_coroner']").checked=data["setup"]["options"]["role_setting"]["시민 조사직"]["excludes_coroner"];
      document.querySelector(".시민조사직 input[name='excludes_sheriff']").checked=data["setup"]["options"]["role_setting"]["시민 조사직"]["excludes_sheriff"];
      document.querySelector(".시민조사직 input[name='excludes_investigator']").checked=data["setup"]["options"]["role_setting"]["시민 조사직"]["excludes_investigator"];
      document.querySelector(".시민조사직 input[name='excludes_detective']").checked=data["setup"]["options"]["role_setting"]["시민 조사직"]["excludes_detective"];
      document.querySelector(".시민조사직 input[name='excludes_lookout']").checked=data["setup"]["options"]["role_setting"]["시민 조사직"]["excludes_lookout"];
      document.querySelector(".시민방어직 input[name='excludes_bodyguard']").checked=data["setup"]["options"]["role_setting"]["시민 방어직"]["excludes_bodyguard"];
      document.querySelector(".시민방어직 input[name='excludes_doctor']").checked=data["setup"]["options"]["role_setting"]["시민 방어직"]["excludes_doctor"];
      document.querySelector(".시민방어직 input[name='excludes_escort']").checked=data["setup"]["options"]["role_setting"]["시민 방어직"]["excludes_escort"];
      document.querySelector(".시민살인직 input[name='excludes_veteran']").checked=data["setup"]["options"]["role_setting"]["시민 살인직"]["excludes_veteran"];
      document.querySelector(".시민살인직 input[name='excludes_jailor']").checked=data["setup"]["options"]["role_setting"]["시민 살인직"]["excludes_jailor"];
      document.querySelector(".시민살인직 input[name='excludes_bodyguard']").checked=data["setup"]["options"]["role_setting"]["시민 살인직"]["excludes_bodyguard"];
      document.querySelector(".시민살인직 input[name='excludes_vigilante']").checked=data["setup"]["options"]["role_setting"]["시민 살인직"]["excludes_vigilante"];
      document.querySelector(".시민능력직 input[name='excludes_veteran']").checked=data["setup"]["options"]["role_setting"]["시민 능력직"]["excludes_veteran"];
      document.querySelector(".시민능력직 input[name='excludes_spy']").checked=data["setup"]["options"]["role_setting"]["시민 능력직"]["excludes_spy"];
      document.querySelector(".시민능력직 input[name='excludes_jailor']").checked=data["setup"]["options"]["role_setting"]["시민 능력직"]["excludes_jailor"];
      document.querySelector(".마피아무작위직 input[name='excludes_killing_role']").checked=data["setup"]["options"]["role_setting"]["마피아 무작위직"]["excludes_killing_role"];
      document.querySelector(".마피아살인직 input[name='excludes_kidnapper']").checked=data["setup"]["options"]["role_setting"]["마피아 살인직"]["excludes_kidnapper"];
      document.querySelector(".마피아살인직 input[name='excludes_mafioso']").checked=data["setup"]["options"]["role_setting"]["마피아 살인직"]["excludes_mafioso"];
      document.querySelector(".마피아살인직 input[name='excludes_godfather']").checked=data["setup"]["options"]["role_setting"]["마피아 살인직"]["excludes_godfather"];
      document.querySelector(".마피아지원직 input[name='excludes_blackmailer']").checked=data["setup"]["options"]["role_setting"]["마피아 지원직"]["excludes_blackmailer"];
      document.querySelector(".마피아지원직 input[name='excludes_kidnapper']").checked=data["setup"]["options"]["role_setting"]["마피아 지원직"]["excludes_kidnapper"];
      document.querySelector(".마피아지원직 input[name='excludes_consort']").checked=data["setup"]["options"]["role_setting"]["마피아 지원직"]["excludes_consort"];
      document.querySelector(".마피아지원직 input[name='excludes_consigliere']").checked=data["setup"]["options"]["role_setting"]["마피아 지원직"]["excludes_consigliere"];
      document.querySelector(".마피아지원직 input[name='excludes_agent']").checked=data["setup"]["options"]["role_setting"]["마피아 지원직"]["excludes_agent"];
      document.querySelector(".마피아속임수직 input[name='excludes_framer']").checked=data["setup"]["options"]["role_setting"]["마피아 속임수직"]["excludes_framer"];
      document.querySelector(".마피아속임수직 input[name='excludes_janitor']").checked=data["setup"]["options"]["role_setting"]["마피아 속임수직"]["excludes_janitor"];
      document.querySelector(".마피아속임수직 input[name='excludes_beguiler']").checked=data["setup"]["options"]["role_setting"]["마피아 속임수직"]["excludes_beguiler"];
      document.querySelector(".삼합회무작위직 input[name='excludes_killing_role']").checked=data["setup"]["options"]["role_setting"]["삼합회 무작위직"]["excludes_killing_role"];
      document.querySelector(".삼합회살인직 input[name='excludes_interrogator']").checked=data["setup"]["options"]["role_setting"]["삼합회 살인직"]["excludes_interrogator"];
      document.querySelector(".삼합회살인직 input[name='excludes_enforcer']").checked=data["setup"]["options"]["role_setting"]["삼합회 살인직"]["excludes_enforcer"];
      document.querySelector(".삼합회살인직 input[name='excludes_dragonhead']").checked=data["setup"]["options"]["role_setting"]["삼합회 살인직"]["excludes_dragonhead"];
      document.querySelector(".삼합회지원직 input[name='excludes_silencer']").checked=data["setup"]["options"]["role_setting"]["삼합회 지원직"]["excludes_silencer"];
      document.querySelector(".삼합회지원직 input[name='excludes_interrogator']").checked=data["setup"]["options"]["role_setting"]["삼합회 지원직"]["excludes_interrogator"];
      document.querySelector(".삼합회지원직 input[name='excludes_liaison']").checked=data["setup"]["options"]["role_setting"]["삼합회 지원직"]["excludes_liaison"];
      document.querySelector(".삼합회지원직 input[name='excludes_administrator']").checked=data["setup"]["options"]["role_setting"]["삼합회 지원직"]["excludes_administrator"];
      document.querySelector(".삼합회지원직 input[name='excludes_vanguard']").checked=data["setup"]["options"]["role_setting"]["삼합회 지원직"]["excludes_vanguard"];
      document.querySelector(".삼합회속임수직 input[name='excludes_forger']").checked=data["setup"]["options"]["role_setting"]["삼합회 속임수직"]["excludes_forger"];
      document.querySelector(".삼합회속임수직 input[name='excludes_incensemaster']").checked=data["setup"]["options"]["role_setting"]["삼합회 속임수직"]["excludes_incensemaster"];
      document.querySelector(".삼합회속임수직 input[name='excludes_deceiver']").checked=data["setup"]["options"]["role_setting"]["삼합회 속임수직"]["excludes_deceiver"];
      document.querySelector(".중립무작위직 input[name='excludes_killing_role']").checked=data["setup"]["options"]["role_setting"]["중립 무작위직"]["excludes_killing_role"];
      document.querySelector(".중립무작위직 input[name='excludes_evil']").checked=data["setup"]["options"]["role_setting"]["중립 무작위직"]["excludes_evil"];
      document.querySelector(".중립무작위직 input[name='excludes_benign']").checked=data["setup"]["options"]["role_setting"]["중립 무작위직"]["excludes_benign"];
      document.querySelector(".중립살인직 input[name='excludes_serialkiller']").checked=data["setup"]["options"]["role_setting"]["중립 살인직"]["excludes_serialkiller"];
      document.querySelector(".중립살인직 input[name='excludes_arsonist']").checked=data["setup"]["options"]["role_setting"]["중립 살인직"]["excludes_arsonist"];
      document.querySelector(".중립살인직 input[name='excludes_massmurderer']").checked=data["setup"]["options"]["role_setting"]["중립 살인직"]["excludes_massmurderer"];
      document.querySelector(".중립악 input[name='excludes_killing_role']").checked=data["setup"]["options"]["role_setting"]["중립 악"]["excludes_killing_role"];
      document.querySelector(".중립악 input[name='excludes_cults']").checked=data["setup"]["options"]["role_setting"]["중립 악"]["excludes_cults"];
      document.querySelector(".중립악 input[name='excludes_witch']").checked=data["setup"]["options"]["role_setting"]["중립 악"]["excludes_witch"];
      document.querySelector(".중립악 input[name='excludes_judge']").checked=data["setup"]["options"]["role_setting"]["중립 악"]["excludes_judge"];
      document.querySelector(".중립악 input[name='excludes_auditor']").checked=data["setup"]["options"]["role_setting"]["중립 악"]["excludes_auditor"];
      document.querySelector(".중립선 input[name='excludes_survivor']").checked=data["setup"]["options"]["role_setting"]["중립 선"]["excludes_survivor"];
      document.querySelector(".중립선 input[name='excludes_jester']").checked=data["setup"]["options"]["role_setting"]["중립 선"]["excludes_jester"];
      document.querySelector(".중립선 input[name='excludes_executioner']").checked=data["setup"]["options"]["role_setting"]["중립 선"]["excludes_executioner"];
      document.querySelector(".중립선 input[name='excludes_amnesiac']").checked=data["setup"]["options"]["role_setting"]["중립 선"]["excludes_amnesiac"];
      break;
    case "applying_setup_success":
      addchat("설정이 적용되었습니다. '/시행'을 입력하여 설정을 시험해볼 수 있습니다.");
      addchat("설정이 바뀌어 준비가 해제되었습니다.");
      addchat("'/저장'을 입력하여 현재 설정을 계정에 저장할 수 있습니다.");
      addchat("'/불러오기'를 입력하여 설정을 계정에 불러올 수 있습니다.");
      break;
    case "applying_setup_failed":
      addchat("설정에 문제가 있어 적용에 실패했습니다.", "red");
      break;
    case "warning":
      addchat("설정에 문제가 있습니다.", "red");
      break;
    case 'message':
      if (data["hell"]) {
        addchat(data["who"]+": "+data["message"], "white", "rgba(100, 30, 22, 0.4)")
      } else {
        addchat(data['who']+': '+data['message'], 'white');
      }
      break;
    case "whispering":
      addchat(data["to"]+"님께 귓속말: " + data["message"], "green");
      break;
    case "whispered":
      addchat(data["from"]+"님에게서 귓속말: " + data["message"], "green");
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
    case "kick":
      addchat(data["kicker"]+"님이 "+data["kicked"]+"님을 강퇴했습니다.");
      break;
    case "kicked":
      alert("방장이 당신을 강퇴했습니다.");
      break;
    case "unable_to_kick":
      addchat(data["reason"]);
      break;
    case "unable_to_start":
      switch (data["reason"]) {
        case "not_readied":
          addchat(data["not_readied"]+"님 등이 준비하지 않아 시작할 수 없습니다.");
          break;
        case "not_enough_members":
          addchat("인원이 설정과 맞지 않습니다. "+data["required_members"]+"명이어야만 시작할 수 있습니다.");
          break;
        case "invalid_setup":
          addchat("설정에 문제가 있어 시작할 수 없습니다.");
          break;
        case "no setup":
          addchat("설정이 없어 시작할 수 없습니다. '/불러오기'를 입력하면 계정에 저장된 설정을 불러올 수 있습니다.");
          break;
        default:
          addchat("게임 시작 불가: "+data["reason"])
        }
      break;
    case 'game_over':
      let result = "";
      for (const [index, info] of data["winner"].entries()) {
        let winner = info[0];
        let role = info[1];
        result += winner+"("+colored(role)+")";
        if (index<data["winner"].length-1) {
          result += ", ";
        }
      }
      addchat('게임이 끝났습니다. 승자들은 '+result+' 등입니다.');
      break;
    case "save_done":
      addchat("게임이 저장되었습니다. 게임 기록을 <a target='_blank' href='archive/"+data["link"]+"'>http://localhost:8080/archive/"+data["link"]+"</a>에서 열람하실 수 있습니다.");
      break;
    case "save_slot_success":
      addchat("게임 설정을 저장했습니다. '/불러오기'를 입력해 해당 설정을 불러올 수 있습니다.");
      break;
    case "load_slot_success":
      addchat("게임 설정을 불러왔습니다.");
      break;
    case "music":
      swap_audio(data["music"]);
      break;
    case "Error":
      addchat(`게임에 오류가 발생했습니다. 오류 메시지: ${data["error_code"]}`, "red")
      break;
    case 'role':
      document.querySelector("#messages").innerHTML = "";
      addchat('당신의 직업은 '+colored(data["role"])+'입니다.');
      switch (data["role"]) {
        case "시장":
          addchat("당신은 마을의 시장입니다.");
          addchat(`당신은 낮에 '/발동'을 입력하여 투표권을 ${data["options"]["extra_votes"]}표로 반영구히 늘릴 수 있습니다.`)
          break;
        case "원수":
          addchat("당신은 마을 민병대의 지도자입니다.");
          addchat("당신은 낮에 '/개시'를 입력하여 집단 사형을 개시할 수 있습니다.");
          addchat(`능력은 단 ${data["options"]["lynch_chance"]}번 사용할 수 있습니다.`);
          break;
        case "시민":
          addchat("당신은 진실과 정의를 믿는 일반적인 시민입니다.");
          addchat("당신은 특별한 능력은 따로 없습니다.");
          if (data["options"]["bulletproof"]) {
            addchat("단 한 번, 방탄조끼를 착용('/착용')하여 밤에 공격에서 보호받을 수 있습니다.");
          }
          break;
        case "비밀조합장":
          addchat("당신은 비밀조합의 지도자입니다.");
          addchat("당신은 밤마다 '/방문 닉네임'을 입력하여 그 사람을 "+colored("비밀조합원")+"으로 영입하려 시도할 수 있습니다.");
          addchat("직업이 "+colored("시민")+"이면 영입 대상은 "+colored("비밀조합원")+"으로 영입됩니다.");
          addchat("직업이 "+colored("이교도")+"세력이면 영입 대상은 당신에게 죽습니다.");
          addchat("직업이 "+colored("마피아")+"나 "+colored("삼합회")+"세력이면 당신의 정체가 그들에게 드러납니다.");
          break;
        case "비밀조합원":
          addchat("당신은 비밀조합의 일원입니다.");
          addchat("매일 밤 비밀조합 소속끼리 대화할 수 있습니다. 당신은 "+colored("이교도")+"에게 개종당하지 않습니다.")
          break;
        case "포고꾼":
          addchat("당신은 목청이 큰 소식전파자로 마을을 돕기 위해 노력합니다.");
          addchat("당신은 밤마다 마을 전체에 익명으로 말을 할 수 있습니다.");
          addchat(colored("판사")+"가 부정한 재판을 열었을 때 판사와 함께 '재판관'이라고 뜨면서 발언이 강조됩니다.");
          break;
        case "보안관":
          addchat("당신은 죽음의 위협을 피해 숨어서 행동을 하는 이 마을의 보안관입니다.");
          addchat("매일 밤 '/방문 닉네임'을 입력하여 그 사람이 수상한지 확인할 수 있습니다.");
          break;
        case "탐정":
          addchat("당신은 이 마을의 비밀 탐정으로서, 음지에서 시민들을 도와줍니다.");
          addchat(`매일 밤 '/방문 닉네임'을 입력하여 그 사람${data["options"]["detect_exact_role"] ? "의 직업을":"이 저지른 범죄를"} 알아낼 수 있습니다.`);
          break;
        case "검시관":
          addchat("당신은 부검에 박식한 검시관입니다.");
          addchat("매일 밤 '/방문 닉네임'을 입력하여 그 사람의 사망 정보를 알 수 있습니다.");
          break;
        case "형사":
          addchat("당신은 숙련된 추적자입니다.");
          addchat("매일 밤 '/방문 닉네임'을 입력하여 그 사람이 누구를 방문하는지 알아낼 수 있습니다.");
          if (data["options"]["ignore_detection_immune"]) {
            addchat("당신은 검출 면역인 사람도 발견할 수 있습니다.");
          }
          break;
        case "감시자":
          addchat("당신은 은밀하게 정보를 얻기 위해 목표대상 집 밖에서 잠복하는 관찰자입니다.");
          addchat("매일 밤 '/방문 닉네임'을 입력하여 그 사람에게 누가 방문하는지 알아낼 수 있습니다.");
          if (data["options"]["ignore_detection_immune"]) {
            addchat("당신은 검출 면역인 사람도 발견할 수 있습니다.");
          }
          break;
        case "의사":
          addchat("당신은 응급처치에 능통한 외과의사입니다.");
          addchat("매일 밤 '/방문 닉네임'을 입력하여 그 사람이 공격받았을 경우 살려낼 수 있습니다.");
          break;
        case "기생":
          addchat("당신은 얇게 입은 옷으로 남들을 비밀스럽게 유혹하는 기생입니다.");
          addchat("매일 밤 '/방문 닉네임'을 입력하여 그 사람이 능력을 사용하는 것을 막을 수 있습니다.");
          break;
        case "버스기사":
          addchat("당신은 야매로 면허를 취득한 버스기사입니다.");
          addchat("매일 밤 '/방문 닉네임 닉네임'을 입력하여 두 사람의 위치를 바꿀 수 있습니다.");
          addchat("한쪽이 누군가의 능력 대상이 될 경우, 다른 쪽이 대신 능력 대상이 됩니다.");
          break;
        case "경호원":
          addchat("당신은 비밀리에 한 사람을 지키는 일로 생계를 유지하는 경호원입니다.");
          addchat("매일 밤 '/방문 닉네임'을 입력하여 그 사람을 보호할 수 있습니다. 목표가 공격당하면 당신은 공격자와 싸워서 같이 죽습니다.");
          break;
        case "자경대원":
          addchat("당신은 정의를 바로잡기 위하여 법을 무시하는 자경대원입니다.");
          addchat("매일 밤 '/방문 닉네임'을 입력하여 그 사람을 죽일 수 있습니다.");
          addchat(`당신은 총을 단 ${data["options"]["kill_chance"]}번 쏠 수 있습니다.`);
          if (data["options"]["suicides_if_shot_town"]) {
            addchat("쏜 대상이 시민이면 남은 총알을 모두 잃습니다.");
          }
          break;
        case "간수":
          addchat("당신은 비밀리에 용의자를 감옥에 구금하는 간수입니다.");
          addchat("낮에 '/감금 닉네임'을 입력하여 그날밤 그 사람을 당신의 감옥에 가둘 수 있습니다. 사형에 있은 날에는 가둘 수 없습니다.");
          break;
        case "퇴역군인":
          addchat("당신은 편집증으로 퇴역한 사람으로, 자기를 괴롭히면 그 사람이 누구든지 죽입니다.");
          addchat("밤에 '/경계'를 입력하여 그날 밤 경계를 설 수 있습니다. 경계한 날 밤 누군가 당신을 방문하면 당신은 그 사람을 죽입니다.");
          addchat(`당신은 총 ${data["options"]["alert_chance"]}회 경계할 수 있습니다.`);
          break;
        case "정보원":
          addchat("당신은 비밀스러운 대화를 몰래 도청할 수 있는 정보원입니다.");
          addchat("당신은 "+colored("마피아")+"와 "+colored("삼합회")+"의 대화를 들을 수 있고, 이들이 누구를 방문하는지 알 수 있습니다.");
          break;
        case "나무 그루터기":
          addchat("당신은 의욕이 없는 게으름뱅이입니다.");
          break;
        case "마피아 일원":
        case "홍곤":
          addchat("당신은 범죄 조직의 일원입니다.");
          addchat("매일 밤 '/방문 닉네임'을 입력하여 그 사람을 죽일 수 있습니다.");
          break;
        case "대부":
        case "용두":
          addchat("당신은 범죄 조직의 지도자입니다.");
          addchat("매일 밤 '/방문 닉네임'을 입력하여 그 사람을 죽일 수 있습니다.");
          addchat("매일 밤 '/영입 닉네임'을 입력하여 그 사람을 조직으로 영입 시도할 수 있습니다.");
          break;
        case "변장자":
        case "밀고자":
          addchat("당신은 조직을 위해 일하는 스파이, 위조에 능통한 "+colored(data["role"])+"입니다.");
          addchat("당신은 딱 한 번, 밤에 '/방문 닉네임'을 입력하여 사람을 죽이고 그 신분을 훔쳐 자기 것으로 만들 수 있습니다.");
          break;
        case "납치범":
        case "심문자":
          addchat("당신은 비밀리에 관심 있는 사람들을 억류하는 부패한 교도소장입니다.");
          addchat("낮에 '/감금 닉네임'을 입력하여 그날밤 그 사람을 당신의 감옥에 가둘 수 있습니다. 사형이 있은 날에는 가둘 수 없습니다.");
          break;
        case "매춘부":
        case "간통범":
          addchat("당신은 조직을 위해 일하는 춤꾼입니다.");
          addchat("매일 밤 '/방문 닉네임'을 입력하여 그 사람이 능력을 사용하는 것을 막을 수 있습니다.");
          break;
        case "조언자":
        case "백지선":
          addchat("당신은 조직 우두머리의 부관입니다.");
          addchat(`매일 밤 '/방문 닉네임'을 입력하여 그 사람${data["options"]["detect_exact_role"] ? "의 직업을":"이 저지른 범죄를"} 알아낼 수 있습니다.`);
          break;
        case "협박자":
        case "침묵자":
          addchat("당신은 사람의 입을 닫기 위해서 도청하고 정보를 사용하여 조종합니다.");
          addchat("매일 밤 '/방문 닉네임'을 입력하여 사람을 협박할 수 있습니다. 그 사람은 다음날 말을 할 수 없게 됩니다.");
          break;
        case "요원":
        case "선봉":
          addchat("당신은 부패한 정보요원으로 집을 도청하거나 정보를 수집하고 대상을 스토킹합니다.");
          addchat("매일 밤 '/방문 닉네임'을 입력하여 그 사람이 방문한 사람과 그 사람에게 방문하는 사람을 알 수 있습니다.");
          if (data["options"]["nights_between_shadowings"]>0) {
            addchat(`한번 누군가를 방문하면 ${data["options"]["nights_between_shadowings"]}일 동안 능력을 사용할 수 없습니다.`);
          }
          break;
        case "조작자":
        case "위조꾼":
          addchat("당신은 조직을 위해 일하는 숙련된 "+colored(data["role"])+"입니다.");
          addchat("매일 밤 '/방문 닉네임'을 입력하여 그 사람의 직업을 무작위 마피아/삼합회 또는 중립 악 직업으로 나오게 하고, 무작위 범죄를 하나 영구히 추가합니다.");
          if (data["options"]["detection_immune"]) {
            addchat("당신은 검출에 면역입니다.");
          }
          break;
        case "관리인":
        case "향주":
          addchat("당신은 조직을 위해 일하는 부검 전문가입니다.");
          addchat("매일 밤 '/방문 닉네임'을 입력하여 누군가를 방문할 수 있습니다. 그 사람이 그날밤 죽으면 그 사람의 직업과 유언을 다음날 드러나지 않게 숨깁니다.");
          addchat(`능력은 총 ${data["options"]["sanitize_chance"]}번 사용할 수 있습니다.`);
          break;
        case "잠입자":
        case "사기꾼":
          addchat("당신은 살아남기 위해 숨어서 조작하는 "+colored(data["role"])+"입니다.");
          addchat("매일 밤 '/방문 닉네임'을 입력하여 그날밤 당신을 방문하는 사람을 모두 그 사람에게 보낼 수 있습니다.");
          addchat(`능력은 총 ${data["options"]["hide_chance"]}번 사용할 수 있습니다.`);
          break;
        case "생존자":
          addchat("무관심하고 개인적인 당신은 단지 살아남기를 원합니다.");
          addchat("매일 밤 '/착용'을 입력하여 방탄조끼를 착용할 수 있습니다.");
          addchat(`당신은 방탄조끼를 총 ${data["options"]["bulletproof_chance"]}벌 보유합니다.`);
          addchat("승리 조건: 끝까지 살아남으세요.");
          break;
        case "기억상실자":
          addchat("당신은 머리에 큰 상처를 입고 최근에 깨어났지만, 자신이 누구인지 전혀 기억이 나지 않는 사람입니다.");
          addchat("당신은 단 한 번, 밤에 '/기억 닉네임'을 입력하여 그 사람의 직업으로 변할 수 있습니다.");
          if (data["options"]["cannot_remember_town"]) {
            addchat(`당신은 ${colored("시민")} 직업을 기억할 수 없습니다.`);
          }
          if (data["options"]["cannot_remember_mafia_and_triad"]) {
            addchat(`당신은 ${colored("마피아")}와 ${colored("삼합회")} 직업을 기억할 수 없습니다.`);
          }
          if (data["options"]["cannot_remember_killing_role"]) {
            addchat("당신은 살인 직업을 기억할 수 없습니다.");
          }
          addchat("승리 조건: 변한 직업의 승리 조건과 같습니다. 만약 기억상실자인 상태로 남는다면 끝까지 살아남는 게 승리 조건이 됩니다.");
          break;
        case "어릿광대":
          addchat("어릿광대의 삶의 목표는 재판으로 공개처형을 당하는 것입니다.");
          addchat("승리 조건: 낮에 사형당하세요.");
          break;
        case "처형자":
          addchat("집착적인 당신의 목표는 목표 대상이 사형당하는 것을 보는 것입니다.");
          if (data["options"]["target_is_town"]) {
            addchat(`당신의 목표는 ${colored("시민")} 세력입니다.`);
          }
          addchat("승리 조건: 목표가 낮에 사형당하는 것을 살아서 목도하세요.");
          break;
        case "마녀":
          addchat("당신은 악하고 신비로운 능력을 보유한 마녀로, 다른 이를 조종하여 그의 능력을 악하게 사용합니다.");
          addchat("매일 밤 '/방문 닉네임 닉네임'을 입력하여 첫 번째 대상이 두 번째 대상에게 능력을 사용하도록 할 수 있습니다.");
          addchat("다섯 번째 밤이 되면 단 한 번 사용할 수 있는 저주 능력을 얻습니다. '/저주 닉네임'을 입력하면 대상은 그날밤 무조건 죽습니다.");
          addchat("승리 조건: 끝까지 살아남아 "+colored("시민")+"세력의 패배를 목격하세요.");
          break;
        case "회계사":
          addchat("당신은 악을 위해 능력과 지식을 사용하는 부패한"+colored("회계사")+"입니다.");
          addchat("매일 밤 '/방문 닉네임'을 입력하여 그 사람을 소속 세력의 최하위권으로 만들 수 있습니다.");
          addchat(`당신은 총 ${data["options"]["audit_chance"]}번 회계할 수 있습니다.`);
          addchat("승리 조건: 끝까지 살아남아 "+colored("시민")+"세력의 패배를 목격하세요.");
          break;
        case "판사":
          addchat("당신은 재판을 조종하기 위해 능력을 사용하는 부패한 판사입니다.");
          addchat(`낮에 '/개정'을 입력하여 부패한 재판을 열 수 있습니다. 재판 동안 당신은 ${data["options"]["extra_votes"]}표를 얻습니다.`);
          addchat(`당신은 재판을 총 ${data["options"]["court_chance"]}번 열 수 있습니다.`);
          if (data["options"]["nights_between_court"]>0) {
            addchat(`재판을 한번 열었다면 ${data["options"]["nights_between_court"]}일이 지나야 재판을 다시 열 수 있습니다.`);
          }
          addchat("승리 조건: 끝까지 살아남아 "+colored("시민")+"세력의 패배를 목격하세요.");
          break;
        case "인간쓰레기":
          addchat("당신은 세상을 싫어하는 패배자입니다.");
          addchat("승리 조건: 끝까지 살아남아 "+colored("시민")+"세력의 패배를 목격하세요.");
          break;
        case "이교도":
          addchat("당신이 속한 이교도 교단은 비밀리에 마을 전체를 자기네 종교로 개종시키는 것이 목표입니다.");
          addchat("매일 밤 '/방문 닉네임'을 입력하여 그 사람을 이교도로 개종시킬 수 있습니다.");
          addchat(colored("마피아")+"/"+colored("삼합회")+"/"+colored("비밀조합")+" 세력을 개종 시도하면 이들에게 당신의 정체가 드러납니다.");
          addchat("승리 조건: 모든 생존한 시민을 "+colored("이교도")+"로 만들고, 모든 범죄 조직을 죽이세요.");
          break;
        case "요술사":
          addchat("당신이 속한 이교도 교단은 비밀리에 마을 전체를 자기네 종교로 개종시키는 것이 목표입니다.");
          addchat("매일 밤 '/방문 닉네임'을 입력하여 그 사람을 살릴 수 있습니다. 대상이 공격받았고 개종가능한 직업이라면 이교도로 개종됩니다.");
          addchat(`당신은 총 ${data["options"]["save_chance"]}번 구원할 수 있습니다.`);
          if (data["options"]["night_between_save"]>0) {
            addchat(`한번 사람을 살리면 ${data["options"]["night_between_save"]}일을 기다려야 또 구원할 수 있습니다.`);
          }
          addchat(colored("마피아")+"/"+colored("삼합회")+"/"+colored("비밀조합")+" 세력을 살리면 이들에게 당신의 정체가 드러납니다.");
          addchat("승리 조건: 모든 생존한 시민을 "+colored("이교도")+"로 만들고, 모든 범죄 조직을 죽이세요.");
          break;
        case "연쇄살인마":
          addchat("당신은 세상을 증오하다 미쳐버린 범죄자입니다.");
          addchat("매일 밤 '/방문 닉네임'을 입력하여 그 사람을 죽일 수 있습니다.");
          addchat("승리 조건: 마지막으로 살아남은 사람이 되십시오.");
          break;
        case "대량학살자":
          addchat("당신은 내장을 조각내는 것을 예술 행위라고 생각하는 미친 살인자입니다.");
          addchat("매일 밤 '/방문 닉네임'을 입력하여 그 사람의 집에 있는 사람들을 전부 죽일 수 있습니다.");
          if (data["options"]["nights_between_murder"]) {
            addchat(`한번에 2명 이상을 죽일 경우 ${data["options"]["nights_between_murder"]}일 동안은 사람을 죽일 수 없습니다.`);
          }
          addchat("승리 조건: 마지막으로 살아남은 사람이 되십시오.");
          break;
        case "방화범":
          addchat("당신은 세상의 모든 것을 태우고 싶어합니다.");
          addchat("매일 밤 '/방문 닉네임'을 입력하여 그 사람에게 기름을 묻힐 수 있습니다. '/방화'를 입력하면 지금까지 기름이 묻은 모든 사람에게 불을 붙입니다.");
          addchat("승리 조건: 마지막으로 살아남은 사람이 되십시오.");
          break;
        default:
          addchat("이 직업의 설명이 등록되지 않았습니다. 운영자에게 문의하세요.");
      }
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
        case "EXECUTION":
          addchat("마을은 "+data["who"]+"님을 사형시키기로 결정했습니다.");
          break;
        case "LAST_WORD":
          addchat(data["who"]+"님, 마지막으로 할 말을 남기세요.");
          break;
        case 'EVENING':
          addchat('저녁이 되었습니다.');
          if (now_playing) {
            now_playing.pause();
          }
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
    case "vote_done":
      addchat("사형투표가 종료되었습니다.");
      addchat("결과는 유죄 "+data["guilty"]+"표에 무죄 "+data["innocent"]+"표.");
      break;
    case "mayor_ability_activation":
      addchat(data["who"]+"님은 <span style='color:#00bf00'>시장</span>입니다!!!", "skyblue");
      break;
    case "marshall_ability_activation":
      addchat(data["who"]+"님은 <span style='color:#00bf00'>원수</span>입니다!!!", "skyblue");
      break;
    case "court":
      addchat("판사가 부패한 재판을 개정했습니다!", "#BB6655");
      break;
    case 'visit':
      switch (data["role"]) {
        case "대부":
          addchat(data["visitor"] +"님이 죽일 대상: "+data["target1"]);
          break;
        case "마피아 일원":
          addchat(data["visitor"]+"님이 죽일 대상(대부의 지시가 우선합니다): "+data["target1"]);
          break;
        case "용두":
          addchat(data["visitor"]+"님이 죽일 대상: " + data["target1"]);
          break;
        case "홍곤":
          addchat(data["visitor"]+"님이 죽일 대상(용두의 지시가 우선합니다): " + data["target1"]);
          break;
        default:
        addchat(data["visitor"]+"님이 오늘 밤 방문할 대상: "+data["target1"]);
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
          addchat('당신은 감옥에서 처형을 집행하는 라이플 소리를 들었습니다...', 'red');
          break;
        case '퇴역군인':
          addchat('당신은 이 조용한 마을에서 누군가 싸우는 소리를 들을 수 있었습니다...', 'red');
          break;convertor
        case '경호원':
          addchat('당신은 격렬한 총격전의 소리를 들었습니다...', 'red');
          break;
        case '자경대원':
          addchat('당신은 마을을 완전히 뒤흔드는 총성을 들었습니다...', 'red');
          break;
        case '비밀조합장':
          addchat('당신은 두개골이 부서지는 역겨운 소리를 들었습니다...', 'red');
          break;
        case '버스기사':
          addchat('당신은 누군가가 차에 치이는 소리를 들었습니다...', 'red');
          break;
        case '마피아 일원':
          addchat('당신은 거리에 총성이 울리는 것을 들었습니다...', 'red');
          break;
        case '연쇄살인마':
          addchat('당신은 살인사건의 비명소리를 들었습니다...', 'red');
          break;
        case '대량학살자':
          if (data["number_of_murdered"] > 1) {
            addchat("당신은 체인톱이 살을 갈아버리는 끔찍한 불협화음을 들었습니다...", "red")
          } else {
            addchat('당신은 소름 끼치는 비명이 뒤섞인 소리를 들었습니다...', 'red');
          }
          break;
        case '방화범':
          addchat('당신은 불이 타오르는 소리와 함께 운명을 저주하는 비명소리를 들을 수 있었습니다...', 'red');
          break;
        case '잠입자':
          addchat('당신은 둔탁한 소리에 의한 짧은 몸부림과 힘든 기침을 들었습니다...', 'red');
          break;
        case '변장자':
          addchat("당신은 둔탁한 '쿵' 소리와 함께 미세한 총소리를 간신히 들을 수 있었습니다...", 'red');
          break;
        case '자살':
          addchat('당신은 밤에 한 발의 총성을 들었습니다...', 'red');
          break;
        case '마녀':
          addchat('소름끼치는 웃음소리가 들립니다...', 'red');
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
    case "unable_to_audit":
      addchat("대상을 회계할 수 없습니다.");
      break;
    case "audit_success":
      addchat("대상의 탈세를 밝혀냈습니다. "+data["who"]+"님은 이제 "+colored(data["role"])+"입니다.");
      break;
    case "unable_to":

      break;
    case "will_burn_today":
      addchat("오늘밤 불을 피우기로 합니다.");
      break;
    case "will_jail":
      addchat("감금할 대상: "+data["whom"]);
      break;
    case "jailed":
      addchat("당신은 감옥에 갇혔습니다!");
      break;
    case "will_execute_the_jailed":
      addchat("간수가 처형할 대상: "+data["executed"])
      break;
    case "has_jailed_someone":
      addchat("당신은 그 사람을 감옥에 가두었습니다. '/처형' 명령어를 입력하면 수감자를 죽일 수 있습니다. 명령어를 다시 입력하면 취소됩니다.")
      break;
    case "recruited_by_cult":
      addchat(`이교도 ${data["who"]}님이 당신을 개종하려 시도했습니다.`);
      break;
    case "tried_to_recruit_Mason":
      addchat(`당신이 개종을 시도한 ${data["who"]}님은 ${colored("비밀조합원")}이었습니다!!! 당신은 ${data["who"]}님께 정체를 들키고 말았습니다.`);
      break;
    case "will_recruit":
      addchat("대부/용두가 영입할 대상: "+data["recruited"]);
      break;
    case "recruit_success":
      addchat(data["who"]+"님이 영입 제안을 수락하고 "+colored(data["role"])+"(으)로 합류했습니다!");
      break;
    case "recruit_failed":
      addchat("대상이 영입 제안을 거절했습니다.");
      break;
    case 'Witch_control_success':
      addchat('당신은 '+data['target1']+'님을 '+data['target2']+'님에게 가도록 조종했습니다.', 'Orchid');
      break;
    case 'controlled_by_Witch':
      addchat('마녀에게 조종당하고 있습니다!', '#6622CC');
      break;
    case 'blocked':
      addchat('아리따운 누군가가 당신을 찾아왔습니다. 당신은 그녀와 황홀한 밤을 보냈습니다. 능력이 차단되었습니다.', 'magenta');
      break;
    case "kill_blocker":
      addchat("아리따운 누군가가 당신을 찾아와 같이 밤을 보내려 하지만, 당신은 다른 생각을 품고 있습니다.");
      break;
    case "target_is_immune_to_block":
      addchat("대상이 같이 밤을 보내려는 당신을 돌려보냈습니다. 대상은 능력 차단에 면역입니다!", "limegreen");
      break;
    case "someone_hides_behind_you":
      addchat("누군가 당신 뒤에 숨었습니다!");
      break;
    case "blackmailed":
      addchat("누군가 찾아와 내일 입을 열었다가는 해코지를 당할 것이라 협박했습니다. 당신은 내일 하루종일 입을 꾹 닫기로 했습니다.", "red");
      break;
    case "attack_failed":
      addchat("공격에 실패했습니다. 오늘 밤 대상의 방어수준은 당신의 공격 수준 이상이었습니다.");
      break;
    case 'oiling_success':
      addchat('당신은 '+data['target1']+'님에게 기름을 묻혔습니다.', "#ffaa00");
      break;
    case "oiled":
      addchat("누군가가 당신 집에 휘발유를 잔뜩 뿌렸습니다. 당신은 기름에 흠뻑 젖었습니다!", '#ffaa00');
      break;
    case "visited_cult":
      addchat(`당신이 방문한 사람은 ${colored("이교도")}였습니다. 당신은 그를 죽였습니다.`);
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
    case "remaining_ability_opportunity":
      addchat("능력을 사용할 기회가 "+data["remaining_ability_opportunity"]+"번 남았습니다.");
      break;
    case 'check_result':
      switch (data['role']) {
        case "검시관":
          addchat("대상의 직업은 "+colored(data["result"]["role"])+"입니다.");
          if (data["result"]["lw"]) {
            addchat("대상은 유언을 남겼습니다:");
            addchat(data["lw"], "yellow");
          } else {
            addchat("대상이 유언을 남기지 않았거나, 유언이 수거되어 발견할 수 없습니다.");
          }
          switch (data["result_type"]) {
            case 3:
              for (const [index, visitors] of data["result"]["visitors"].entries()) {
                let night = index + 1;
                addchat(`${night}번째 밤, 대상을 ${visitors} 등이 방문했습니다.`);
              }
              break;
            case 2:
              for (const [index, visitors] of data["result"]["visitors"].entries()) {
                let night = index + 1;
                addchat(`${night}번째 밤, 대상을 ${visitors} 등이 방문했습니다.`);
              }
              break;
            case 1:
              for (const [index, visitors] of data["result"]["visitors"].entries()) {
                let night = index + 1;
                addchat(`${night}번째 밤, 대상을 ${visitors} 등이 방문했습니다.`);
              }
              break;
            case 0:
              addchat("대상의 사망 정보가 인멸되어 아무것도 발견할 수 없었습니다.");
              break;
          }
          break;
        case '탐정':
          if (typeof data['result'] === 'object') {
            let crimeList = [];
            for (const [crime, did] of Object.entries(data['result'])) {
              if (did) {
                crimeList.push(crime);
              }
            }
            addchat('대상이 저지른 범죄: ' + crimeList);
          } else { // 정확한 직업을 알 수 있는 경우
            addchat('대상의 직업은' + data['result'] + '입니다.');
          }
          break;
        case '형사':
          addchat('대상은 오늘 밤 ' + data['result'] + '님을 방문했습니다.');
          break;
        case '감시자':
          addchat('오늘 밤 ' + data['result'] + '님이 대상을 방문했습니다.');
          break;
        case '보안관':
          if (data['result']) {
            addchat('대상은 ' + colored(data['result']) + '입니다!!!');
          } else {
            addchat('대상은 수상하지 않습니다.');
          }
          break;
        case "요원":
        case "선봉":
          addchat("대상은 오늘 밤 " + data["result"]["visiting"]+"님을 방문했습니다.");
          addchat("오늘 밤 " + data["result"]["visited_by"]+"님이 대상을 방문했습니다.");
          break;
        case "조언자":
        case "백지선":
          if (typeof data['result'] === 'object') {
            let crimeList = [];
            for (const [crime, did] of Object.entries(data['result'])) {
              if (did) {
                crimeList.push(crime);
              }
            }
            addchat('대상이 저지른 범죄: ' + crimeList);
          } else { // 정확한 직업을 알 수 있는 경우
            addchat('대상의 직업은' + data['result'] + '입니다.');
          }
          break;
      }
      break;
    case "spy_result":
      addchat("오늘 밤 "+colored(ata["team"])+" 중 한 명이 "+data["result"]+"님을 방문했습니다.");
      break;
    case "sanitized_lw":
      if (data["lw"]) {
        addchat("대상이 남긴 유언:");
        addchat(data["lw"], "yellow");
      } else {
        addchat("대상은 유언을 남기지 않았습니다.");
      }
      break;
    case "the_dead_is_sanitized":
      addchat("우리는 " +data["who"]+"님의 유언을 찾을 수 없었습니다.");
      break;
    case "executed":
      addchat(data["who"]+"님이 형장의 이슬로 사라졌습니다.");
      break;
    case "executioner_target":
      addchat("당신의 목표는 "+data["target"]+"입니다.");
      break;
    case "execution_success":
      addchat("당신은 성공하여 안도의 한숨을 내쉬었습니다...", "#00bf00");
      break;
    case 'dead':
      if (data['dead_while_guarding']) {
        addchat('당신은 '+data['attacker']+'에게서 대상을 지키고 대신 사망했습니다.', 'red');
      } else if (data["attacker"]=="VOTE") {
        addchat("당신은 투표로 사형당했습니다.", "red");
      } else if (data["attacker"]=="마녀") {
        addchat("당신은 마녀의 저주를 맞아 죽었습니다.", "red");
      } else {
        addchat("당신은 "+data["attacker"]+"에게 죽었습니다.", "red");
      }
      break;
    case 'attacked':
      addchat('당신은 '+data['attacker']+'에게 공격당했습니다.', 'red');
      break;
    case 'healed':
      addchat('당신은 '+data['attacker']+'에게 공격당했습니다.', 'red');
      setTimeout(addchat('그러나 '+data['healer']+'가 당신을 살려주었습니다.', '#00bf00'), 500);
      break;
    case 'bodyguarded':
      addchat('당신은 '+data['attacker']+'에게 공격당했습니다.', 'red');
      setTimeout(addchat('그러나 경호원이 당신을 보호해주었습니다.', '#00bf00'), 500);
      break;
    case 'suicide':
      switch (data['reason']) {
        case '고의':
          addchat('당신은 자살했습니다.', 'red');
          break;
        case '어릿광대':
          addchat('당신은 어릿광대를 죽였다는 죄책감에 못이겨 자살했습니다.', 'red');
          break;
        case "마녀":
          addchat("당신은 마녀에게 조종되어 자살당했습니다.", 'red');
          break;
        case "잠입자":
          addchat("당신은 잠입자에게 조종되어 자살당했습니다.", "red");
          break;
        case "사기꾼":
          addchat("당신은 사기꾼에게 조종되어 자살당했습니다.", "red");
          break;
      }
      break;
    case "target_is_attacked":
      addchat("대상은 오늘 밤 공격받았습니다!");
      break;
    case "dead_announced":
      addchat(data["dead"]+"님이 사망했습니다.");
      break;
    case "dead_reason":
      addchat(`대상은 ${data["reason"]}에게 죽었습니다.`);
      break;
    case "role_announced":
      addchat(data["who"]+"님의 직업은 "+colored(data["role"])+"입니다.");
      break;
    case "unable_to_edit_lw":
      addchat(data["reason"]);
      break;
    case "wrote_lw":
      addchat("죽음에 대비해 유언을 작성했습니다.");
      addchat(data["lw"], "yellow");
      break;
    case "lw_query":
      addchat(data["whose"]+"님의 유언을 열람합니다.");
      addchat(data["lw"], "yellow");
      break;
    case "lw_announced":
      if (data["lw"]=="") {
        addchat(data["dead"]+"님은 유언을 남기지 않았습니다.");
      } else {
        addchat(data["dead"]+"님은 유언을 남겼습니다:");
        addchat(data["lw"], "yellow");
      }
      break;
    case "lw_edit":
      document.querySelector(".lw_modal").style.display = "block";
      document.querySelector("#lw").value = data["lw"];
      break;
    case "will_remember":
      addchat("오늘밤 기억할 대상: "+data["remember_target"]);
      break;
    case "role_converted":
      addchat(colored(data["convertor"])+"의 능력으로 직업이 "+colored(data["role"])+"(으)로 바뀌었습니다.");
      break;
    default:
      addchat(data);
  }
});

export {addchat};
