import random
import asyncio
import aiosqlite
import random
import string
import json
import inspect
import sqlite3
from sanic.log import logger
from datetime import datetime, timedelta

from . import roles

# TODO: 마녀 저주 5밤 이후부터 써지도록 수정: 해결
# TODO: 죽은 사람에게 투표 안 되도록 수정: 해결
# TODO: 마녀 저주 때 emit_sound 하도록 수정
# TODO: will_curse 이벤트 프론트엔드에서 받도록 수정
# TODO: 판사 구현: 해결
# TODO: 대부-마피아 일원 살인 일원화 구현: 해결
# TODO: 기억상실자
# TODO: 사인 공개되도록 수정
# TODO: 정보원은 마피아/삼합회가 존재해야만 등장할 수 있도록 수정

def validate_setup(setup):
    # type and range check
    role_setting = setup["options"]["role_setting"]
    assert isinstance(role_setting[roles.Citizen.name]["bulletproof"], bool)
    assert isinstance(role_setting[roles.Citizen.name]["win_1v1"], bool)
    assert isinstance(role_setting[roles.Citizen.name]["recruitable"], bool)
    assert isinstance(role_setting[roles.Sheriff.name]["detect_mafia_and_triad"], bool)
    assert isinstance(role_setting[roles.Sheriff.name]['detect_SerialKiller'], bool)
    assert isinstance(role_setting[roles.Sheriff.name]["detect_Arsonist"], bool)
    assert isinstance(role_setting[roles.Sheriff.name]["detect_Cult"], bool)
    assert isinstance(role_setting[roles.Sheriff.name]["detect_MassMurderer"], bool)
    assert isinstance(role_setting[roles.Investigator.name]["detect_exact_role"], bool)
    assert isinstance(role_setting[roles.Detective.name]["ignore_detection_immune"], bool)
    assert isinstance(role_setting[roles.Lookout.name]["ignore_detection_immune"], bool)
    assert isinstance(role_setting[roles.Doctor.name]["knows_if_attacked"], bool)
    assert isinstance(role_setting[roles.Doctor.name]["prevents_cult_conversion"], bool)
    assert isinstance(role_setting[roles.Doctor.name]["knows_if_culted"], bool)
    assert isinstance(role_setting[roles.Doctor.name]["WitchDoctor_when_converted"], bool)
    assert isinstance(role_setting[roles.Escort.name]["cannot_be_blocked"], bool)
    assert isinstance(role_setting[roles.Escort.name]["detects_block_immune_target"], bool)
    assert isinstance(role_setting[roles.Escort.name]["recruitable"], bool)
    assert role_setting[roles.Jailor.name]["execution_chance"] in {1, 2, 3, 999}
    assert role_setting[roles.Vigilante.name]["kill_chance"] in {1, 2, 3, 4, 999}
    assert isinstance(role_setting[roles.Vigilante.name]["suicides_if_shot_town"], bool)
    assert isinstance(role_setting[roles.Mason.name]["promoted_if_alone"], bool)
    assert role_setting[roles.MasonLeader.name]["recruit_chance"] in {2, 3, 4, 999}
    assert isinstance(role_setting[roles.Coroner.name]["discover_all_targets"], bool)
    assert isinstance(role_setting[roles.Coroner.name]["discover_lw"], bool)
    assert isinstance(role_setting[roles.Coroner.name]["discover_death_type"], bool)
    assert isinstance(role_setting[roles.Coroner.name]["discover_visitor_role"], bool)
    assert role_setting[roles.Bodyguard.name]["offense_level"] in {1, 2}
    assert isinstance(role_setting[roles.Bodyguard.name]["unhealable"], bool)
    assert isinstance(role_setting[roles.Bodyguard.name]["prevents_conversion"], bool)
    assert role_setting[roles.Veteran.name]["alert_chance"] in {2, 3, 999}
    assert role_setting[roles.Veteran.name]["offense_level"] in {1, 2}
    assert isinstance(role_setting[roles.Mayor.name]["lose_extra_votes"], bool)
    assert role_setting[roles.Mayor.name]["extra_votes"] in {2, 3, 4}
    assert isinstance(role_setting[roles.Mayor.name]["unhealable"], bool)
    assert role_setting[roles.Marshall.name]["lynch_chance"] in {1, 2}
    assert role_setting[roles.Marshall.name]["executions_per_group"] in {2, 3, 4}
    assert isinstance(role_setting[roles.Marshall.name]["unhealable"], bool)
    assert isinstance(role_setting[roles.Consigliere.name]["promoted_if_no_Godfather"], bool)
    assert isinstance(role_setting[roles.Consigliere.name]["detect_exact_role"], bool)
    assert isinstance(role_setting[roles.Consigliere.name]["becomes_mafioso"], bool)
    assert role_setting[roles.Godfather.name]["defense_level"] in {0, 1}
    assert isinstance(role_setting[roles.Godfather.name]["cannot_be_blocked"], bool)
    assert isinstance(role_setting[roles.Godfather.name]["detection_immune"], bool)
    assert isinstance(role_setting[roles.Godfather.name]["killable_without_mafioso"], bool)
    assert isinstance(role_setting[roles.Consort.name]["cannot_be_blocked"], bool)
    assert isinstance(role_setting[roles.Consort.name]["detects_block_immune_target"], bool)
    assert isinstance(role_setting[roles.Consort.name]["becomes_mafioso"], bool)
    assert isinstance(role_setting[roles.Framer.name]["detection_immune"], bool)
    assert isinstance(role_setting[roles.Framer.name]["becomes_mafioso"], bool)
    assert role_setting[roles.Janitor.name]["sanitize_chance"] in {1, 2, 3, 999}
    assert isinstance(role_setting[roles.Janitor.name]["becomes_mafioso"], bool)
    assert isinstance(role_setting[roles.Blackmailer.name]["can_talk_during_trial"], bool)
    assert isinstance(role_setting[roles.Blackmailer.name]["becomes_mafioso"], bool)
    assert isinstance(role_setting[roles.Kidnapper.name]["can_jail_members"], bool)
    assert isinstance(role_setting[roles.Kidnapper.name]["becomes_mafioso"], bool)
    assert role_setting[roles.Agent.name]["nights_between_shadowings"] in {0, 1, 2}
    assert isinstance(role_setting[roles.Agent.name]["becomes_mafioso"], bool)
    assert role_setting[roles.Beguiler.name]["hide_chance"] in {2, 3, 4}
    assert isinstance(role_setting[roles.Beguiler.name]["target_is_notified"], bool)
    assert isinstance(role_setting[roles.Beguiler.name]["can_hide_behind_member"], bool)
    assert isinstance(role_setting[roles.Beguiler.name]["becomes_mafioso"], bool)
    assert isinstance(role_setting[roles.Administrator.name]["promoted_if_no_Dragonhead"], bool)
    assert isinstance(role_setting[roles.Administrator.name]["detect_exact_role"], bool)
    assert isinstance(role_setting[roles.Administrator.name]["becomes_enforcer"], bool)
    assert role_setting[roles.DragonHead.name]["defense_level"] in {0, 1}
    assert isinstance(role_setting[roles.DragonHead.name]["cannot_be_blocked"], bool)
    assert isinstance(role_setting[roles.DragonHead.name]["detection_immune"], bool)
    assert isinstance(role_setting[roles.DragonHead.name]["killable_without_enforcer"], bool)
    assert isinstance(role_setting[roles.Liaison.name]["cannot_be_blocked"], bool)
    assert isinstance(role_setting[roles.Liaison.name]["detects_block_immune_target"], bool)
    assert isinstance(role_setting[roles.Liaison.name]["becomes_enforcer"], bool)
    assert isinstance(role_setting[roles.Forger.name]["detection_immune"], bool)
    assert isinstance(role_setting[roles.Forger.name]["becomes_enforcer"], bool)
    assert role_setting[roles.IncenseMaster.name]["sanitize_chance"] in {1, 2, 3, 999}
    assert isinstance(role_setting[roles.IncenseMaster.name]["becomes_enforcer"], bool)
    assert isinstance(role_setting[roles.Silencer.name]["can_talk_during_trial"], bool)
    assert isinstance(role_setting[roles.Silencer.name]["becomes_enforcer"], bool)
    assert isinstance(role_setting[roles.Interrogator.name]["can_jail_members"], bool)
    assert isinstance(role_setting[roles.Interrogator.name]["becomes_enforcer"], bool)
    assert role_setting[roles.Vanguard.name]["nights_between_shadowings"] in {0, 1, 2}
    assert isinstance(role_setting[roles.Vanguard.name]["becomes_enforcer"], bool)
    assert role_setting[roles.Deceiver.name]["hide_chance"] in {2, 3, 4}
    assert isinstance(role_setting[roles.Deceiver.name]["target_is_notified"], bool)
    assert isinstance(role_setting[roles.Deceiver.name]["can_hide_behind_member"], bool)
    assert isinstance(role_setting[roles.Deceiver.name]["becomes_enforcer"], bool)
    assert role_setting[roles.Survivor.name]["bulletproof_chance"] in {0, 1, 2, 3, 4}
    assert isinstance(role_setting[roles.Amnesiac.name]["revealed"], bool)
    assert isinstance(role_setting[roles.Amnesiac.name]["cannot_remember_town"], bool)
    assert isinstance(role_setting[roles.Amnesiac.name]["cannot_remember_mafia_and_triad"], bool)
    assert isinstance(role_setting[roles.Amnesiac.name]["cannot_remember_killing_role"], bool)
    assert isinstance(role_setting[roles.Jester.name]["randomly_suicide"], bool)
    assert isinstance(role_setting[roles.Executioner.name]["becomes_Jester"], bool)
    assert isinstance(role_setting[roles.Executioner.name]["target_is_town"], bool)
    assert isinstance(role_setting[roles.Executioner.name]["win_if_survived"], bool)
    assert role_setting[roles.Executioner.name]["defense_level"] in {0, 1}
    assert isinstance(role_setting[roles.Witch.name]["can_control_self"], bool)
    assert isinstance(role_setting[roles.Witch.name]["target_is_notified"], bool)
    assert isinstance(role_setting[roles.Witch.name]["WitchDoctor_when_converted"], bool)
    assert isinstance(role_setting[roles.Auditor.name]["can_audit_mafia"], bool)
    assert isinstance(role_setting[roles.Auditor.name]["can_audit_triad"], bool)
    assert isinstance(role_setting[roles.Auditor.name]["can_audit_night_immune"], bool)
    assert role_setting[roles.Auditor.name]["audit_chance"] in {2, 3, 4}
    assert role_setting[roles.Judge.name]["court_chance"] in {1, 2}
    assert role_setting[roles.Judge.name]["nights_between_court"] in {0, 1}
    assert role_setting[roles.Judge.name]["extra_votes"] in {2, 3, 4}
    assert isinstance(role_setting[roles.Cultist.name]["can_convert_night_immune"], bool)
    assert role_setting[roles.Cultist.name]["nights_between_conversion"] in {0, 1}
    assert role_setting[roles.WitchDoctor.name]["save_chance"] in {1, 2, 3, 999}
    assert role_setting[roles.WitchDoctor.name]["night_between_save"] in {0, 1}
    assert isinstance(role_setting[roles.WitchDoctor.name]["detection_immune"], bool)
    assert role_setting[roles.SerialKiller.name]["defense_level"] in {0, 1}
    assert isinstance(role_setting[roles.SerialKiller.name]["kill_blocker"], bool)
    assert isinstance(role_setting[roles.SerialKiller.name]["win_if_1v1_with_Arsonist"], bool)
    assert isinstance(role_setting[roles.SerialKiller.name]["detection_immune"], bool)
    assert role_setting[roles.MassMurderer.name]["defense_level"] in {0, 1}
    assert isinstance(role_setting[roles.MassMurderer.name]["can_visit_self"], bool)
    assert role_setting[roles.MassMurderer.name]["nights_between_murder"] in {0, 1, 2}
    assert isinstance(role_setting[roles.MassMurderer.name]["detection_immune"], bool)
    assert role_setting[roles.Arsonist.name]["offense_level"] in {1, 3}
    assert role_setting[roles.Arsonist.name]["defense_level"] in {0, 1}
    assert isinstance(role_setting[roles.Arsonist.name]["fire_spreads"], bool)
    assert isinstance(role_setting[roles.Arsonist.name]["target_is_notified"], bool)
    assert isinstance(role_setting[roles.Arsonist.name]["douse_blocker"], bool)
    assert isinstance(role_setting["모든 무작위직"]["excludes_killing_role"], bool)
    assert isinstance(role_setting["모든 무작위직"]["excludes_mafia"], bool)
    assert isinstance(role_setting["모든 무작위직"]["excludes_triad"], bool)
    assert isinstance(role_setting["모든 무작위직"]["excludes_neutral"], bool)
    assert isinstance(role_setting["모든 무작위직"]["excludes_town"], bool)
    assert isinstance(role_setting['시민 무작위직']["excludes_killing_role"], bool)
    assert isinstance(role_setting["시민 무작위직"]["excludes_government"], bool)
    assert isinstance(role_setting["시민 무작위직"]["excludes_investigative"], bool)
    assert isinstance(role_setting["시민 무작위직"]["excludes_protective"], bool)
    assert isinstance(role_setting["시민 무작위직"]["excludes_power"], bool)
    assert isinstance(role_setting["시민 행정직"]["excludes_citizen"], bool)
    assert isinstance(role_setting["시민 행정직"]["excludes_mason"], bool)
    assert isinstance(role_setting["시민 행정직"]["excludes_mayor_and_marshall"], bool)
    assert isinstance(role_setting["시민 행정직"]["excludes_masonleader"], bool)
    assert isinstance(role_setting["시민 행정직"]["excludes_crier"], bool)
    assert isinstance(role_setting["시민 조사직"]["excludes_coroner"], bool)
    assert isinstance(role_setting["시민 조사직"]["excludes_sheriff"], bool)
    assert isinstance(role_setting["시민 조사직"]["excludes_investigator"], bool)
    assert isinstance(role_setting["시민 조사직"]["excludes_detective"], bool)
    assert isinstance(role_setting["시민 조사직"]["excludes_lookout"], bool)
    assert isinstance(role_setting["시민 방어직"]["excludes_bodyguard"], bool)
    assert isinstance(role_setting["시민 방어직"]["excludes_doctor"], bool)
    assert isinstance(role_setting["시민 방어직"]["excludes_escort"], bool)
    assert isinstance(role_setting["시민 살인직"]["excludes_veteran"], bool)
    assert isinstance(role_setting["시민 살인직"]["excludes_jailor"], bool)
    assert isinstance(role_setting["시민 살인직"]["excludes_bodyguard"], bool)
    assert isinstance(role_setting["시민 살인직"]["excludes_vigilante"], bool)
    assert isinstance(role_setting["시민 능력직"]["excludes_veteran"], bool)
    assert isinstance(role_setting["시민 능력직"]["excludes_spy"], bool)
    assert isinstance(role_setting["시민 능력직"]["excludes_jailor"], bool)
    assert isinstance(role_setting["마피아 무작위직"]["excludes_killing_role"], bool)
    assert isinstance(role_setting["마피아 살인직"]["excludes_kidnapper"], bool)
    assert isinstance(role_setting["마피아 살인직"]["excludes_mafioso"], bool)
    assert isinstance(role_setting["마피아 살인직"]["excludes_godfather"], bool)
    assert isinstance(role_setting["마피아 지원직"]["excludes_blackmailer"], bool)
    assert isinstance(role_setting["마피아 지원직"]["excludes_kidnapper"], bool)
    assert isinstance(role_setting["마피아 지원직"]["excludes_consort"], bool)
    assert isinstance(role_setting['마피아 지원직']["excludes_consigliere"], bool)
    assert isinstance(role_setting["마피아 지원직"]["excludes_agent"], bool)
    assert isinstance(role_setting["마피아 속임수직"]["excludes_framer"], bool)
    assert isinstance(role_setting["마피아 속임수직"]["excludes_janitor"], bool)
    assert isinstance(role_setting["마피아 속임수직"]["excludes_beguiler"], bool)
    assert isinstance(role_setting["삼합회 무작위직"]["excludes_killing_role"], bool)
    assert isinstance(role_setting["삼합회 살인직"]["excludes_interrogator"], bool)
    assert isinstance(role_setting["삼합회 살인직"]["excludes_enforcer"], bool)
    assert isinstance(role_setting["삼합회 살인직"]["excludes_dragonhead"], bool)
    assert isinstance(role_setting["삼합회 지원직"]["excludes_silencer"], bool)
    assert isinstance(role_setting["삼합회 지원직"]["excludes_interrogator"], bool)
    assert isinstance(role_setting["삼합회 지원직"]["excludes_liaison"], bool)
    assert isinstance(role_setting['삼합회 지원직']["excludes_administrator"], bool)
    assert isinstance(role_setting["삼합회 지원직"]["excludes_vanguard"], bool)
    assert isinstance(role_setting["삼합회 속임수직"]["excludes_forger"], bool)
    assert isinstance(role_setting["삼합회 속임수직"]["excludes_incensemaster"], bool)
    assert isinstance(role_setting["삼합회 속임수직"]["excludes_deceiver"], bool)
    assert isinstance(role_setting["중립 무작위직"]["excludes_killing_role"], bool)
    assert isinstance(role_setting["중립 무작위직"]["excludes_evil"], bool)
    assert isinstance(role_setting["중립 무작위직"]["excludes_benign"], bool)
    assert isinstance(role_setting["중립 살인직"]["excludes_serialkiller"], bool)
    assert isinstance(role_setting["중립 살인직"]["excludes_arsonist"], bool)
    assert isinstance(role_setting["중립 살인직"]["excludes_massmurderer"], bool)
    assert isinstance(role_setting["중립 악"]["excludes_killing_role"], bool)
    assert isinstance(role_setting["중립 악"]["excludes_cults"], bool)
    assert isinstance(role_setting["중립 악"]["excludes_witch"], bool)
    assert isinstance(role_setting["중립 악"]["excludes_judge"], bool)
    assert isinstance(role_setting["중립 악"]["excludes_auditor"], bool)
    assert isinstance(role_setting["중립 선"]["excludes_survivor"], bool)
    assert isinstance(role_setting["중립 선"]["excludes_jester"], bool)
    assert isinstance(role_setting["중립 선"]["excludes_executioner"], bool)
    assert isinstance(role_setting["중립 선"]["excludes_amnesiac"], bool)
    time_setup = setup["options"]["time_setup"]
    assert 1.0<=time_setup["day_time"]<=6.0
    assert 0.5<=time_setup["night_time"]<=2.0
    assert 0.5<=time_setup["discussion_time"]<=3.0
    assert 0.5<=time_setup["court_time"]<=2.0
    select_setup = setup["options"]["select_setup"]
    assert select_setup["initial_state"] in {"MORNING", "MORNING_WITHOUT_COURT", "NIGHT"}
    assert select_setup["night_type"] in {"normal", "reason", "classic"}
    checkbox_setup = setup["options"]["checkbox_setup"]
    assert isinstance(checkbox_setup["whisper_allowed"], bool)
    assert isinstance(checkbox_setup["use_discussion_time"], bool)
    assert isinstance(checkbox_setup["pause_daytime"], bool)
    assert isinstance(checkbox_setup["use_defense_time"], bool)
    # logic check
    sheriff_can = role_setting["보안관"]
    assert sheriff_can["detect_mafia_and_triad"] or sheriff_can["detect_SerialKiller"] or sheriff_can["detect_Arsonist"] or sheriff_can["detect_Cult"] or sheriff_can["detect_MassMurderer"]
    formation = setup["formation"]
    assert formation.count("시장")<2
    assert formation.count("원수")<2
    assert formation.count("포고꾼")<2
    assert formation.count("비밀조합장")<2
    assert formation.count("대부")<2
    assert formation.count("용두")<2
    assert formation.count("판사")<2
    assert formation.count("요술사")<2

def remove_roles_from_pool(pool, category):
    if isinstance(category, list):
        for constructor in pool:
            for role in category:
                remove_roles_from_pool(pool, role)
    else:
        if category is roles.Mason: # roles.MasonLeader가 roles.Mason을 상속하기 때문에 Mason만 지우고 MasonLeader를 지우지 않으려면 이렇게 해야 함
            for constructor in pool:
                pool[:] = [constructor for constructor in pool if not issubclass(constructor, roles.Mason) or issubclass(constructor, roles.MasonLeader)]
        else:
            for constructor in pool:
                pool[:] = [constructor for constructor in pool if not issubclass(constructor, category)]

def distribute_roles(formation)->list:
    distributed = []
    fixed = [constructor for constructor in formation if inspect.isclass(constructor)]
    pools = [pool for pool in formation if isinstance(pool, list)]
    pools = sorted(pools, key=lambda pool: bool([role for role in pool if issubclass(role, roles.Mafia) or issubclass(role, roles.Triad)]), reverse=True)
    pools = sorted(pools, key=lambda pool: roles.Cult in pool or roles.WitchDoctor in pool or roles.Auditor in pool, reverse=True)
    distributed = fixed
    for pool in pools:
        while True:
            picked = random.choice(pool)
            if picked in (roles.Mayor, roles.Marshall,
                          roles.Crier, roles.MasonLeader,
                          roles.Godfather, roles.DragonHead,
                          roles.Judge, roles.WitchDoctor) and picked in distributed:
                continue
            elif picked in (roles.Mason, roles.MasonLeader) and not (roles.Cultist in distributed or roles.WitchDoctor in distributed or roles.Auditor in distributed):
                continue
            elif picked is roles.Spy and not [role for role in distributed if issubclass(role, roles.Mafia) or issubclass(role, roles.Triad)]:
                continue
            elif picked is roles.Mayor and roles.Marshall in [role for role in distributed if role not in fixed]:
                continue
            elif picked is roles.Marshall and roles.Mayor in [role for role in distributed if role not in fixed]:
                continue
            else:
                break
        distributed.append(picked)
    return distributed

class GameRoom:
    def __init__(
        self, roomID, title, capacity, host, setup, password=""
    ):
        assert isinstance(title, str)
        assert isinstance(capacity, int)
        assert isinstance(password, str) or password is None
        self.roomID = roomID
        self.title = title
        self.capacity = capacity
        self.members = []
        self.readied = set()
        self.host = host
        self.setup = setup
        self.formation = []
        self.options = dict()
        self.password = password
        self.private = password!=""
        self.inGame = False
        self.justCreated = True
        self.message_record = []
        # self.apply_setup(setup)

    async def apply_setup(self, sio, setup):
        try:
            validate_setup(setup)
        except Exception as e:
            logger.warning(f"Applying setup failed in {self.roomID}. reason: {e}")
            data = {
                "type": "applying_setup_failed",
            }
            await self.emit_event(sio, data, room=self.roomID)
        else:
            self.formation = [] # 초기화
            self.options = dict() # 초기화
            role_pool = dict()
            category_pool = {
                "all_random": [],
                roles.Town: [],
                roles.TownGovernment: [],
                roles.TownProtective: [],
                roles.TownInvestigative: [],
                roles.TownKilling: [],
                roles.TownPower: [],
                roles.Mafia: [],
                roles.MafiaKilling: [],
                roles.MafiaDeception: [],
                roles.MafiaSupport: [],
                roles.Triad: [],
                roles.TriadKilling: [],
                roles.TriadDeception: [],
                roles.TriadSupport: [],
                roles.Neutral: [],
                roles.NeutralBenign: [],
                roles.NeutralEvil: [],
                roles.NeutralKilling: [],
            }
            for name, obj in inspect.getmembers(roles):
                if inspect.isclass(obj) and hasattr(obj, "name") and obj not in (roles.Scumbag, roles.Stump):
                    role_pool[obj.name]=obj
                    category_pool["all_random"].append(obj)
                    for category, pool in category_pool.items():
                        if category != "all_random" and issubclass(obj, category):
                            pool.append(obj)

            role_setting = setup["options"]["role_setting"]
            if role_setting["모든 무작위직"]["excludes_killing_role"]:
                remove_roles_from_pool(category_pool["all_random"], [roles.TownKilling, roles.MafiaKilling, roles.TriadKilling, roles.NeutralKilling])
            if role_setting["모든 무작위직"]["excludes_mafia"]:
                remove_roles_from_pool(category_pool["all_random"], roles.Mafia)
            if role_setting["모든 무작위직"]["excludes_triad"]:
                remove_roles_from_pool(category_pool["all_random"], roles.Triad)
            if role_setting["모든 무작위직"]["excludes_neutral"]:
                remove_roles_from_pool(category_pool["all_random"], roles.Neutral)
            if role_setting["모든 무작위직"]["excludes_town"]:
                remove_roles_from_pool(category_pool["all_random"], roles.Town)
            if role_setting["시민 무작위직"]["excludes_killing_role"]:
                remove_roles_from_pool(category_pool[roles.Town], roles.TownKilling)
            if role_setting["시민 무작위직"]["excludes_government"]:
                remove_roles_from_pool(category_pool[roles.Town], roles.TownGovernment)
            if role_setting["시민 무작위직"]["excludes_investigative"]:
                remove_roles_from_pool(category_pool[roles.Town], roles.TownInvestigative)
            if role_setting["시민 무작위직"]["excludes_protective"]:
                remove_roles_from_pool(category_pool[roles.Town], roles.TownProtective)
            if role_setting["시민 무작위직"]["excludes_power"]:
                remove_roles_from_pool(category_pool[roles.Town], roles.TownPower)
            if role_setting["시민 행정직"]["excludes_citizen"]:
                remove_roles_from_pool(category_pool[roles.TownGovernment], roles.Citizen)
            if role_setting["시민 행정직"]["excludes_mason"]:
                remove_roles_from_pool(category_pool[roles.TownGovernment], roles.Mason)
            if role_setting["시민 행정직"]["excludes_mayor_and_marshall"]:
                remove_roles_from_pool(category_pool[roles.TownGovernment], roles.Mayor)
                remove_roles_from_pool(category_pool[roles.TownGovernment], roles.Marshall)
            if role_setting["시민 행정직"]["excludes_masonleader"]:
                remove_roles_from_pool(category_pool[roles.TownGovernment], roles.MasonLeader)
            if role_setting["시민 행정직"]["excludes_crier"]:
                remove_roles_from_pool(category_pool[roles.TownGovernment], roles.Crier)
            if role_setting["시민 조사직"]["excludes_coroner"]:
                remove_roles_from_pool(category_pool[roles.TownInvestigative], roles.Coroner)
            if role_setting["시민 조사직"]["excludes_sheriff"]:
                remove_roles_from_pool(category_pool[roles.TownInvestigative], roles.Sheriff)
            if role_setting["시민 조사직"]["excludes_investigator"]:
                remove_roles_from_pool(category_pool[roles.TownInvestigative], roles.Investigator)
            if role_setting["시민 조사직"]["excludes_detective"]:
                remove_roles_from_pool(category_pool[roles.TownInvestigative], roles.Detective)
            if role_setting["시민 조사직"]["excludes_lookout"]:
                remove_roles_from_pool(category_pool[roles.TownInvestigative], roles.Lookout)
            if role_setting["시민 방어직"]["excludes_bodyguard"]:
                remove_roles_from_pool(category_pool[roles.TownProtective], roles.Bodyguard)
            if role_setting["시민 방어직"]["excludes_doctor"]:
                remove_roles_from_pool(category_pool[roles.TownProtective], roles.Doctor)
            if role_setting["시민 방어직"]["excludes_escort"]:
                remove_roles_from_pool(category_pool[roles.TownProtective], roles.Escort)
            if role_setting["시민 살인직"]["excludes_veteran"]:
                remove_roles_from_pool(category_pool[roles.TownKilling], roles.Veteran)
            if role_setting["시민 살인직"]["excludes_jailor"]:
                remove_roles_from_pool(category_pool[roles.TownKilling], roles.Jailor)
            if role_setting["시민 살인직"]["excludes_bodyguard"]:
                remove_roles_from_pool(category_pool[roles.TownKilling], roles.Bodyguard)
            if role_setting["시민 살인직"]["excludes_vigilante"]:
                remove_roles_from_pool(category_pool[roles.TownKilling], roles.Vigilante)
            if role_setting["시민 능력직"]["excludes_veteran"]:
                remove_roles_from_pool(category_pool[roles.TownPower], roles.Veteran)
            if role_setting["시민 능력직"]["excludes_spy"]:
                remove_roles_from_pool(category_pool[roles.TownPower], roles.Spy)
            if role_setting["시민 능력직"]["excludes_jailor"]:
                remove_roles_from_pool(category_pool[roles.TownPower], roles.Jailor)
            if role_setting["마피아 무작위직"]["excludes_killing_role"]:
                remove_roles_from_pool(category_pool[roles.Mafia], roles.MafiaKilling)
            if role_setting["마피아 살인직"]["excludes_kidnapper"]:
                remove_roles_from_pool(category_pool[roles.MafiaKilling], roles.Kidnapper)
            if role_setting["마피아 살인직"]["excludes_mafioso"]:
                remove_roles_from_pool(category_pool[roles.MafiaKilling], roles.Mafioso)
            if role_setting["마피아 살인직"]["excludes_godfather"]:
                remove_roles_from_pool(category_pool[roles.MafiaKilling], roles.Godfather)
            if role_setting["마피아 지원직"]["excludes_blackmailer"]:
                remove_roles_from_pool(category_pool[roles.MafiaSupport], roles.Blackmailer)
            if role_setting["마피아 지원직"]["excludes_kidnapper"]:
                remove_roles_from_pool(category_pool[roles.MafiaSupport], roles.Kidnapper)
            if role_setting["마피아 지원직"]["excludes_consort"]:
                remove_roles_from_pool(category_pool[roles.MafiaSupport], roles.Consort)
            if role_setting["마피아 지원직"]["excludes_consigliere"]:
                remove_roles_from_pool(category_pool[roles.MafiaSupport], roles.Consigliere)
            if role_setting["마피아 지원직"]["excludes_agent"]:
                remove_roles_from_pool(category_pool[roles.MafiaSupport], roles.Agent)
            if role_setting["마피아 속임수직"]["excludes_framer"]:
                remove_roles_from_pool(category_pool[roles.MafiaDeception], roles.Framer)
            if role_setting["마피아 속임수직"]["excludes_janitor"]:
                remove_roles_from_pool(category_pool[roles.MafiaDeception], roles.Janitor)
            if role_setting["마피아 속임수직"]["excludes_beguiler"]:
                remove_roles_from_pool(category_pool[roles.MafiaDeception], roles.Beguiler)
            if role_setting["삼합회 무작위직"]["excludes_killing_role"]:
                remove_roles_from_pool(category_pool[roles.Triad], roles.TriadKilling)
            if role_setting["삼합회 살인직"]["excludes_interrogator"]:
                remove_roles_from_pool(category_pool[roles.TriadKilling], roles.Interrogator)
            if role_setting["삼합회 살인직"]["excludes_enforcer"]:
                remove_roles_from_pool(category_pool[roles.TriadKilling], roles.Enforcer)
            if role_setting["삼합회 살인직"]["excludes_dragonhead"]:
                remove_roles_from_pool(category_pool[roles.TriadKilling], roles.Dragonhead)
            if role_setting["삼합회 지원직"]["excludes_silencer"]:
                remove_roles_from_pool(category_pool[roles.TriadSupport], roles.Silencer)
            if role_setting["삼합회 지원직"]["excludes_interrogator"]:
                remove_roles_from_pool(category_pool[roles.TriadSupport], roles.Interrogator)
            if role_setting["삼합회 지원직"]["excludes_liaison"]:
                remove_roles_from_pool(category_pool[roles.TriadSupport], roles.Liaison)
            if role_setting["삼합회 지원직"]["excludes_administrator"]:
                remove_roles_from_pool(category_pool[roles.TriadSupport], roles.Administrator)
            if role_setting["삼합회 지원직"]["excludes_vanguard"]:
                remove_roles_from_pool(category_pool[roles.TriadSupport], roles.Vanguard)
            if role_setting["삼합회 속임수직"]["excludes_forger"]:
                remove_roles_from_pool(category_pool[roles.TriadDeception], roles.Forger)
            if role_setting["삼합회 속임수직"]["excludes_incensemaster"]:
                remove_roles_from_pool(category_pool[roles.TriadDeception], roles.IncenseMaster)
            if role_setting["삼합회 속임수직"]["excludes_deceiver"]:
                remove_roles_from_pool(category_pool[roles.TriadDeception], roles.Deceiver)
            if role_setting["중립 무작위직"]["excludes_killing_role"]:
                remove_roles_from_pool(category_pool[roles.Neutral], roles.NeutralKilling)
            if role_setting["중립 무작위직"]["excludes_evil"]:
                remove_roles_from_pool(category_pool[roles.Neutral], roles.NeutralEvil)
            if role_setting["중립 무작위직"]["excludes_benign"]:
                remove_roles_from_pool(category_pool[roles.Neutral], roles.NeutralBenign)
            if role_setting["중립 살인직"]["excludes_serialkiller"]:
                remove_roles_from_pool(category_pool[roles.NeutralKilling], roles.SerialKiller)
            if role_setting["중립 살인직"]["excludes_arsonist"]:
                remove_roles_from_pool(category_pool[roles.NeutralKilling], roles.Arsonist)
            if role_setting["중립 살인직"]["excludes_massmurderer"]:
                remove_roles_from_pool(category_pool[roles.NeutralKilling], roles.MassMurderer)
            if role_setting["중립 악"]["excludes_killing_role"]:
                remove_roles_from_pool(category_pool[roles.NeutralEvil], roles.NeutralKilling)
            if role_setting["중립 악"]["excludes_cults"]:
                remove_roles_from_pool(category_pool[roles.NeutralEvil], roles.Cult)
            if role_setting["중립 악"]["excludes_witch"]:
                remove_roles_from_pool(category_pool[roles.NeutralEvil], roles.Witch)
            if role_setting["중립 악"]["excludes_judge"]:
                remove_roles_from_pool(category_pool[roles.NeutralEvil], roles.Judge)
            if role_setting["중립 악"]["excludes_auditor"]:
                remove_roles_from_pool(category_pool[roles.NeutralEvil], roles.Auditor)
            if role_setting["중립 선"]["excludes_survivor"]:
                remove_roles_from_pool(category_pool[roles.NeutralBenign], roles.Survivor)
            if role_setting["중립 선"]["excludes_jester"]:
                remove_roles_from_pool(category_pool[roles.NeutralBenign], roles.Jester)
            if role_setting["중립 선"]["excludes_executioner"]:
                remove_roles_from_pool(category_pool[roles.NeutralBenign], roles.Executioner)
            if role_setting["중립 선"]["excludes_amnesiac"]:
                remove_roles_from_pool(category_pool[roles.NeutralBenign], roles.Amnesiac)

            for role_name in setup["formation"]:
                if role_name in role_pool:
                    self.formation.append(role_pool[role_name])
                elif " " in role_name: # 무작위 직업
                    if role_name == "모든 무작위직":
                        self.formation.append(category_pool["all_random"])
                    elif role_name == "시민 무작위직":
                        self.formation.append(category_pool[roles.Town])
                    elif role_name == "시민 행정직":
                        self.formation.append(category_pool[roles.TownGovernment])
                    elif role_name == "시민 조사직":
                        self.formation.append(category_pool[roles.TownInvestigative])
                    elif role_name == "시민 방어직":
                        self.formation.append(category_pool[roles.TownProtective])
                    elif role_name == "시민 살인직":
                        self.formation.append(category_pool[roles.TownKilling])
                    elif role_name == "시민 능력직":
                        self.formation.append(category_pool[roles.TownPower])
                    elif role_name == "마피아 무작위직":
                        self.formation.append(category_pool[roles.Mafia])
                    elif role_name == "마피아 살인직":
                        self.formation.append(category_pool[roles.MafiaKilling])
                    elif role_name == "마피아 지원직":
                        self.formation.append(category_pool[roles.MafiaSupport])
                    elif role_name == "마피아 속임수직":
                        self.formation.append(category_pool[roles.MafiaDeception])
                    elif role_name == "삼합회 무작위직":
                        self.formation.append(category_pool[roles.Triad])
                    elif role_name == "삼합회 살인직":
                        self.formation.append(category_pool[roles.TriadKilling])
                    elif role_name == "삼합회 지원직":
                        self.formation.append(category_pool[roles.TriadSupport])
                    elif role_name == "삼합회 속임수직":
                        self.formation.append(category_pool[roles.TriadDeception])
                    elif role_name == "중립 무작위직":
                        self.formation.append(category_pool[roles.Neutral])
                    elif role_name == "중립 살인직":
                        self.formation.append(category_pool[roles.NeutralKilling])
                    elif role_name == "중립 악":
                        self.formation.append(category_pool[roles.NeutralEvil])
                    elif role_name == "중립 선":
                        self.formation.append(category_pool[roles.NeutralBenign])

            for index, slot in enumerate(self.formation):
                if slot == []:
                    self.formation[index] = [roles.Citizen]
                    logger.warning(f"role cannot be spawned due to the invalid formation in room #{self.roomID}")
                    data = {
                        "type": "warning",
                        "reason": "invalid_formation",
                        "slot_with_problem": index+1,
                    }
                    await self.emit_event(sio, data, room=self.roomID)
            data = {
                "type": "applying_setup_success",
            }
            await self.emit_event(sio, data, room=self.roomID)
            self.readied = set() # 설정이 바뀌면 준비 자동으로 풀림
            await self.emit_player_list(sio)

    def is_full(self):
        return len(self.members) >= self.capacity

    def write_to_record(self, sio, data, room, skip_sid):
        receivers = [p.nickname for p in self.players.values() if room in sio.rooms(p.sid) and p.sid not in (skip_sid or [])]
        self.message_record.append((datetime.now().strftime("%y/%m/%d %H:%M:%S"), str(data), str(receivers)))

    async def emit_event(self, sio, data, room, skip_sid=None):
        await sio.emit("event", data, room=room, skip_sid=skip_sid)
        if self.inGame:
            self.write_to_record(sio, data, room, skip_sid)

    async def handle_message(self, sio, sid, msg):
        async with sio.session(sid) as user:
            if msg == "": return
            msg = msg[:206] # 최대 글자수
            logger.info(f"[room #{self.roomID}] {user['nickname']}: {msg}")
            if msg == "/시행":
                distributed = distribute_roles(self.formation)
                result = [(index+1, role.name) for index, role in enumerate(distributed)]
                data = {
                    "type": "simulation",
                    "result": result,
                }
                await self.emit_event(sio, data, room=sid)
                return
            if not self.inGame:
                if msg.startswith("/유언편집"):
                    return
                if msg == "/준비":
                    if sid in self.readied:
                        self.readied.remove(sid)
                    else:
                        self.readied.add(sid)
                    await self.emit_player_list(sio)
                    return
                if msg == "/시작" and sid == self.host:
                    if len(self.members)<3:
                        data = {
                            "type": "unable_to_start",
                            "reason": "not_enough_members",
                            "required_members": 3,
                        }
                        await self.emit_event(sio, data, room=sid)
                        return
                    elif len(self.readied)!=len(self.members):
                        not_readied = await asyncio.gather(*[sio.get_session(sid) for sid in self.members if sid not in self.readied], return_exceptions=True)
                        not_readied = [session["nickname"] for session in not_readied if not isinstance(session, Exception)]
                        data = {
                            "type": "unable_to_start",
                            "reason": "not_readied",
                            "not_readied": not_readied,
                        }
                        await self.emit_event(sio, data, room=self.roomID)
                        return
                    await self.init_game(sio)
                    await self.run_game(sio)
                    await self.finish_game(sio)
                else:
                    data = {
                        "type": "message",
                        "who": user["nickname"],
                        "message": msg,
                    }
                    await self.emit_event(sio, data, room=self.roomID)
                return
            if user["nickname"] not in self.players: # 나중에 들어온 사람일 경우: hell에 입장한 상태임.
                data = {
                    "type": "message",
                    "who": user["nickname"],
                    "message": msg,
                    "hell": True,
                }
                await self.emit_event(sio, data, room=self.hell)
                return

            commander = self.players[user["nickname"]]
            if msg.startswith("/"):
                if msg.startswith("/유언편집") and commander.alive:
                    if self.STATE == "NIGHT":
                        data = {
                            "type": "unable_to_edit_lw",
                            "reason": "밤에는 유언을 작성할 수 없습니다.",
                        }
                        await self.emit_event(sio, data, room=sid)
                    elif msg == "/유언편집": # 그냥 /유언편집 만 치면 현재 자기 유언 보내주도록 설정
                        data = {
                            "type": "lw_edit",
                            "lw": commander.lw,
                        }
                        await self.emit_event(sio, data, room=sid)
                    else:
                        commander.lw = msg[6:206] # [5:]로 하면 /유언편집과 실제 유언 사이 공백 1칸이 포함됨
                        data = {
                            "type": "wrote_lw",
                            "lw": commander.lw,
                        }
                        await self.emit_event(sio, data, room=sid)
                msg = msg.split()
                if len(msg) == 3:
                    cmd, target1, target2 = msg
                    if target1 not in self.players:
                        return
                    if cmd!="/귓" and target2 not in self.players:
                        return
                elif len(msg) == 2:
                    cmd, target1 = msg
                    target2 = None
                    if target1 not in self.players:
                        return
                else:
                    cmd = msg[0]
                    target1 = target2 = None
                if target1 and commander is self.players[target1] and not commander.role.visitable_himself:
                    return
                elif cmd == "/유언" and target1 in self.players and not self.players[target1].alive:
                    data = {
                        "type": "lw_query",
                        "whose": target1,
                        "lw": self.players[target1].lw,
                    }
                    await self.emit_event(sio, data, room=sid)
                elif cmd == "/기억" and target1 in self.players and not self.players[target1].alive:
                    target = self.players[target1]
                    for banned in (roles.Mayor,
                                   roles.Marshall,
                                   roles.Judge,
                                   roles.Crier,
                                   roles.WitchDoctor,
                                   roles.Godfather,
                                   roles.DragonHead,
                                   roles.MasonLeader):
                        if isinstance(target.role, banned):
                            return
                    commander.remember_today = True
                    commander.remember_target = target
                    data = {
                        "type": "will_remember",
                        "remember_target": target.nickname,
                    }
                    await self.emit_event(sio, data, room=commander.sid)
                elif commander.jailed:
                    return
                # 이 이하로는 갇혔을 때 사용할 수 없는 명령어들
                elif (
                    cmd == "/감금"
                    and commander.alive
                    and self.STATE != "EVENING"
                    and self.STATE != "NIGHT"
                    and target1
                    and (
                        isinstance(commander.role, roles.Jailor)
                        or isinstance(commander.role, roles.Kidnapper)
                        or isinstance(commander.role, roles.Interrogator)
                    )
                ):
                    jailor = commander
                    to_jail = self.players[target1]
                    jailor.has_jailed_whom = to_jail
                    data = {
                        "type": "will_jail",
                        "whom": to_jail.nickname,
                    }
                    await self.emit_event(sio, data, room=commander.sid)
                elif (
                    cmd == "/발동"
                    and commander.alive
                    and isinstance(commander.role, roles.Mayor)
                    and self.STATE != "EVENING"
                    and self.STATE != "NIGHT"
                    and commander.votes != 4
                    and not commander.blackmailed
                ):
                    mayor = commander
                    mayor.votes = 4
                    data = {
                        "type": "mayor_ability_activation",
                        "who": mayor.nickname,
                    }
                    await self.emit_event(sio, data, room=self.roomID)
                    data = {
                        "type": "music",
                        "music": "mayor_normal",
                    }
                    await self.emit_event(sio, data, room=self.roomID)
                    mayor.crimes["부패"] = True
                elif commander==self.elected:
                    return
                # 이 이하로는 재판대에 섰을 때 사용할 수 없는 명령어들
                elif (
                    cmd == "/귓" # 귓속말
                    and self.STATE!="NIGHT"
                    and self.STATE!="EVENING"
                    and commander.alive
                    and not self.in_court
                    and not commander.blackmailed
                    and target1
                ):
                    whisper = target2
                    data = {
                        "type": "whispering",
                        "to": self.players[target1].nickname,
                        "message": whisper,
                    }
                    await self.emit_event(sio, data, room=commander.sid)
                    data = {
                        "type": "whispered",
                        "from": commander.nickname,
                        "message": whisper,
                    }
                    await self.emit_event(sio, data, room=self.players[target1].sid)
                elif (
                    cmd == "/개정" # 부패한 재판 개정
                    and (self.STATE=="DISCUSSION" or self.STATE=="VOTE")
                    and commander.alive
                    and isinstance(commander.role, roles.Judge)
                    and not self.in_court
                    and commander.role.ability_opportunity>0
                    and not commander.blackmailed
                ):
                    judge = commander
                    commander.votes = 3
                    self.in_court = True
                    commander.role.ability_opportunity -= 1
                    data = {
                        "type": "court",
                    }
                    await self.emit_event(sio, data, room=self.roomID)
                    data = {
                        "type": "music",
                        "music": "court_with_lynch" if self.in_lynch else "court_normal",
                    }
                    await self.emit_event(sio, data, room=self.roomID)
                    judge.crimes["부패"] = True
                elif (
                    cmd == "/개시" # 집단사형 개시
                    and (self.STATE == "DISCUSSION" or self.STATE=="VOTE")
                    and commander.alive
                    and isinstance(commander.role, roles.Marshall)
                    and not self.in_lynch
                    and commander.role.ability_opportunity>0
                    and not commander.blackmailed
                ):
                    marshall = commander
                    self.in_lynch = True
                    marshall.role.ability_opportunity-=1
                    data = {
                        "type": "marshall_ability_activation",
                        "who": marshall.nickname,
                    }
                    await self.emit_event(sio, data, room=self.roomID)
                    data = {
                        "type": "music",
                        "music": "court_with_lynch" if self.in_court else "marshall_normal",
                    }
                    await self.emit_event(sio, data, room=self.roomID)
                    marshall.crimes["부패"] = True

                elif cmd == "/투표" and self.STATE == "VOTE" and target1:
                    voter = commander
                    voted = self.players[target1]
                    if not voter.alive or not voted.alive:
                        return
                    if voter.has_voted:
                        self.cancel_vote(voter)
                        data = {
                            "type": "vote_cancel",
                            "voter": "???" if self.in_court else voter.nickname,
                        }
                        await self.emit_event(sio, data, room=self.roomID)
                    else:
                        voted = self.players[target1]
                        data = {
                            "type": "vote",
                            "voter": "???" if self.in_court else voter.nickname,
                            "voted": voted.nickname,
                        }
                        self.vote(voter, voted)
                        await self.emit_event(sio, data, room=self.roomID)
                elif cmd == "/유죄" and self.STATE == "VOTE_EXECUTION":
                    voter = commander
                    if not voter.alive:
                        return
                    if voter.has_voted:
                        self.cancel_vote(voter)
                        data = {
                            "type": "vote_cancel",
                            "voter": voter.nickname,
                        }
                        await self.emit_event(sio, data, room=self.roomID)
                    else:
                        self.vote_execution(voter, guilty=True)
                        data = {
                            "type": "vote_execution",
                            "voter": voter.nickname,
                        }
                        await self.emit_event(sio, data, room=self.roomID)
                elif cmd == "/무죄" and self.STATE == "VOTE_EXECUTION":
                    voter = commander
                    if not voter.alive:
                        return
                    if voter.has_voted:
                        self.cancel_vote(voter)
                        data = {
                            "type": "vote_cancel",
                            "voter": voter.nickname,
                        }
                        await self.emit_event(sio, data, room=self.roomID)
                    else:
                        self.vote_execution(voter, guilty=False)
                        data = {
                            "type": "vote_execution",
                            "voter": voter.nickname,
                        }
                        await self.emit_event(sio, data, room=self.roomID)
                elif (
                    cmd == "/방문"
                    and commander.alive
                    and self.STATE == "EVENING"
                    and target1
                    and ((not self.players[target1].alive) if isinstance(commander.role, roles.Coroner) else self.players[target1].alive)
                ):
                    visitor = commander
                    visited = self.players[target1]
                    if isinstance(commander.role, roles.Godfather):
                        self.Godfather_target = visited
                    elif isinstance(commander.role, roles.Mafioso) and not self.Godfather_target:
                        self.mafia_target = visited
                    elif isinstance(commander.role, roles.DragonHead):
                        self.DragonHead_target = visited
                    elif isinstance(commander.role, roles.Enforcer) and not self.DragonHead_target:
                        self.triad_target = visited
                    elif (
                        isinstance(visitor.role, roles.MassMurderer)
                        and visitor.cannot_murder_until >= self.day
                    ):
                        return
                    else:
                        visitor.target1 = visited
                    if target2 and (
                        isinstance(visitor.role, roles.Witch)
                        # or isinstance(visitor.role, roles.BusDriver)
                    ):
                        visitor.target2 = self.players[target2]
                    data = {
                        "type": "visit",
                        "visitor": visitor.nickname,
                        "role": visitor.role.name,
                        "target1": visited.nickname,
                        "target2": visitor.target2.nickname
                        if visitor.target2
                        else None,
                    }
                    for night_chatting_role in (roles.Mafia, roles.Triad, roles.Cult, roles.Mason):
                        if isinstance(visitor.role, night_chatting_role):
                            await self.emit_event(sio, data, room=self.night_chat[night_chatting_role])
                            break
                    else:
                        await self.emit_event(sio, data, room=visitor.sid)
                elif (
                    cmd == "/경계"
                    and self.STATE == "EVENING"
                    and isinstance(commander.role, roles.Veteran)
                    and commander.role.ability_opportunity>0
                ):
                    V = commander
                    V.alert_today = not V.alert_today
                    if V.alert_today:
                        V.role.defense_level = V.role.offense_level = 2
                    else:
                        V.role.defense_level = V.role.offense_level = 0
                    data = {
                        "type": "alert",
                        "alert": V.alert_today,
                    }
                    await self.emit_event(sio, data, room=V.sid)
                elif (
                    cmd == "/착용"
                    and commander.alive
                    and self.STATE == "EVENING"
                    and (
                        isinstance(commander.role, roles.Citizen)
                        or isinstance(commander.role, roles.Survivor)
                    )
                    and commander.role.ability_opportunity>0
                ):
                    wearer = commander
                    wearer.wear_vest_today = not wearer.wear_vest_today
                    data = {"type": "wear_vest", "wear_vest": wearer.wear_vest_today}
                    await self.emit_event(sio, data, room=wearer.sid)
                elif (
                    cmd == "/영입"
                    and commander.alive
                    and self.STATE == "EVENING"
                    and target1
                    and (
                        isinstance(commander.role, roles.Godfather)
                        or isinstance(commander.role, roles.DragonHead)
                    )
                ):
                    recruiter = commander
                    recruited = self.players[target1]
                    recruiter.recruit_target = recruited
                    data = {
                        "type": "will_recruit",
                        "recruited": recruited.nickname,
                    }
                    if isinstance(commander.role, roles.Godfather):
                        await self.emit_event(sio, data, room=self.night_chat[roles.Mafia])
                    else:
                        await self.emit_event(sio, data, room=self.night_chat[roles.Triad])
                elif cmd == "/처형" and commander.alive and self.STATE == "EVENING":
                    if (
                        isinstance(commander.role, roles.Jailor)
                        and commander.has_jailed_whom
                        and commander.role.ability_opportunity > 0
                    ):
                        commander.kill_the_jailed_today = (
                            not commander.kill_the_jailed_today
                        )
                        if commander.kill_the_jailed_today:
                            data = {
                                "type": "will_execute_the_jailed",
                                "executed": commander.has_jailed_whom.nickname,
                            }
                            await self.emit_event(sio, data, room=commander.has_jailed_whom.jailID)
                        else:
                            data = {
                                "type": "will_not_execute",
                            }
                            await self.emit_event(sio, data, room=commander.has_jailed_whom.jailID)
                    elif (
                        isinstance(commander.role, roles.Kidnapper)
                        or isinstance(commander.role, roles.Interrogator)
                    ) and commander.has_jailed_whom:
                        commander.kill_the_jailed_today = (
                            not commander.kill_the_jailed_today
                        )
                        if commander.kill_the_jailed_today:
                            data = {
                                "type": "will_execute_the_jailed",
                                "executed": commander.has_jailed_whom.nickname,
                            }
                            await self.emit_event(sio, data, room=commander.has_jailed_whom.jailID)
                        else:
                            data = {
                                "type": "will_not_execute",
                            }
                            await self.emit_events(sio, data, room=commander.has_jailed_whom.jailID)
                elif cmd == "/저주"\
                and commander.alive\
                and target1\
                and self.players[target1]\
                and isinstance(commander.role, roles.Witch)\
                and commander.role.ability_opportunity>0\
                and self.STATE == "EVENING"\
                and self.day>=5:
                    commander.curse_target = self.players[target1]
                    data = {
                        "type": "will_curse",
                        "cursed": commander.curse_target.nickname
                    }
                    await self.emit_event(sio, data, room=commander.sid)
                elif cmd == "/방화"\
                and commander.alive\
                and self.STATE == "EVENING":
                    commander.burn_today = True
                    data = {
                        "type": "will_burn_today",
                    }
                    await self.emit_event(sio, data, room=commander.sid)
            else:
                if commander not in self.alive_list:
                    data = {
                        "type": "message",
                        "who": user["nickname"],
                        "message": msg,
                        "hell": True,
                    }
                    await self.emit_event(sio, data, room=self.hell)
                elif self.STATE == "NIGHT":
                    return
                elif self.STATE == "EVENING" and not commander.blackmailed:
                    player = commander
                    if player.jailed:
                        data = {
                            "type": "message",
                            "who": player.nickname,
                            "message": msg,
                        }
                        await self.emit_event(sio, data, room=player.jailID)
                    elif (
                        isinstance(player.role, roles.Jailor) and player.has_jailed_whom
                    ):
                        data = {
                            "type": "message",
                            "who": roles.Jailor.name,
                            "message": msg,
                        }
                        await self.emit_event(sio, data, room=player.has_jailed_whom.jailID)
                    elif (
                        isinstance(player.role, roles.Kidnapper)
                        and player.has_jailed_whom
                    ):
                        skip_list = [
                            p.sid
                            for p in self.alive_list
                            if isinstance(p.role, roles.Mafia)
                        ]
                        data = {
                            "type": "message",
                            "who": roles.Jailor.name,
                            "message": msg,
                        }
                        await self.emit_event(sio, data, room=player.has_jailed_whom.jailID, skip_sid=skip_list)
                        data["who"] = player.nickname
                        await self.emit_event(sio, data, room=self.night_chat[roles.Mafia])
                    elif (
                        isinstance(player.role, roles.Interrogator)
                        and player.has_jailed_whom
                    ):
                        skip_list = [
                            p.sid
                            for p in self.alive_list
                            if isinstance(p.role, roles.Triad)
                        ]
                        data = {
                            "type": "message",
                            "who": roles.Jailor.name,
                            "message": msg,
                        }
                        await self.emit_event(sio, data, room=player.has_jailed_whom.jailID, skip_sid=skip_list)
                        data["who"] = player.nickname
                        await self.emit_event(sio, data, room=self.night_chat[roles.Triad])
                    elif isinstance(player.role, roles.Judge) or isinstance(
                        player.role, roles.Crier
                    ):
                        data = {
                            "type": "message",
                            "who": roles.Crier.name,
                            "message": msg,
                        }
                        await self.emit_event(sio, data, room=self.roomID)
                        player.crimes["치안을 어지럽힘"] = True
                    elif isinstance(player.role, roles.Mafia):
                        data = {
                            "type": "message",
                            "who": user["nickname"],
                            "message": msg,
                        }
                        await self.emit_event(sio, data, room=self.night_chat[roles.Mafia])
                        data["who"] = roles.Mafia.team
                        await self.emit_event(sio, data, room=self.night_chat[roles.Spy])
                    elif isinstance(player.role, roles.Triad):
                        data = {
                            "type": "message",
                            "who": user["nickname"],
                            "message": msg,
                        }
                        await self.emit_event(sio, data, room=self.night_chat[roles.Triad])
                        data["who"] = roles.Triad.team
                        await self.emit_event(sio, data, room=self.night_chat[roles.Spy])
                    elif isinstance(player.role, roles.Cult):
                        data = {
                            "type": "message",
                            "who": user["nickname"],
                            "message": msg,
                        }
                        await self.emit_event(sio, data, room=self.night_chat[roles.Cult])
                    elif isinstance(player.role, roles.Mason):
                        data = {
                            "type": "message",
                            "who": user["nickname"],
                            "message": msg,
                        }
                        await self.emit_event(sio, data, room=self.night_chat[roles.Mason])
                elif (self.STATE == "DEFENSE" or self.STATE=="VOTE_EXECUTION") and not commander.blackmailed:
                    data = {
                        "type": "message",
                        "who": user["nickname"],
                        "message": msg,
                        "from_elected": commander==self.elected,
                    }
                    await self.emit_event(sio, data, room=self.roomID)
                elif not commander.blackmailed or self.STATE=="LAST_WORD":
                    data = {
                        "type": "message",
                        "who": user["nickname"],
                        "message": msg,
                    }
                    if self.in_court:
                        data["who"]="재판관" if isinstance(commander.role, roles.Judge) else "배심원"
                        data["in_court"]=True
                    await self.emit_event(sio, data, room=self.roomID)

    def vote(self, voter, voted):
        assert self.STATE == "VOTE"
        alive = len([p for p in self.players.values() if p.alive])
        majority = alive // 2 + 1
        voter.has_voted = True
        voted.votes_gotten += voter.votes
        voter.voted_to_whom = voted
        if voted.votes_gotten >= majority:
            self.elected = voted
            self.election.set()

    def vote_execution(self, voter, guilty):
        assert self.STATE == "VOTE_EXECUTION"
        voter.has_voted = True
        if guilty:
            self.elected.voted_guilty += voter.votes
            voter.voted_to_which = "guilty"
        else:
            self.elected.voted_innocent += voter.votes
            voter.voted_to_which = "innocent"

    def cancel_vote(self, voter):
        voter.has_voted = False
        if self.STATE == "VOTE":
            voter.voted_to_whom.votes_gotten -= voter.votes
            voter.voted_to_whom = None
        elif self.STATE == "VOTE_EXECUTION":
            voter.voted_to_which = None
            if voter.voted_to_which == "guilty":
                self.elected.voted_innocent -= 1
            else:
                self.elected.voted_guilty -= 1

    def clear_vote(self):
        for p in self.alive_list:
            p.has_voted = False
            p.votes_gotten = 0
            p.voted_to_whom = None
            p.voted_guilty = 0
            p.voted_innocent = 0
            p.voted_to_which = None

    async def execute_the_elected(self, sio):
        executed_democratically = True # whether executed by guilty/innocent vote or not
        if self.STATE == "VOTE_EXECUTION": # executed by vote
            data = {
                "type": "vote_done",
                "guilty": self.elected.voted_guilty,
                "innocent": self.elected.voted_innocent,
            }
            await self.emit_event(sio, data, room=self.roomID)
            await asyncio.sleep(3)
        else: # executed by court or lynch
            executed_democratically = False
        self.STATE = "EXECUTION"
        data = {
            "type": "state",
            "state": self.STATE,
            "who": self.elected.nickname,
        }
        await self.emit_event(sio, data, room=self.roomID)
        await asyncio.sleep(3)
        if not self.in_court and not self.in_lynch:
            self.STATE = "LAST_WORD"
            data = {
                "type": "state",
                "state": self.STATE,
                "who": self.elected.nickname,
            }
            await self.emit_event(sio, data, room=self.roomID)
            await asyncio.sleep(5)
        await self.elected.die(attacker="VOTE", room=self)
        data = {
            "type": "executed",
            "who": self.elected.nickname,
        }
        await self.emit_event(sio, data, room=self.roomID)
        self.die_today.append(self.elected)
        self.alive_list.remove(self.elected)
        # 처형자
        for p in self.alive_list:
            if isinstance(p.role, roles.Executioner) and p.role.target is self.elected:
                p.win = True
        await asyncio.gather(*[self.emit_event(sio, {"type": "execution_success"}, room=p.sid)
                             for p in self.players.values()
                             if isinstance(p.role, roles.Executioner) and p.role.target is self.elected], return_exceptions=True)
        if isinstance(self.elected.role, roles.Jester):
            self.elected.win = True
            for voter in self.alive_list:
                if (
                    (voter.voted_to_which=="guilty" and executed_democratically)
                    or (voter.voted_to_whom is self.elected and not executed_democratically)
                ):
                    voter.voted_to_execution_of_jester = True

    async def announce_role_and_lw_of(self, dead, sio):
        if isinstance(dead, Player):
            data = {
                "type": "role_announced",
                "who": dead.nickname,
                "role": dead.role.name,
            }
            await self.emit_event(sio, data, room=self.roomID)
            await asyncio.sleep(5)
            data = {
                "type": "lw_announced",
                "dead": dead.nickname,
                "lw": dead.lw,
            }
            await self.emit_event(sio, data, room=self.roomID)
            await asyncio.sleep(5)
        else:
            for d in dead:
                data = {
                    "type": "role_announced",
                    "who": d.nickname,
                    "role": d.role.name,
                }
                await self.emit_event(sio, data, room=self.roomID)
                await asyncio.sleep(5)
                data = {
                    "type": "lw_announced",
                    "dead": d.nickname,
                    "lw": d.lw,
                }
                await self.emit_event(sio, data, room=self.roomID)
                await asyncio.sleep(5)
        await self.emit_player_list(sio)

    def killable(self, attacker, attacked):
        return attacker.role.offense_level > attacked.role.defense_level

    async def emit_sound(self, sio, sound, dead=True, number_of_murdered=1):
        data = {
            "type": "sound",
            "sound": sound,
            "dead": dead,
            "number_of_murdered": number_of_murdered,
        }
        await self.emit_event(sio, data, room=self.roomID)

    async def convert_role(self, sio, convertor, converted, role):
        if converted.night_chat:
            sio.leave_room(converted.sid, converted.night_chat)
            converted.night_chat = None
        data = {
            "type": "role_converted",
            "role": role.name,
            "convertor": convertor.role.name if convertor else None,
        }
        converted.role = role
        converted.role_record.append(role)
        await self.emit_event(sio, data, room=converted.sid)
        for night_chatting_role in (roles.Mafia, roles.Triad, roles.Cult, roles.Mason, roles.Spy):
            if isinstance(converted.role, night_chatting_role):
                sio.enter_room(converted.sid, self.night_chat[night_chatting_role])
                converted.night_chat = self.night_chat[night_chatting_role]

    async def trigger_evening_events(self, sio):
        for p in self.alive_list:
            if isinstance(p.role, roles.Mason) and not isinstance(p.role, roles.MasonLeader):
                for p2 in self.alive_list:
                    if isinstance(p.role, roles.MasonLeader):
                        break
                else: # 비조장이 없다. 한 명 비조장으로 승격
                    await self.convert_role(sio, convertor=p, converted=p, role=roles.MasonLeader())
        for p in self.alive_list:
            if isinstance(p.role, roles.Consigliere):
                for p2 in self.alive_list:
                    if isinstance(p2.role, roles.Godfather):
                        break
                else:
                    await self.convert_role(sio, convertor=p, converted=p, role=roles.Godfather())
        for p in self.alive_list:
            if isinstance(p.role, roles.Mafia):
                for p2 in self.alive_list:
                    if isinstance(p2.role, roles.MafiaKilling):
                        break
                else:
                    await self.convert_role(sio, convertor=p, converted=p, role=roles.Mafioso())
                    break
        for p in self.alive_list:
            if isinstance(p.role, roles.Administrator):
                for p2 in self.alive_list:
                    if isinstance(p2.role, roles.DragonHead):
                        break
                else:
                    await self.convert_role(sio, convertor=p, converted=p, role=roles.DragonHead())
                    break
        for p in self.alive_list:
            if isinstance(p.role, roles.Triad):
                for p2 in self.alive_list:
                    if isinstance(p2.role, roles.TriadKilling):
                        break
                else:
                    await self.convert_role(sio, convertor=p, converted=p, role=roles.Enforcer())
                    break

        if not self.die_today: # 사형이 있은 날에는 감금 불가
            for p in self.alive_list:
                if (
                    (
                        isinstance(p.role, roles.Jailor)
                        or isinstance(p.role, roles.Kidnapper)
                        or isinstance(p.role, roles.Interrogator)
                    )
                    and not p.jailed
                    and p.has_jailed_whom
                ):
                    p.has_jailed_whom.jailed = True
                    p.crimes["납치"] = True
            for p in self.alive_list:
                if not p.jailed:
                    if isinstance(p.role, roles.Jailor) and p.has_jailed_whom:
                        sio.enter_room(p.sid, p.has_jailed_whom.jailID)
                        data = {
                            "type": "has_jailed_someone",
                        }
                        await self.emit_event(sio, data, p.sid)
                        data = {
                            "type": "jailed",
                        }
                        await self.emit_event(sio, data, p.has_jailed_whom.sid)
                    elif isinstance(p.role, roles.Kidnapper) and p.has_jailed_whom:
                        data = {
                            "type": "has_jailed_someone",
                        }
                        await self.emit_event(sio, data, p.sid)
                        for maf in self.alive_list:
                            if isinstance(maf.role, roles.Mafia) and not maf.jailed:
                                sio.enter_room(maf.sid, p.has_jailed_whom.jailID)
                        data = {
                            "type": "jailed",
                        }
                        await self.emit_event(sio, data, p.has_jailed_whom.sid)
                    elif isinstance(p.role, roles.Interrogator) and p.has_jailed_whom:
                        data = {
                            "type": "has_jailed_someone",
                        }
                        await self.emit_event(sio, data, p.sid)
                        for trd in self.alive_list:
                            if isinstance(trd.role, roles.Triad) and not trd.jailed:
                                sio.enter_room(trd.sid, p.has_jailed_whom.jailID)
                        data = {
                            "type": "jailed",
                        }
                        await self.emit_event(sio, data, p.has_jailed_whom.sid)

    async def trigger_night_events(self, sio):
        # 감옥 채팅 나가기
        for p1 in self.alive_list:
            for p2 in self.alive_list:
                if p1 is not p2:
                    sio.leave_room(p1, p2.jailID)

        # 생존자 방탄 착용
        for p in self.alive_list:
            if isinstance(p.role, roles.Survivor) and p.wear_vest_today and p.role.ability_opportunity>0:
                p.role.ability_opportunity -= 1
                p.role.defense_level = 1
                data = {
                    "type": "wear_vest",
                    "wear_vest": p.wear_vest_today,
                }
                await self.emit_event(sio, data, room=p.sid)

        # 시민 방탄 착용
        for p in self.alive_list:
            if isinstance(p.role, roles.Citizen) and p.wear_vest_today and p.role.ability_opportunity>0:
                p.role.ability_opportunity -= 1
                p.role.defense_level = 1
                data = {
                    "type": "wear_vest",
                    "wear_vest": p.wear_vest_today,
                }
                await self.emit_event(sio, data, room=p.sid)

        # 마녀 능력 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Witch) and p.target1 and p.target2:
                p.target1.visited_by[self.day].add(p)
                if (isinstance(p.target1, roles.Veteran) and p.target1.alert_today) or (
                    isinstance(p.target1, roles.MassMurderer) and p.target1
                ):
                    continue
                else:
                    p.target1.target1 = p.target2
                    p.target1.controlled_by = p
                    data = {
                        "type": "Witch_control_success",
                        "target1": p.target1.nickname,
                        "target2": p.target2.nickname,
                    }
                    await self.emit_event(sio, data, room=p.sid)
                    data = {
                        "type": "controlled_by_Witch",
                    }
                    await self.emit_event(sio, data, room=p.target1.sid)

        # 기생 능력 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Escort) and p.target1:
                p.target1.visited_by[self.day].add(p)
                p.target1.target1 = None
                p.target1.recruit_target = None
                p.target1.burn_today = False
                p.target1.curse_today = False
                data = {"type": "blocked"}
                await self.emit_event(sio, data, room=p.target1.sid)
                p.crimes["호객행위"] = True
                if isinstance(p.target1.role, roles.Town):
                    p.crimes["치안을 어지럽힘"] = True

        # 매춘부 능력 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Consort) and p.target1:
                p.target1.visited_by[self.day].add(p)
                p.target1.target1 = None
                p.target1.recruit_target = None
                p.target1.burn_today = False
                p.target1.curse_today = False
                data = {"type": "blocked"}
                await self.emit_event(sio, data, room=p.target1.sid)
                p.crimes["호객행위"] = True
                if isinstance(p.target1.role, roles.Town):
                    p.crimes["치안을 어지럽힘"] = True

        # 간통범 능력 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Liaison) and p.target1:
                p.target1.visited_by[self.day].add(p)
                p.target1.target1 = None
                p.target1.recruit_target = None
                p.target1.burn_today = False
                p.target1.curse_today = False
                data = {"type": "blocked"}
                await self.emit_event(sio, data, room=p.target1.sid)
                p.crimes["호객행위"] = True
                if isinstance(p.target1.role, roles.Town):
                    p.crimes["치안을 어지럽힘"] = True

        # 잠입자 능력 적용
        for p in self.alive_list:
            if (
                isinstance(p.role, roles.Beguiler)
                and p.target1
                and p.role.ability_opportunity > 0
            ):
                p.target1.visited_by[self.day].add(p)
                for p2 in self.alive_list:
                    if p2.target1 is p:
                        p2.target1 = p.target1
                        p2.controlled_by = p
                p.crimes["무단침입"] = True
                p.role.ability_opportunity -= 1
                # TODO: 자살유도 범죄 추가

        # 사기꾼 능력 적용
        for p in self.alive_list:
            if (
                isinstance(p.role, roles.Deceiver)
                and p.target1
                and p.role.ability_opportunity > 0
            ):
                p.target1.visited_by[self.day].add(p)
                for p2 in self.alive_list:
                    if p2.target1 is p:
                        p2.target1 = p.target1
                        p2.controlled_by = p
                p.crimes["무단침입"] = True
                p.role.ability_opportunity -= 1
                # TODO: 자살유도 범죄 추가

        # 방문자 모두 확정되면 방문자 목록에 추가
        # TODO: 방문자 로직 수정

        # 조작자 조작
        for p in self.alive_list:
            if isinstance(p.role, roles.Framer) and p.target1:
                p.target1.framed = True
                not_did = []
                for crime, did in p.target1.crimes.items():
                    if not did:
                        not_did.append(crime)
                if not_did:
                    p.target1.crimes[random.choice(not_did)] = True
        # 위조꾼 조작
        for p in self.alive_list:
            if isinstance(p.role, roles.Forger) and p.target1:
                p.target1.framed = True
                not_did = []
                for crime, did in p.target1.crimes.items():
                    if not did:
                        not_did.append(crime)
                if not_did:
                    p.target1.crimes[random.choice(not_did)] = True

        # 방화범 기름칠 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Arsonist) and not p.burn_today and p.target1:
                p.target1.visited_by[self.day].add(p)
                p.target1.oiled = True
                data = {
                    "type": "oiling_success",
                    "target1": p.target1.nickname,
                }
                await self.emit_event(sio, data, room=p.sid)
                p.crimes["무단침입"] = True

        # 의사 능력 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Doctor) and p.target1:
                p.target1.visited_by[self.day].add(p)
                p.target1.healed_by.append(p)

        # 요술사 능력 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.WitchDoctor) and p.target1 and p.role.ability_opportunity>0:
                p.role.ability_opportunity -= 1
                p.target1.visited_by[self.day].add(p)
                p.target1.healed_by.append(p)

        # 경호원 능력 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Bodyguard) and p.target1:
                p.target1.visited_by[self.day].add(p)
                p.target1.bodyguarded_by.append(p)

        # 사망자 발생 시작
        # 경계 중인 퇴역군인에게 간 애들부터 죽는다.
        for p in self.alive_list:
            if isinstance(p.role, roles.Veteran) and p.alert_today:
                p.role.ability_opportunity-=1
                data = {
                    "type": "remaining_ability_opportunity",
                    "remaining_ability_opportunity": p.role.ability_opportunity,
                }
                await self.emit_event(sio, data, room=p.sid)
                p.crimes["재물 손괴"] = True
                for visitor in [visitor for visitor in self.alive_list if visitor.target1 is p]:
                    p.visited_by[self.day].add(visitor)
                    if isinstance(visitor.role, roles.Lookout):
                        continue
                    if isinstance(visitor.role, roles.Doctor) or isinstance(
                        visitor.role, roles.WitchDoctor
                    ):
                        p.healed_by.remove(visitor)
                    elif isinstance(visitor.role, roles.Bodyguard):
                        p.bodyguarded_by.remove(visitor)
                    data = {"type": "someone_visited_to_Veteran"}
                    await self.emit_event(sio, data, room=p.sid)
                    data = {
                        "type": "visited_Veteran",
                        "with_Bodyguard": len(visitor.bodyguarded_by) != 0,
                    }
                    await self.emit_event(sio, data, room=visitor.sid)
                    if self.killable(p, visitor):
                        if visitor.bodyguarded_by:
                            BG = visitor.bodyguarded_by.pop()  # BG stands for Bodyguard
                            await visitor.bodyguarded(room=self, attacker=p)
                            await self.emit_sound(sio, BG.role.name)
                            data = {
                                "type": "fighted_with_bodyguard",
                            }
                            await self.emit_event(sio, data, room=p.sid)
                            if BG.healed_by:
                                H = BG.healed_by.pop()
                                await BG.healed(room=self, attacker=p, healer=H)
                            else:
                                await BG.die(attacker=p, dead_while_guarding=True, room=self)
                                p.crimes["살인"] = True
                        elif visitor.healed_by:
                            H = visitor.healed_by.pop()
                            await self.emit_sound(sio, visitor.role.name)
                            await p.healed(room=self, attacker=p, healer=H)
                        else:
                            await self.emit_sound(sio, p.role.name)
                            await visitor.die(attacker=p, die_tonight=self.die_tonight, room=self)
                            p.crimes["살인"] = True
                    else:
                        await self.emit_sound(sio, p.role.name, dead=False)
                        await visitor.attacked(room=self, attacker=p)

        # 간수의 처형대상이 죽는다.
        for p in self.alive_list:
            if (
                isinstance(p.role, roles.Jailor)
                and p.kill_the_jailed_today
                and p.role.ability_opportunity > 0
            ):
                await self.emit_sound(sio, roles.Jailor.name)
                await p.has_jailed_whom.die(attacker=p, room=self)
                p.crimes["살인"] = True
                p.role.ability_opportunity -= 1
                data = {
                    "type": "remaining_ability_opportunity",
                    "remaining_ability_opportunity": p.role.ability_opportunity,
                }
                await self.emit_event(sio, data, room=p.sid)

        # 납치범의 처형대상이 죽는다.
        for p in self.alive_list:
            if (
                isinstance(p.role, roles.Kidnapper)
                and p.kill_the_jailed_today
                and p.role.ability_opportunity > 0
            ):
                await self.emit_sound(sio, roles.Jailor.name)
                await p.has_jailed_whom.die(attacker=p, room=self)
                p.crimes["살인"] = True
                p.role.ability_opportunity -= 1
                data = {
                    "type": "remaining_ability_opportunity",
                    "remaining_ability_opportunity": p.role.ability_opportunity,
                }
                await self.emit_event(sio, data, room=p.sid)

        # 심문자의 처형대상이 죽는다.
        for p in self.alive_list:
            if (
                isinstance(p.role, roles.Interrogator)
                and p.kill_the_jailed_today
                and p.role.ability_opportunity > 0
            ):
                await self.emit_sound(sio, roles.Jailor.name)
                await p.has_jailed_whom.die(attacker=p, room=self)
                p.crimes["살인"] = True
                p.role.ability_opportunity -= 1
                data = {
                    "type": "remaining_ability_opportunity",
                    "remaining_ability_opportunity": p.role.ability_opportunity,
                }
                await self.emit_event(sio, data, room=p.sid)
        # TODO: 조종자살 시 소리만 나는 것 수정
        # 자경대원의 대상이 죽는다.
        for p in self.alive_list:
            if isinstance(p.role, roles.Vigilante) and p.target1:
                p.role.ability_opportunity -= 1
                data = {
                    "type": "remaining_ability_opportunity",
                    "remaining_ability_opportunity": p.role.ability_opportunity,
                }
                await self.emit_event(sio, data, room=p.sid)
                victim = p.target1
                victim.visited_by[self.day].add(p)
                if isinstance(victim.role, roles.Veteran) and victim.alert_today:
                    continue
                if victim == p:
                    if self.killable(p, p):
                        await self.emit_sound(sio, "Suicide_by_control")
                        await p.suicide(room=self, reason=p.controlled_by.role.name)
                    else:
                        data = {"type": "almost_suicide"}
                        await self.emit_event(sio, data, room=p.sid)
                    continue
                p.crimes["무단침입"] = True
                if victim.bodyguarded_by:
                    BG = victim.bodyguarded_by.pop()  # BG stands for Bodyguard
                    await victim.bodyguarded(room=self, attacker=p)
                    await self.emit_sound(sio, BG.role.name)
                    if p.healed_by:
                        H = p.healed_by.pop()  # H stands for Healer
                        await p.healed(room=self, attacker=p, healer=H)
                    else:
                        await p.die(attacker=BG, room=self)
                        BG.crimes["살인"] = True
                    if BG.healed_by:
                        H = BG.healed_by.pop()
                        await BG.healed(room=self, attacker=p, healer=H, dead_while_guarding=True)
                    else:
                        await BG.die(attacker=p, dead_while_guarding=True, room=self)
                        p.crimes["살인"] = True
                elif self.killable(p, victim):
                    await self.emit_sound(sio, p.role.name)
                    if victim.healed_by:
                        H = victim.healed_by.pop()
                        await victim.healed(room=self, attacker=p, healer=H)
                    else:
                        await victim.die(attacker=p, room=self)
                        p.crimes["살인"] = True
                else:
                    await self.emit_sound(sio, p.role.name, dead=False)
                    await victim.attacked(room=self, attacker=p)

        # 마피아의 대상이 죽는다.
        if self.mafia_target or self.Godfather_target:
            for p in self.alive_list:
                if isinstance(p.role, roles.Godfather):
                    M = p # M stands for Mafia
                    break
            else:
                for p in self.alive_list:
                    if isinstance(p.role, roles.Mafioso):
                        M = p
                        break
            victim = self.Godfather_target or self.mafia_target
            victim.visited_by[self.day].add(M)
            if isinstance(victim.role, roles.Veteran) and victim.alert_today:
                pass
            else:
                if victim == M:
                    if self.killable(M, M):
                        await self.emit_sound(sio, "Suicide_by_control")
                        await M.suicide(room=self, reason=M.controlled_by.role.name)
                    else:
                        data = {"type": "almost_suicide"}
                        await self.emit_event(sio, data, room=M.sid)
                else:
                    M.crimes["무단침입"] = True
                    if victim.bodyguarded_by:
                        BG = victim.bodyguarded_by.pop()  # BG stands for Bodyguard
                        await victim.bodyguarded(room=self, attacker=M)
                        await self.emit_sound(sio, BG.role.name)
                        if M.healed_by:
                            H = M.healed_by.pop()  # H stands for Healer
                            await M.healed(room=self, attacker=M, healer=H)
                        else:
                            await M.die(attacker=BG, room=self)
                            BG.crimes["살인"] = True
                        if BG.healed_by:
                            H = BG.healed_by.pop()
                            await BG.healed(room=self, attacker=M, healer=H, dead_while_guarding=True)
                        else:
                            await BG.die(attacker=M, dead_while_guarding=True, room=self)
                            M.crimes["살인"] = True
                    elif self.killable(M, victim):
                        await self.emit_sound(sio, roles.Mafioso.name)
                        if victim.healed_by:
                            H = victim.healed_by.pop()
                            await victim.healed(room=self, attacker=M, healer=H)
                        else:
                            await victim.die(attacker=M, room=self)
                            M.crimes["살인"] = True
                    else:
                        await self.emit_sound(sio, roles.Mafioso.name, dead=False)
                        await victim.attacked(room=self, attacker=M)

        # 삼합회의 대상이 죽는다.
        if self.triad_target or self.DragonHead_target:
            for p in self.alive_list:
                if isinstance(p.role, roles.DragonHead):
                    T = p # T stands for triad
                    break
            else:
                for p in self.alive_list:
                    if isinstance(p.role, roles.Enforcer):
                        T = p
                        break
            victim = self.DragonHead_target or self.triad_target
            victim.visited_by[self.day].add(T)
            if isinstance(victim.role, roles.Veteran) and victim.alert_today:
                pass
            else:
                if victim == T:
                    if self.killable(T, T):
                        await self.emit_sound(sio, "Suicide_by_control")
                        await T.suicide(room=self, reason=T.controlled_by.role.name)
                    else:
                        data = {"type": "almost_suicide"}
                        await self.emit_event(sio, data, room=T.sid)
                else:
                    T.crimes["무단침입"] = True
                    if victim.bodyguarded_by:
                        BG = victim.bodyguarded_by.pop()  # BG stands for Bodyguard
                        await victim.bodyguarded(room=self, attacker=T)
                        await self.emit_sound(sio, BG.role.name)
                        if T.healed_by:
                            H = T.healed_by.pop()  # H stands for Healer
                            await T.healed(room=self, attacker=T, healer=H)
                        else:
                            await T.die(attacker=BG, room=self)
                            BG.crimes["살인"] = True
                        if BG.healed_by:
                            H = BG.healed_by.pop()
                            await BG.healed(room=self, attacker=T, healer=H, dead_while_guarding=True)
                        else:
                            await BG.die(attacker=T, dead_while_guarding=True, room=self)
                            T.crimes["살인"] = True
                    elif self.killable(T, victim):
                        await self.emit_sound(sio, roles.Mafioso.name)
                        if victim.healed_by:
                            H = victim.healed_by.pop()
                            await victim.healed(room=self, attacker=T, healer=H)
                        else:
                            await victim.die(attacker=T, room=self)
                            T.crimes["살인"] = True
                    else:
                        await self.emit_sound(sio, roles.Mafioso.name, dead=False)
                        await victim.attacked(room=self, attacker=T)

        # 연쇄살인마의 대상이 죽는다.
        for p in self.alive_list:
            if isinstance(p.role, roles.SerialKiller) and p.target1:
                victim = p.target1
                victim.visited_by[self.day].add(p)
                if isinstance(victim.role, roles.Veteran) and victim.alert_today:
                    continue
                if victim == p:
                    if self.killable(p, p):
                        await self.emit_sound(sio, "Suicide_by_control")
                        await p.suicide(room=self, reason=p.controlled_by.role.name)
                    else:
                        data = {"type": "almost_suicide"}
                        await self.emit_event(sio, data, room=p.sid)
                    continue
                p.crimes["무단침입"] = True
                if victim.bodyguarded_by:
                    BG = victim.bodyguarded_by.pop()  # BG stands for Bodyguard
                    await victim.bodyguarded(room=self, attacker=p)
                    await self.emit_sound(sio, BG.role.name)
                    if p.healed_by:
                        H = p.healed_by.pop()  # H stands for Healer
                        await p.healed(room=self, attacker=p, healer=H)
                    else:
                        await p.die(attacker=BG, room=self)
                        BG.crimes["살인"] = True
                    if BG.healed_by:
                        H = BG.healed_by.pop()
                        await BG.healed(room=self, attacker=p, healer=H, dead_while_guarding=True)
                    else:
                        await BG.die(attacker=p, dead_while_guarding=True, room=self)
                        p.crimes["살인"] = True
                elif self.killable(p, victim):
                    await self.emit_sound(sio, p.role.name)
                    if victim.healed_by:
                        H = victim.healed_by.pop()
                        await victim.healed(room=self, attacker=p, healer=H)
                    else:
                        await victim.die(attacker=p, room=self)
                        p.crimes["살인"] = True
                else:
                    await self.emit_sound(sio, p.role.name, dead=False)
                    await victim.attacked(room=self, attacker=p)

        # 방화범이 불을 피운다.
        for p in self.alive_list:
            if isinstance(p.role, roles.Arsonist) and p.burn_today:
                p.crimes["방화"] = True
                p.crimes["재물 손괴"] = True
                oiled = {v for v in self.alive_list if v.oiled}
                victims = oiled.copy()
                for o in oiled:
                    if o.target1:
                        victims.add(o.target1)
                await self.emit_sound(sio, p.role.name, number_of_murdered=len(victims))
                for victim in victims:
                    if self.killable(p, victim):
                        if victim.healed_by:
                            H = victim.healed_by.pop()
                            await victim.healed(room=self, attacker=p, healer=H)
                        else:
                            await victim.die(attacker=p, room=self)
                            p.crimes["살인"] = True
                    else:
                        await victim.attacked(room=self, attacker=p)

        # 비밀조합장의 살인 적용
        for p in self.alive_list:
            if (
                isinstance(p.role, roles.MasonLeader)
                and p.target1
                and isinstance(p.target1.role, roles.Cult)
            ):
                p.crimes["호객행위"] = True
                p.crimes["무단침입"] = True
                victim = p.target1
                victim.visited_by[self.day].add(p)
                data = {
                    "type": "visited_cult",
                }
                await self.emit_event(sio, data, room=p.sid)
                if victim.bodyguarded_by:
                    BG = victim.bodyguarded_by.pop()
                    await self.emit_sound(sio, BG.role.name)
                    await victim.bodyguarded(room=self, attacker=p)
                    if p.healed_by:
                        H = p.healed_by.pop()
                        await p.healed(room=self, attacker=BG, healer=H)
                    else:
                        await p.die(attacker=BG, room=self)
                        BG.crimes["살인"] = True
                    if BG.healed_by:
                        H = BG.healed_by.pop()
                        await BG.healed(room=self, attacker=p)
                    else:
                        await BG.die(attacker=p, dead_while_guarding=True, room=self)
                        p.crimes["살인"] = True
                elif not self.killable(p, victim):
                    await self.emit_sound(sio, p.role.name)
                    await victim.attacked(room=self, attacker=p)
                elif victim.healed_by:
                    H = victim.healed_by.pop()
                    await self.emit_sound(sio, p.role.name)
                    await victim.healed(room=self, attacker=p, healer=H)
                else:
                    await self.emit_sound(sio, p.role.name)
                    await victim.die(attacker=p, room=self)
                    p.crimes["살인"] = True

        # 대량학살자 살인 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.MassMurderer) and p.target1 and p.cannot_murder_until<self.day:
                p.crimes["무단침입"] = True
                p.target1.visited_by[self.day].add(p)
                victims = {
                    v
                    for v in self.alive_list
                    if (
                        v.target1 is p.target1
                        or (isinstance(v.role, roles.Bodyguard) and v.target1 is p)
                    )
                    and v is not p
                }  # 경호원이 대학 경호 시 사망하는 것 구현
                if p.target1.target1 is None:
                    victims.add(p.target1)
                await self.emit_sound(sio, p.role.name, number_of_murdered=len(victims))
                if len(victims) > 1:
                    p.crimes["재물손괴"] = True
                    p.cannot_murder_until = self.day + 1
                for v in victims:
                    if v.bodyguarded_by:
                        BG = v.bodyguarded_by.pop()
                        await v.bodyguarded(room=self, attacker=p)
                        if p.healed_by:
                            H = p.healed_by.pop()
                            await p.healed(room=self, attacker=BG, healer=H)
                        else:
                            await p.die(attacker=BG, room=self)
                            BG.crimes["살인"] = True
                        if BG.healed_by:
                            H = BG.healed_by.pop()
                            await BG.healed(room=self, attacker=p, healer=H)
                        else:
                            await BG.die(attacker=p, room=self)
                            p.crimes["살인"] = True
                    elif not self.killable(p, v):
                        await v.attacked(room=self, attacker=p)
                    elif v.healed_by:
                        H = v.healed_by.pop()
                        await v.healed(room=self, attacker=p, healer=H)
                    else:
                        await v.die(attacker=p, room=self)
                        p.crimes["살인"] = True

        # 어릿광대 자살 적용
        candidates = [p for p in self.alive_list if p.voted_to_execution_of_jester]
        if candidates:
            victim = random.choice(candidates)
            await self.emit_sound(sio, "자살")
            if victim.healed_by:
                H = victim.healed_by.pop()
                class Dummy:
                    pass
                d = Dummy()
                d.role = Dummy()
                d.role.name = roles.Jester.name
                await victim.healed(room=self, attacker=d, healer=H)
            else:
                await victim.suicide(room=self, reason=roles.Jester.name)

        # TODO: 심장마비 자살
        # TODO: 변장자
        # TODO: 밀고자

        # 고의 자살 적용

        # 마녀 저주 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Witch) and p.curse_target and p.role.ability_opportunity>0:
                victim = p.curse_target
                # if victim.healed_by: # 마녀 저주는 치료 안 됨
                #     H = victim.healed_by.pop()
                #     await victim.healed(room=self, attacker=p, healer=H)
                # else:
                await victim.die(attacker=p, room=self)

        # 사망자들 제거
        for dead in self.die_tonight:
            self.alive_list.remove(dead)

        # 살인직들의 살인이 반영된 방문자 목록 갱신
        for p in self.alive_list:
            if p.target1:
                p.target1.visited_by[self.day].add(p)
        # TODO: 변장자, 밀고자 (사망자들 제거된 이후에 능력 발동됨)

        for p in self.alive_list:
            if isinstance(p.role, roles.Janitor) and p.target1 and not p.target1.alive and p.role.ability_opportunity>0:
                p.role.ability_opportunity -= 1
                p.target1.sanitized = True
                data = {
                    "type": "sanitized_lw",
                    "lw": p.target1.lw,
                }
                await self.emit_event(sio, data, room=p.sid)

        for p in self.alive_list:
            if isinstance(p.role, roles.IncenseMaster) and p.taregt1 and not p.target1.alive and p.role.ability_opportunity>0:
                p.role.ability_opportunity -= 1
                p.target1.sanitized = True
                data = {
                    "type": "sanitized_lw",
                    "lw": p.target1.lw,
                }
                await self.emit_event(sio, data, room=p.sid)

        # 고의 자살 적용
        for p in self.alive_list:
            if p.suicide_today:
                await self.emit_sound(sio, "자살")
                if p.healed_by:
                    H = p.healed_by.pop()
                    class Dummy:  # dummy class
                        pass
                    dummy = Dummy()
                    dummy.role = Dummy()
                    dummy.role.name = "자살"
                    await p.healed(room=self, attacker=dummy, healer=H)
                else:
                    await p.suicide(room=self, reason="고의")
                    self.die_tonight.add(p)
                    self.alive_list.remove(p)
        # 조사직들 능력 발동
        # 검시관
        for p in self.alive_list:
            if isinstance(p.role, roles.Coroner) and p.target1 and not p.target1.alive:
                data = {
                    "type": "check_result",
                    "role": p.role.name,
                    "result": {"lw": p.target1.lw,
                               "role": p.target1.role.name,
                               "visitors": [[visitor.role.name for visitor in visitors] for visitors in p.target1.visited_by[1:]],}
                }
                await self.emit_event(sio, data, room=p.sid)

        # 형사
        for p in self.alive_list:
            if isinstance(p.role, roles.Detective) and p.target1:
                p.crimes["무단침입"] = True
                for visited in self.alive_list:
                    if p.target1 in visited.visited_by[self.day]:
                        # 그냥 p.target1.target1을 주지 않고 이렇게 복잡하게 하는 것은
                        # p.target1이 자신의 target1만 설정해놓고 실제로 능력을 쓰지는 못하고 이날 밤에 죽었을 경우에(퇴군에게 죽었을 경우를 제외)
                        # None이 아닌 p.target1.target1을 주게 되면 형사 입장에서는 자기 목표가 능력을 쓰고 죽은 걸로 착각하게 되기 떄문이다.
                        # 예시: 탐정이 시장을 방문. 대부가 탐정을 방문. 형사가 탐정을 방문.
                        # 이때 그냥 p.target1.target1을 주게 되면 형사에게는 탐정이 시장을 방문한 것으로 보이게 됨. 실제로는 방문하지 못했음에도 불구.
                        # 따라서 각 플레이어들의 visited_by에 p.target1이 들어가 있는지를 확인하여 실제로 방문했을 때만 결과를 전송해야 한다.
                        result = visited.nickname
                        break
                else:
                    result = None
                if p.target1.framed:
                    framed_to_visit = []
                    for murderring_role in (roles.Mafia, roles.Triad, roles.Arsonist,
                                            roles.MassMurderer, roles.SerialKiller,
                                            roles.Witch):
                        for dead in self.die_tonight:
                            if murderring_role.team in dead.murdered_by:
                                framed_to_visit.append(dead.nickname)
                    result = random.choice(framed_to_visit)
                data = {
                    "type": "check_result",
                    "role": p.role.name,
                    "result": result,
                }
                await self.emit_event(sio, data, room=p.sid)

        # 감시자
        for p in self.alive_list:
            if isinstance(p.role, roles.Lookout) and p.target1:
                p.crimes["무단침입"] = True
                result = [visitor.nickname for visitor in p.target1.visited_by[self.day]]
                if p.target1.murdered_by:
                    for can_be_framed in self.alive_list:
                        if can_be_framed.framed:
                            result.append(can_be_framed.nickname)
                            break
                random.shuffle(result)
                result = list(set(result))
                result = [visitor for visitor in result if not visitor.role.detection_immune]
                data = {
                    "type": "check_result",
                    "role": p.role.name,
                    "result": result,
                }
                await self.emit_event(sio, data, room=p.sid)

        # 보안관
        for p in self.alive_list:
            if isinstance(p.role, roles.Sheriff) and p.target1:
                data = {
                    "type": "check_result",
                    "role": p.role.name,
                    "result": None,
                }
                for evil in (roles.Mafia, roles.Triad, roles.Cult):
                    if isinstance(p.target1.role, evil):
                        data["result"] = evil.team
                        break
                else:
                    for killing in (roles.SerialKiller, roles.MassMurderer, roles.Arsonist):
                        if isinstance(p.target1.role, killing):
                            data["result"] = killing.name
                            break
                if p.framed:
                    result = []
                    for evil in (roles.Mafia, roles.Triad, roles.Cult):
                        if isinstance(p.target1.role, evil):
                            result.append(evil.team)
                    for killing in (roles.SerialKiller, roles.MassMurderer, roles.Arsonist):
                        if isinstance(p.target1.role, killing):
                            result.append(killing.name)
                    data["result"] = random.choice(result)
                await self.emit_event(sio, data, room=p.sid)

        # 조언자
        for p in self.alive_list:
            if isinstance(p.role, roles.Consigliere) and p.target1:
                p.crimes["무단침입"] = True
                data = {
                    "type": "check_result",
                    "role": p.role.name,
                    "result": p.target1.role.name,
                }
                await self.emit_event(sio, data, room=p.sid)

        # 백지선
        for p in self.alive_list:
            if isinstance(p.role, roles.Administrator) and p.target1:
                p.crimes["무단침입"] = True
                data = {
                    "type": "check_result",
                    "role": p.role.name,
                    "result": p.target1.role.name,
                }
                await self.emit_event(sio, data, room=p.sid)

        # 요원
        for p in self.alive_list:
            if isinstance(p.role, roles.Agent) and p.target1:
                p.crimes["무단침입"] = True
                for visited in self.alive_list:
                    if p.target1 in visited.visited_by[self.day]:
                        # 그냥 p.target1.target1을 주지 않고 이렇게 복잡하게 하는 것은
                        # p.target1이 자신의 target1만 설정해놓고 실제로 능력을 쓰지는 못하고 이날 밤에 죽었을 경우에(퇴군에게 죽었을 경우를 제외)
                        # None이 아닌 p.target1.target1을 주게 되면 형사 입장에서는 자기 목표가 능력을 쓰고 죽은 걸로 착각하게 되기 떄문이다.
                        # 예시: 탐정이 시장을 방문. 대부가 탐정을 방문. 형사가 탐정을 방문.
                        # 이때 그냥 p.target1.target1을 주게 되면 형사에게는 탐정이 시장을 방문한 것으로 보이게 됨. 실제로는 방문하지 못했음에도 불구.
                        # 따라서 각 플레이어들의 visited_by에 p.target1이 들어가 있는지를 확인하여 실제로 방문했을 때만 결과를 전송해야 한다.
                        visiting = visited.nickname
                        break
                else:
                    visiting = None
                data = {
                    "type": "check_result",
                    "role": p.role.name,
                    "result": {
                        "visiting": visiting,
                        "visited_by": [p.nickname for p in p.target1.visited_by[self.day]],
                    }
                }
                await self.emit_event(sio, data, room=p.sid)

        # 선봉
        for p in self.alive_list:
            if isinstance(p.role, roles.Vanguard) and p.target1:
                p.crimes["무단침입"] = True
                for visited in self.alive_list:
                    if p.target1 in visited.visited_by[self.day]:
                        # 그냥 p.target1.target1을 주지 않고 이렇게 복잡하게 하는 것은
                        # p.target1이 자신의 target1만 설정해놓고 실제로 능력을 쓰지는 못하고 이날 밤에 죽었을 경우에(퇴군에게 죽었을 경우를 제외)
                        # None이 아닌 p.target1.target1을 주게 되면 형사 입장에서는 자기 목표가 능력을 쓰고 죽은 걸로 착각하게 되기 떄문이다.
                        # 예시: 탐정이 시장을 방문. 대부가 탐정을 방문. 형사가 탐정을 방문.
                        # 이때 그냥 p.target1.target1을 주게 되면 형사에게는 탐정이 시장을 방문한 것으로 보이게 됨. 실제로는 방문하지 못했음에도 불구.
                        # 따라서 각 플레이어들의 visited_by에 p.target1이 들어가 있는지를 확인하여 실제로 방문했을 때만 결과를 전송해야 한다.
                        visiting = visited.nickname
                        break
                else:
                    visiting = None
                data = {
                    "type": "check_result",
                    "role": p.role.name,
                    "result": {
                        "visiting": visiting,
                        "visited_by": [p.nickname for p in p.target1.visited_by[self.day]],
                    }
                }
                await self.emit_event(sio, data, room=p.sid)
        # TODO: 변장자 이동
        # 정보원
        for p in self.alive_list:
            if isinstance(p.role, roles.Spy):
                for p2 in self.alive_list:
                    if (isinstance(p2.role, roles.Mafia) or isinstance(p2.role, roles.Triad)) and p2.target1:
                        data = {
                            "type": "spy_result",
                            "team": p2.role.team,
                            "result": p2.target1.nickname,
                        }
                        await self.emit_event(sio, data, room=p.sid)
        # TODO: 어릿광대 괴롭히기

        # 탐정 (코드 내 위치에 따라서 발견할 수 있는 범죄가 달라지는 데 유의할 것.)
        #     (이 위치에서는 조사직들과 살인직들만 발견 가능하고 회계, 비조 등은 당일 밤에는 발견 못 함.)
        for p in self.alive_list:
            if isinstance(p.role, roles.Investigator) and p.target1:
                p.crimes["무단침입"] = True
                data = {
                    "type": "check_result",
                    "role": p.role.name,
                    "result": p.target1.crimes,
                }
                await self.emit_event(sio, data, room=p.sid)

        # 회계
        for p in self.alive_list:
            if isinstance(p.role, roles.Auditor) and p.target1 and p.role.ability_opportunity>0:
                if p.target1.role.defense_level > 0 or isinstance(
                    p.target1.role, roles.Cult
                ):
                    data = {
                        "type": "unable_to_audit",
                    }
                    await self.emit_event(sio, data, room=p.sid)
                else:
                    p.role.ability_opportunity-=1
                    if p.target1 is p:
                        await self.convert_role(
                            sio, convertor=p, converted=p, role=roles.Stump()
                        )
                    elif isinstance(p.target1.role, roles.Mafia):
                        await self.convert_role(
                            sio, convertor=p, converted=p.target1, role=roles.Mafioso()
                        )
                    elif isinstance(p.target1.role, roles.Triad):
                        await self.convert_role(
                            sio, convertor=p, converted=p.target1, role=roles.Triad()
                        )
                    elif isinstance(p.target1.role, roles.Town):
                        await self.convert_role(
                            sio, convertor=p, converted=p.target1, role=roles.Citizen()
                        )
                    else:
                        await self.convert_role(
                            sio, convertor=p, converted=p.target1, role=roles.Scumbag()
                        )
                    data = {
                        "type": "audit_success",
                        "role": p.target1.role.name,
                        "who": p.target1.nickname,
                    }
                    await self.emit_event(sio, data, room=p.sid)
                    p.crimes["부패"] = True

        # 비밀조합 영입
        for p in self.alive_list:
            if isinstance(p.role, roles.MasonLeader) and p.target1:
                p.crimes["호객행위"] = True
                if isinstance(p.target1.role, roles.Citizen):
                    await self.convert_role(
                        sio, convertor=p, converted=p.target1, role=roles.Mason()
                    )
                    data = {
                        "type": "recruit_success",
                        "role": p.target1.role.name,
                        "who": p.target1.nickname,
                    }
                    await self.emit_event(sio, data, room=p.sid)
                elif not isinstance(p.target1.role, roles.Cult):
                    data = {"type": "recruit_failed"}
                    await self.emit_event(sio, data, room=p.sid)

        # 이교도 개종
        for p in self.alive_list:
            # TODO: 개종 최대 수 제한 넣기
            if isinstance(p.role, roles.Cultist) and p.target1:
                p.crimes["호객행위"] = True
                if isinstance(p.target1.role, roles.Mason):
                    data = {
                        "type": "recruited_by_cult",
                        "who": p.nickname,
                    }
                    await self.emit_event(sio, data, room=p.target1.sid)
                    data = {"type": "tried_to_recruit_Mason", "who": p.target1.nickname}
                    await self.emit_event(sio, data, room=self.night_chat[roles.Cult])
                elif p.target1.role.defense_level > 0:
                    data = {
                        "type": "recruit_failed",
                    }
                    await self.emit_event(sio, data, room=self.night_chat[roles.Cult])
                elif isinstance(p.target1.role, roles.Mafia) or isinstance(
                    p.target1.role, roles.Triad
                ):
                    data = {
                        "type": "recruited_by_cult",
                        "who": p.nickname,
                    }
                    await self.emit_event(sio, data, room=p.target1.sid)
                    data = {
                        "type": "recruit_failed",
                    }
                    await self.emit_event(sio, data, room=self.night_chat[roles.Cult])
                else:
                    if (
                        (isinstance(p.target1.role, roles.Witch)
                        or isinstance(p.target1.role, roles.Doctor))
                        and roles.WitchDoctor.name not in {p.role.name for p in self.players}
                    ):
                        await self.convert_role(
                            sio,
                            convertor=p,
                            converted=p.target1,
                            role=roles.WitchDoctor(),
                        )
                    else:
                        await self.convert_role(
                            sio, convertor=p, converted=p.target1, role=roles.Cultist()
                        )
                    data = {
                        "type": "recruit_success",
                        "role": p.target1.role.name,
                        "who": p.target1.nickname,
                    }
                    await self.emit_event(sio, data, room=self.night_chat[roles.Cult])
                    p.crimes["음모"] = True

        # 마피아 영입
        for p in self.alive_list:
            if isinstance(p.role, roles.Godfather) and p.recruit_target:
                if isinstance(p.recruit_target.role, roles.Citizen):
                    await self.convert_role(
                        sio,
                        convertor=p,
                        converted=p.recruit_target,
                        role=roles.Mafioso(),
                    )
                    data = {
                        "type": "recruit_success",
                        "role": p.recruit_target.role.name,
                        "who": p.recruit_target.nickname,
                    }
                    await self.emit_event(sio, data, room=self.night_chat[roles.Mafia])
                elif isinstance(p.recruit_target.role, roles.Escort) and self.setup!="8331":
                    await self.convert_role(
                        sio,
                        convertor=p,
                        converted=p.recruit_target,
                        role=roles.Consort(),
                    )
                    data = {
                        "type": "recruit_success",
                        "role": p.recruit_target.role.name,
                        "who": p.recruit_target.nickname,
                    }
                    await self.emit_event(sio, data, room=self.night_chat[roles.Mafia])
                else:
                    data = {"type": "recruit_failed"}
                    await self.emit_event(sio, data, room=self.night_chat[roles.Mafia])

        # 삼합회 영입
        for p in self.alive_list:
            if isinstance(p.role, roles.DragonHead) and p.recruit_target:
                if isinstance(p.recruit_target.role, roles.Citizen):
                    await self.convert_role(
                        sio,
                        convertor=p,
                        converted=p.recruit_target,
                        role=roles.Enforcer(),
                    )
                    data = {
                        "type": "recruit_success",
                        "role": p.recruit_target.role.name,
                        "who": p.recruit_target.nickname,
                    }
                    await self.emit_event(sio, data, room=self.night_chat[roles.Triad])
                elif isinstance(p.recruit_target.role, roles.Escort) and self.setup!="8331":
                    await self.convert_role(
                        sio,
                        convertor=p,
                        converted=p.recruit_target,
                        role=roles.Liaison(),
                    )
                    data = {
                        "type": "recruit_success",
                        "role": p.recruit_target.role.name,
                        "who": p.recruit_target.nickname,
                    }
                    await self.emit_event(sio, data, room=self.night_chat[roles.Triad])
                else:
                    data = {"type": "recruit_failed"}
                    await self.emit_event(sio, data, room=self.night_chat[roles.Triad])

        # 기억상실자 기억
        for p in self.alive_list:
            if isinstance(p.role, roles.Amnesiac) and p.remember_today:
                await self.convert_role(sio, p, p, p.remember_target.role.__class__())
                if isinstance(p.role, roles.Spy):
                    p.crimes["무단침입"] = True

        # 협박자 협박
        for p in self.alive_list:
            if isinstance(p.role, roles.Blackmailer) and p.target1:
                p.target1.blackmailed = True
                data = {
                    "type": "blackmailed",
                }
                await self.emit_event(sio, data, room=p.target1.sid)

        # 침묵자 협박
        for p in self.alive_list:
            if isinstance(p.role, roles.Silencer) and p.target1:
                p.target1.blackmailed = True
                data = {
                    "type": "blackmailed",
                }
                await self.emit_event(sio, data, room=p.target1.sid)

    async def clear_up(self):
        self.clear_vote()
        self.in_lynch = False
        self.in_court = False
        self.Godfather_target = None
        self.mafia_target = None
        self.DragonHead_target = None
        self.triad_target = None
        for p in self.players.values():
            if not isinstance(p.role, roles.Mayor) and not isinstance(p.role, roles.Stump):
                p.votes = 1
            if (isinstance(p.role, roles.Survivor) or isinstance(p.role, roles.Citizen)) and p.wear_vest_today:
                p.role.defense_level = 0
            p.has_voted = False
            p.voted_to_whom = None
            p.voted_to_execution_of_jester = False
            p.has_voted_in_execution_vote = False
            p.voted_to_which = None
            p.votes_gotten = 0
            p.voted_guilty = 0
            p.voted_innocent = 0
            p.activated_lynch_today = False
            p.visited_by.append(set())
            p.wear_vest_today = False
            p.alert_today = False
            p.burn_today = False
            p.curse_today = False
            p.suicide_today = False
            p.protected_from_cult = False
            p.protected_from_auditor = False
            p.kill_the_jailed_today = False
            p.jailed = False
            p.jailed_by = []
            p.has_jailed_whom = None
            p.bodyguarded_by = []
            p.healed_by = []
            p.target1 = None
            p.target2 = None
            p.curse_target = None
            p.recruit_target = None

    def game_over(self):
        remaining = self.alive_list
        if len(remaining) == 0 or len(remaining) == 1 or len(remaining) == 2:
            return True
        townRemains = False
        mafiaRemains = False
        triadRemains = False
        neutralKillingRemains = False
        neutralEvilThatIsNotNeutralKillingRemains = False
        for p in remaining:
            if isinstance(p.role, roles.Town):
                townRemains = True
            elif isinstance(p.role, roles.Mafia):
                mafiaRemains = True
            elif isinstance(p.role, roles.Triad):
                triadRemains = True
            elif isinstance(p.role, roles.NeutralKilling):
                neutralKillingRemains = True
            elif isinstance(p.role, roles.NeutralEvil) and not isinstance(
                p.role, roles.NeutralKilling
            ):
                neutralEvilThatIsNotNeutralKillingRemains = True
        if townRemains:
            return (
                not mafiaRemains
                and not triadRemains
                and not neutralKillingRemains
                and not neutralEvilThatIsNotNeutralKillingRemains
            )
        if mafiaRemains:
            return not triadRemains and not neutralKillingRemains
        if triadRemains:
            return not neutralKillingRemains
        if neutralKillingRemains:  # 중살들밖에 안남은 경우
            arsonistRemains = False
            massMurdererRemains = False
            serialKillerRemains = False
            for p in remaining:
                if isinstance(p.role, roles.Arsonist):
                    arsonistRemains = True
                elif isinstance(p.role, roles.MassMurderer):
                    massMurdererRemains = True
                elif isinstance(p.role, roles.SerialKiller):
                    serialKillerRemains = True
            return not (arsonistRemains and massMurdererRemains and serialKillerRemains)
        return True  # 중선들만 남은 경우

    def win(self, winning_role, include_dead):
        if include_dead:
            for p in self.players.values():
                if isinstance(p.role, winning_role):
                    p.win = True
        else:
            for p in self.alive_list:
                if isinstance(p.role, winning_role):
                    p.win = True

    async def init_game(self, sio):
        # init game
        logger.info(f"Game initiated in room #{self.roomID}")
        self.inGame = True
        self.readied = set()
        self.election = asyncio.Event()
        self.elected = None
        self.day = 0
        self.die_today = set()
        self.die_tonight = set()
        self.message_record = [] # 초기화
        self.in_lynch = False
        self.in_court = False
        self.Godfather_target = None
        self.DragonHead_target = None
        self.mafia_target = None
        self.triad_target = None
        self.cult_target = None
        try:
            validate_setup(self.setup)
        except Exception as e:
            data = {
                "type": "unable_to_start",
                "reason": "invalid_setup",
            }
            await self.emit_event(sio, data, room=self.roomID)
            return
        if self.setup=="test":
            self.STATE = "MORNING"  # game's first state when game starts
            self.DISCUSSION_TIME = 10
            self.VOTE_TIME = 30
            self.DEFENSE_TIME = 10
            self.VOTE_EXECUTION_TIME = 10
            self.EVENING_TIME = 10
        if self.setup == "8331":
            self.STATE = "MORNING"  # game's first state when game starts
            self.DISCUSSION_TIME = 30
            self.VOTE_TIME = 120
            self.DEFENSE_TIME = 15
            self.VOTE_EXECUTION_TIME = 20
            self.EVENING_TIME = 36
            mafia_random = role_pool[roles.MafiaKilling]+role_pool[roles.MafiaDeception]+role_pool[roles.MafiaSupport]
            town_random = role_pool[roles.TownKilling]+role_pool[roles.TownPower]+role_pool[roles.TownProtective]+role_pool[roles.TownInvestigative]
            all_random = town_random+role_pool[roles.Neutral]
            roles_to_distribute = []
            roles_to_distribute.append(random.choice(role_pool[roles.Neutral]))
            while to_insert:=random.choice(role_pool[roles.Neutral]):
                if roles.Judge in roles_to_distribute and to_insert is roles.Judge:
                    continue
                else:
                    roles_to_distribute.append(to_insert)
                    break
            if roles.Auditor in roles_to_distribute or roles.Cultist in roles_to_distribute:
                role_pool[roles.TownGovernment].append(roles.MasonLeader)
            roles_to_distribute.append(random.choice(mafia_random))
            roles_to_distribute.append(random.choice(mafia_random))
            roles_to_distribute.append(roles.Godfather)
            roles_to_distribute.append(random.choice(role_pool[roles.TownGovernment]))
            roles_to_distribute.append(random.choice(role_pool[roles.TownProtective]))
            roles_to_distribute.append(random.choice(role_pool[roles.TownProtective]))
            roles_to_distribute.append(random.choice(role_pool[roles.TownKilling]))
            roles_to_distribute.append(random.choice(role_pool[roles.TownPower]))
            roles_to_distribute.append(random.choice(role_pool[roles.TownInvestigative]))
            roles_to_distribute.append(random.choice(role_pool[roles.TownInvestigative]))
            roles_to_distribute.append(random.choice(town_random))
            roles_to_distribute.append(random.choice(role_pool[roles.NeutralKilling]))
            while to_insert:=random.choice(all_random):
                if roles.Judge in roles_to_distribute and to_insert is roles.Judge:
                    continue
                else:
                    roles_to_distribute.append(to_insert)
                    break
        elif self.setup == "power_conflict":
            pass
        elif self.setup == "test":
            roles_to_distribute = [
                roles.Survivor,
                roles.Citizen,
                roles.Mafioso,
            ]
        random.shuffle(roles_to_distribute)
        self.players = {
            (await sio.get_session(sid))["nickname"]: Player(
                sid=sid,
                roomID=self.roomID,
                nickname=(await sio.get_session(sid))["nickname"],
                role=(roles_to_distribute.pop())(),
                sio=sio,
            )
            for sid in self.members
        }
        await self.emit_player_list(sio)
        self.hell = str(self.roomID) + "_hell"
        self.night_chat = dict()
        self.night_chat[roles.Mafia] = str(self.roomID) + "_Mafia"
        self.night_chat[roles.Triad] = str(self.roomID) + "_Triad"
        self.night_chat[roles.Cult] = str(self.roomID) + "_Cult"
        self.night_chat[roles.Spy] = str(self.roomID) + "_Spy"
        self.night_chat[roles.Mason] = str(self.roomID) + "_Mason"

        for p in self.players.values():
            sio.enter_room(p.sid, p.jailID)
            for night_chatting_role in (roles.Mafia, roles.Triad, roles.Cult, roles.Spy, roles.Mason):
                if isinstance(p.role, night_chatting_role):
                    sio.enter_room(p.sid, self.night_chat[night_chatting_role])
                    p.night_chat = self.night_chat[night_chatting_role]

        self.alive_list = list(self.players.values())
        await asyncio.gather(*[self.emit_event(sio, {"type": "role", "role": p.role.name}, room=p.sid) for p in self.players.values()], return_exceptions=True)
        for p in self.players.values():
            if isinstance(p.role, roles.Spy):
                p.crimes["무단침입"] = True
        for p in self.players.values():
            if isinstance(p.role, roles.Executioner):
                player_list = list(self.players.values())
                player_list.remove(p)
                p.role.set_target(player_list)
        await asyncio.gather(*[self.emit_event(sio,
                             {"type": "executioner_target", "target": p.role.target.nickname},
                             room=p.sid)
                             for p in self.players.values()
                             if isinstance(p.role, roles.Executioner)], return_exceptions=True)
        data = {
            "type": "setup",
            "setup": self.setup,
        }
        await self.emit_event(sio, data, room=self.roomID)
        for i in range(10, 0, -1):
            data = {
                "type": "will_start",
                "in": i,
            }
            await self.emit_event(sio, data, room=self.roomID)
            await asyncio.sleep(1)

    async def run_game(self, sio):
        logger.info(f"Game starts in room #{self.roomID}")
        while True:
            self.day += 1
            # MORNING
            self.STATE = "MORNING"
            data = {
                "type": "state",
                "state": self.STATE,
            }
            await self.emit_event(sio, data, room=self.roomID)
            for dead in self.die_tonight:
                data = {
                    "type": "dead_announced",
                    "dead": dead.nickname,
                }
                await self.emit_event(sio, data, room=self.roomID)
                await asyncio.sleep(5)
                if dead.sanitized:
                    data = {
                        "type": "the_dead_is_sanitized",
                        "who": dead.nickname,
                    }
                    await self.emit_event(sio, data, room=self.roomID)
                    await asyncio.sleep(5)
                else:
                    await self.announce_role_and_lw_of(dead, sio)
                await self.emit_player_list(sio)
            await self.emit_player_list(sio)
            if self.game_over():
                return
            self.die_tonight = set() # 사망자 목록 초기화
            # DISCUSSION
            self.STATE = "DISCUSSION"
            data = {
                "type": "state",
                "state": self.STATE,
            }
            await self.emit_event(sio, data, room=self.roomID)
            await asyncio.sleep(self.DISCUSSION_TIME)
            # VOTE
            if self.day == 1: # 첫날에는 토론만 하고 바로 저녁이 되도록.
                pass
            else:
                self.STATE = "VOTE"
                data = {
                    "type": "state",
                    "state": self.STATE,
                }
                await self.emit_event(sio, data, room=self.roomID)
                self.VOTE_STARTED_AT = datetime.now()
                self.VOTE_TIME_REMAINING = self.VOTE_TIME
                self.die_today = [] # 선거사망자 목록 초기화
                while self.VOTE_TIME_REMAINING >= 0:
                    try:
                        await asyncio.wait_for(
                            self.election.wait(), timeout=self.VOTE_TIME_REMAINING
                        )
                    except asyncio.TimeoutError:  # nobody has been elected today
                        break
                    else:  # someone has been elected
                        self.VOTE_TIME_REMAINING -= (datetime.now()-self.VOTE_STARTED_AT).total_seconds()
                        if self.in_court and self.in_lynch:
                            await self.execute_the_elected(sio)
                            await asyncio.sleep(3)
                            self.VOTE_STARTED_AT = datetime.now()
                            self.clear_vote()
                            if len(self.die_today)==3:
                                break
                            self.STATE = "VOTE"
                            data = {
                                "type": "state",
                            }
                            await self.emit_event(sio, data, room=self.roomID)
                        elif self.in_court:
                            await self.execute_the_elected(sio)
                            await asyncio.sleep(3)
                            break
                        elif self.in_lynch:
                            await self.execute_the_elected(sio)
                            await asyncio.sleep(3)
                            self.clear_vote()
                            if len(self.die_today)==3:
                                break
                            self.VOTE_STARTED_AT = datetime.now()
                            self.STATE = "VOTE"
                            data = {
                                "type": "state",
                                "state": self.STATE,
                            }
                            await self.emit_event(sio, data, room=self.roomID)
                        else:
                            self.clear_vote()
                            self.STATE = "DEFENSE"
                            data = {
                                "type": "state",
                                "state": self.STATE,
                                "who": self.elected.nickname,
                            }
                            await self.emit_event(sio, data, room=self.roomID)
                            await asyncio.sleep(self.DEFENSE_TIME)
                            self.STATE = "VOTE_EXECUTION"
                            data = {
                                "type": "state",
                                "state": self.STATE,
                                "who": self.elected.nickname,
                            }
                            await self.emit_event(sio, data, room=self.roomID)
                            await asyncio.sleep(self.VOTE_EXECUTION_TIME)
                            if self.elected.voted_guilty > self.elected.voted_innocent:
                                await self.execute_the_elected(sio)
                                await asyncio.sleep(3)
                                break
                            else:
                                self.clear_vote()
                                self.VOTE_STARTED_AT = datetime.now()
                                self.STATE = "VOTE"
                                data = {
                                    "type": "state",
                                    "state": self.STATE,
                                }
                                await self.emit_event(sio, data, room=self.roomID)
                    finally:
                        self.clear_vote()
                        self.election.clear()
                        self.elected = None
                await self.announce_role_and_lw_of(self.die_today, sio)

                if self.game_over():
                    return
            # EVENING
            self.STATE = "EVENING"
            data = {
                "type": "state",
                "state": self.STATE,
            }
            await self.emit_event(sio, data, room=self.roomID)
            await self.trigger_evening_events(sio)
            await self.emit_player_list(sio)
            await asyncio.sleep(self.EVENING_TIME)
            for p in self.alive_list:
                p.blackmailed = False
            # NIGHT
            self.STATE = "NIGHT"
            data = {
                "type": "state",
                "state": self.STATE,
            }
            await self.emit_event(sio, data, room=self.roomID)
            await self.trigger_night_events(sio)
            await self.emit_player_list(sio)
            await self.clear_up()
            await asyncio.sleep(5)

    async def finish_game(self, sio):
        logger.info(f"Game finished in room #{self.roomID}")
        remaining = self.alive_list
        if len(remaining) == 0:
            pass
        else:
            # 같이 이길 수 없는 세력들
            for p in remaining:
                if isinstance(p.role, roles.Arsonist):
                    self.win(roles.Arsonist, False)
                    break
            else:
                for p in remaining:
                    if isinstance(p.role, roles.SerialKiller):
                        self.win(roles.SerialKiller, False)
                        break
                else:
                    for p in remaining:
                        if isinstance(p.role, roles.MassMurderer):
                            self.win(roles.MassMurderer, False)
                            break
                    else:
                        for p in remaining:
                            if isinstance(p.role, roles.Triad):
                                self.win(roles.Triad, True)
                                break
                        else:
                            for p in remaining:
                                if isinstance(p.role, roles.Mafia):
                                    self.win(roles.Mafia, True)
                                    break
                            else:
                                for p in remaining:
                                    if isinstance(p.role, roles.Cult):
                                        self.win(roles.Cult, True)
                                        break
                                else:
                                    for p in remaining:
                                        if isinstance(p.role, roles.NeutralEvil):
                                            self.win(roles.NeutralEvil, False)
                                            break
                                    else:
                                        for p in remaining:
                                            if isinstance(p.role, roles.Town):
                                                self.win(roles.Town, True)
                                                break
            for p in remaining:
                if isinstance(p.role, roles.Scumbag):
                    self.win(roles.Scumbag, False)
                elif isinstance(p.role, roles.Witch):
                    self.win(roles.Witch, False)
                elif isinstance(p.role, roles.Judge):
                    self.win(roles.Judge, False)
                elif isinstance(p.role, roles.Auditor):
                    self.win(roles.Auditor, False)
                elif isinstance(p.role, roles.Survivor):
                    self.win(roles.Survivor, False)
                elif isinstance(p.role, roles.Amnesiac):
                    self.win(roles.Amnesiac, False)
        data = {
            "type": "game_over",
            "winner": [(p.nickname, p.role.name) for p in self.players.values() if p.win]
        }
        await self.emit_event(sio, data, room=self.roomID)
        self.inGame = False
        await asyncio.gather(*[sio.close_room(in_game_chatID) for in_game_chatID in (self.hell,
                                                                                     self.night_chat[roles.Mafia],
                                                                                     self.night_chat[roles.Triad],
                                                                                     self.night_chat[roles.Cult],
                                                                                     self.night_chat[roles.Spy],
                                                                                     self.night_chat[roles.Mason])])
        await asyncio.gather(*[sio.close_room(p.jailID) for p in self.players.values()])
        async with aiosqlite.connect("sql/records.db") as DB:
            def get_random_alphanumeric_string(length): # TODO: 정말로 alphanum만 오는지 확인 (SQL 인젝션 방어)
                letters_and_digits = string.ascii_letters + string.digits
                result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
                return result_str
            async def insert(DB, record):
                query = f'INSERT INTO {gamelog_id} values ("{record[0]}", "{record[1]}", "{record[2]}");'
                await DB.execute(query)
                await DB.commit()
            while True:
                try:
                    gamelog_id = get_random_alphanumeric_string(32)
                    query = f"CREATE TABLE {gamelog_id} (time string not null, message string not null, receivers string not null);"
                    await DB.execute(query)
                    break
                except sqlite3.OperationalError: # gamelog_id가 중복되는 경우
                    continue
            await asyncio.gather(*[insert(DB, record) for record in self.message_record])
            data = {
                "type": "save_done",
                "link": gamelog_id,
            }
            await sio.emit("event", data, room=self.roomID)
        del self.alive_list
        del self.players
        del self

    async def emit_player_list(self, sio):
        if self.inGame:
            coros = []
            for p in self.players.values():
                to_send = []
                if isinstance(p.role, roles.Mafia):
                    for p2 in self.players.values():
                        to_send.append((p2.nickname, p2.alive, p2.role.name if isinstance(p2.role, roles.Mafia) or (not p2.alive and not p2.sanitized) else ("???" if p2.sanitized else None)))
                    data = {
                        "player_list": to_send,
                        "inGame": self.inGame,
                    }
                    coros.append(sio.emit("player_list", data, room=p.sid))
                elif isinstance(p.role, roles.Triad):
                    for p2 in self.players.values():
                        to_send.append((p2.nickname, p2.alive, p2.role.name if isinstance(p2.role, roles.Triad) or (not p2.alive and not p2.sanitized) else ("???" if p2.sanitized else None)))
                    data = {
                        "player_list": to_send,
                        "inGame": self.inGame,
                    }
                    coros.append(sio.emit("player_list", data, room=p.sid))
                elif isinstance(p.role, roles.Cult):
                    for p2 in self.players.values():
                        to_send.append((p2.nickname, p2.alive, p2.role.name if isinstance(p2.role, roles.Cult) or (not p2.alive and not p2.sanitized) else ("???" if p2.sanitized else None)))
                    data = {
                        "player_list": to_send,
                        "inGame": self.inGame,
                    }
                    coros.append(sio.emit("player_list", data, room=p.sid))
                elif isinstance(p.role, roles.Mason):
                    for p2 in self.players.values():
                        to_send.append((p2.nickname, p2.alive, p2.role.name if isinstance(p2.role, roles.Mason) or (not p2.alive and not p2.sanitized) else ("???" if p2.sanitized else None)))
                    data = {
                        "player_list": to_send,
                        "inGame": self.inGame,
                    }
                    coros.append(sio.emit("player_list", data, room=p.sid))
                else:
                    for p2 in self.players.values():
                        to_send.append((p2.nickname, p2.alive, p2.role.name if p is p2 or (not p2.alive and not p2.sanitized) else ("???" if p2.sanitized else None)))
                    data = {
                        "player_list": to_send,
                        "inGame": self.inGame,
                    }
                    coros.append(sio.emit("player_list", data, room=p.sid))
            await asyncio.gather(*coros, return_exceptions=True)
        else:
            player_list = map(lambda s: s["nickname"], await asyncio.gather(*[sio.get_session(sid) for sid in self.members], return_exceptions=True))
            readied = await asyncio.gather(*[sio.get_session(sid) for sid in self.readied], return_exceptions=True)
            readied = {s["nickname"] for s in readied if not isinstance(s, Exception)}
            player_list = [(nickname, nickname in readied) for nickname in player_list]
            data = {
                "player_list": player_list,
                "inGame": self.inGame,
            }
            await sio.emit("player_list", data, room=self.roomID)

    async def someone_entered(self, sid, sio):
        await self.emit_player_list(sio)
        if self.inGame:
            enterer = (await sio.get_session(sid))["nickname"]
            if enterer in self.players and self.players[enterer].alive:
                pass
            else:
                sio.enter_room(sid, self.hell)

    async def someone_left(self, sid, sio):
        if sid in self.readied:
            self.readied.remove(sid)
        await self.emit_player_list(sio)
        if self.inGame:
            for p in self.players.values():
                if p.sid==sid:
                    p.suicide_today = True
                    break


class Player:
    def __init__(self, sid, roomID, nickname, role, sio, alive=True):
        self.sid = sid
        self.nickname = nickname
        self.role = role
        self.role_record = [self.role]
        self.sio = sio
        self.alive = alive
        self.win = False
        self.votes = 1
        self.has_voted = False
        self.voted_to_whom = None
        self.voted_to_execution_of_jester = False
        self.voted_to_which = None
        self.votes_gotten = 0
        self.voted_guilty = 0
        self.voted_innocent = 0
        self.lw = ""  # last will
        self.visited_by = [None, set()]
        self.murdered_by = []
        self.controlled_by = None
        self.wear_vest_today = False
        self.alert_today = False
        self.burn_today = False
        self.curse_today = False
        self.remember_today = False
        self.suicide_today = False
        self.blackmailed = False
        self.framed = False
        self.sanitized = False
        self.cannot_murder_until = 0
        self.protected_from_cult = False
        self.protected_from_auditor = False
        self.oiled = False
        self.jailed = False
        self.jailed_by = []
        self.jailID = str(roomID) + "_Jail_" + self.nickname
        self.has_jailed_whom = None
        self.kill_the_jailed_today = False
        self.has_disguised = False
        self.has_cursed = False
        self.bodyguarded_by = []  # list of Player objects
        self.healed_by = []  # list of Player objects
        self.target1 = None
        self.target2 = None
        self.curse_target = None
        self.recruit_target = None
        self.remember_target = None
        self.night_chat = None
        self.crimes = {
            "무단침입": False,
            "납치": False,
            "부패": False,
            "신분도용": False,
            "호객행위": False,
            "살인": False,
            "치안을 어지럽힘": False,
            "음모": False,
            "재물 손괴": False,
            "방화": False,
        }

    async def die(self, room, attacker, dead_while_guarding=False):
        if attacker!="VOTE":
            room.die_tonight.add(self)
        self.alive = False
        self.murdered_by.append(attacker if attacker=="VOTE" else attacker.role.team)
        data = {
            "type": "dead",
            "attacker": attacker.role.name if attacker!="VOTE" else "VOTE",
            "dead_while_guarding": dead_while_guarding,
        }
        await room.emit_event(self.sio, data, room=self.sid)
        if self.night_chat:
            self.sio.leave_room(self.sid, self.night_chat)
            self.night_chat = None
        self.sio.enter_room(self.sid, room.hell)

    async def attacked(self, room, attacker):
        data = {
            "type": "attacked",
            "attacker": attacker.role.name,
        }
        await room.emit_event(self.sio, data, room=self.sid)
        data = {
            "type": "attack_failed",
        }
        await room.emit_event(self.sio, data, room=attacker.sid)
        await asyncio.sleep(5)

    async def healed(self, room, attacker, healer):
        data = {
            "type": "healed",
            "attacker": attacker.role.name,
            "healer": healer.role.name,
        }
        await room.emit_event(self.sio, data, room=self.sid)
        if isinstance(healer.role, roles.WitchDoctor):
            if isinstance(self.role, roles.Mason):
                pass # TODO: 발각
            else:
                await room.convert_role(self.sio, healer, self, roles.Cultist())
        await asyncio.sleep(5)

    async def bodyguarded(self, room, attacker):
        data = {
            "type": "bodyguarded",
            "attacker": attacker.role.name,
        }
        await room.emit_event(self.sio, data, room=self.sid)
        await asyncio.sleep(5)

    async def suicide(self, room, reason):
        # TODO: suicide(room=self, )를 그냥 die()로 대체
        room.die_tonight.add(self)
        self.alive = False
        self.murdered_by.append(reason)
        data = {
            "type": "suicide",
            "reason": reason,
        }
        await room.emit_event(self.sio, data, room=self.sid)
        await asyncio.sleep(5)
