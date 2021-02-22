import random

class Role:
    def __init__(self):
        self.detection_immune = False
        self.offense_level = 0
        self.defense_level = 0
        self.visitable_self = False
        self.unhealable = False
        self.cannot_be_blocked = False


"""
==========
Teams
==========
"""


class Town(Role):
    team = "시민" # 속성 "team"을 공유하는 클래스끼리는 같이 승리함.


class Mafia(Role):
    team = "마피아"


class Triad(Role):
    team = "삼합회"


class Neutral(Role):
    pass

"""
==========
Categories
==========
"""

# Town
class TownGovernment(Town):
    pass


class TownProtective(Town):
    pass


class TownKilling(Town):
    pass


class TownInvestigative(Town):
    pass


class TownPower(Town):
    pass


# Mafia
class MafiaKilling(Mafia):
    pass


class MafiaSupport(Mafia):
    pass


class MafiaDeception(Mafia):
    pass


# Triad
class TriadKilling(Triad):
    pass


class TriadSupport(Triad):
    pass


class TriadDeception(Triad):
    pass


# Neutral
class NeutralBenign(Neutral):
    pass


class NeutralEvil(Neutral):
    pass


class NeutralKilling(NeutralEvil):
    pass


# Cult
class Cult(NeutralEvil):
    team = "이교도"


"""
==========
Roles
==========
"""


# Town
class Bodyguard(TownProtective, TownKilling):
    name = "경호원"

    def __init__(self, setup):
        super().__init__()
        self.offense_level = setup["options"]["role_setting"][self.name]["offense_level"]
        self.unhealable = setup["options"]["role_setting"][self.name]["unhealable"]
        self.prevents_conversion = setup["options"]["role_setting"][self.name]["prevents_conversion"]

#
# class BusDriver(TownProtective, TownPower): # NeutralEvil
#     name = "버스기사"
#     def __init__(self):
#         super().__init__()
#         self.visitable_self = True


class Citizen(TownGovernment):
    name = "시민"
    def __init__(self, setup):
        super().__init__()
        self.ability_opportunity = 1 if setup["options"]["role_setting"][self.name]["bulletproof"] else 0
        self.recruitable = setup["options"]["role_setting"][self.name]["recruitable"]


class Coroner(TownInvestigative):
    name = "검시관"
    def __init__(self, setup):
        super().__init__()
        self.discover_all_targets = setup["options"]["role_setting"][self.name]["discover_all_targets"]
        self.discover_lw = setup["options"]["role_setting"][self.name]["discover_lw"]
        self.discover_death_type = setup["options"]["role_setting"][self.name]["discover_death_type"]
        self.discover_visitor_role = setup["options"]["role_setting"][self.name]["discover_visitor_role"]


class Crier(TownGovernment):
    name = "포고꾼"

    def __init__(self, setup):
        super().__init__()


class Detective(TownInvestigative):
    name = "형사"
    def __init__(self, setup):
        super().__init__()
        self.ignore_detection_immune = setup["options"]["role_setting"][self.name]["ignore_detection_immune"]


class Doctor(TownProtective):
    name = "의사"
    def __init__(self, setup):
        super().__init__()
        self.knows_if_attacked = setup["options"]["role_setting"][self.name]["knows_if_attacked"]
        self.prevents_cult_conversion = setup["options"]["role_setting"][self.name]["prevents_cult_conversion"]
        self.knows_if_culted = setup["options"]["role_setting"][self.name]["knows_if_culted"]
        self.WitchDoctor_when_converted = setup["options"]["role_setting"][self.name]["WitchDoctor_when_converted"]


class Escort(TownProtective):
    name = "기생"
    def __init__(self, setup):
        super().__init__()
        self.cannot_be_blocked = setup["options"]["role_setting"][self.name]["cannot_be_blocked"]
        self.detects_block_immune_target = setup["options"]["role_setting"][self.name]["detects_block_immune_target"]
        self.recruitable = setup["options"]["role_setting"][self.name]["recruitable"]


class Investigator(TownInvestigative):
    name = "탐정"
    def __init__(self, setup):
        super().__init__()
        self.detect_exact_role = setup["options"]["role_setting"][self.name]["detect_exact_role"]


class Jailor(TownPower, TownKilling):
    name = "간수"

    def __init__(self, setup):
        super().__init__()
        self.ability_opportunity = setup["options"]["role_setting"][self.name]["execution_chance"]


class Lookout(TownInvestigative):
    name = "감시자"
    def __init__(self, setup):
        super().__init__()
        self.visitable_self = True
        self.ignore_detection_immune = setup["options"]["role_setting"][self.name]["ignore_detection_immune"]


class Marshall(TownGovernment):
    name = "원수"
    def __init__(self, setup):
        super().__init__()
        self.ability_opportunity = setup["options"]["role_setting"][self.name]["lynch_chance"]
        self.executions_per_group = setup["options"]["role_setting"][self.name]["executions_per_group"]
        self.unhealable = setup["options"]["role_setting"][self.name]["unhealable"]


class Mason(TownGovernment):
    name = "비밀조합원"
    def __init__(self, setup):
        super().__init__()
        self.promoted_if_alone = setup["options"]["role_setting"]["비밀조합원"]["promoted_if_alone"]


class MasonLeader(Mason):
    name = "비밀조합장"

    def __init__(self, setup):
        super().__init__(setup)
        self.offense_level = 1
        self.ability_opportunity = setup["options"]["role_setting"][self.name]["recruit_chance"]


class Mayor(TownGovernment):
    name = "시장"
    def __init__(self, setup):
        super().__init__()
        self.lose_extra_votes = setup["options"]["role_setting"][self.name]["lose_extra_votes"]
        self.extra_votes = setup["options"]["role_setting"][self.name]["extra_votes"]
        self.unhealable = setup["options"]["role_setting"][self.name]["unhealable"]


class Sheriff(TownInvestigative):
    name = "보안관"

    def __init__(self, setup):
        super().__init__()
        self.detect_mafia_and_triad = setup["options"]["role_setting"][self.name]["detect_mafia_and_triad"]
        self.detect_SerialKiller = setup["options"]["role_setting"][self.name]["detect_SerialKiller"]
        self.detect_Arsonist = setup["options"]["role_setting"][self.name]["detect_Arsonist"]
        self.detect_Cult = setup["options"]["role_setting"][self.name]["detect_Cult"]
        self.detect_MassMurderer = setup["options"]["role_setting"][self.name]["detect_MassMurderer"]

class Spy(TownPower):
    name = "정보원"
    def __init__(self, setup):
        super().__init__()


class Stump(TownPower):
    name = "나무 그루터기"
    def __init__(self, setup):
        super().__init__()


class Veteran(TownKilling, TownPower):
    name = "퇴역군인"
    def __init__(self, setup):
        super().__init__()
        self.offense_level = setup["options"]["role_setting"][self.name]["offense_level"]
        self.ability_opportunity = setup["options"]["role_setting"][self.name]["alert_chance"]


class Vigilante(TownKilling):
    name = "자경대원"

    def __init__(self, setup):
        super().__init__()
        self.offense_level = 1
        self.ability_opportunity = setup["options"]["role_setting"][self.name]["kill_chance"]
        self.suicides_if_shot_town = setup["options"]["role_setting"][self.name]["suicides_if_shot_town"]


# Mafia


class Agent(MafiaSupport):
    name = "요원"

    def __init__(self, setup):
        super().__init__()
        self.nights_between_shadowings = setup["options"]["role_setting"][self.name]["nights_between_shadowings"]
        self.becomes_mafioso = setup["options"]["role_setting"][self.name]["becomes_mafioso"]


class Beguiler(MafiaDeception):
    name = "잠입자"

    def __init__(self, setup):
        super().__init__()
        self.ability_opportunity = setup["options"]["role_setting"][self.name]["hide_chance"]
        self.target_is_notified = setup["options"]["role_setting"][self.name]["target_is_notified"]
        self.can_hide_behind_member = setup["options"]["role_setting"][self.name]["can_hide_behind_member"]
        self.becomes_mafioso = setup["options"]["role_setting"][self.name]["becomes_mafioso"]


class Blackmailer(MafiaSupport):
    name = "협박자"

    def __init__(self, setup):
        super().__init__()
        self.can_talk_during_trial = setup["options"]["role_setting"][self.name]["can_talk_during_trial"]
        self.becomes_mafioso = setup["options"]["role_setting"][self.name]["becomes_mafioso"]


class Consigliere(MafiaSupport):
    name = "조언자"

    def __init__(self, setup):
        super().__init__()
        self.promoted_if_no_Godfather = setup["options"]["role_setting"][self.name]["promoted_if_no_Godfather"]
        self.detect_exact_role = setup["options"]["role_setting"][self.name]["detect_exact_role"]
        self.becomes_mafioso = setup["options"]["role_setting"][self.name]["becomes_mafioso"]

class Consort(MafiaSupport):
    name = "매춘부"

    def __init__(self, setup):
        super().__init__()
        self.cannot_be_blocked = setup["options"]["role_setting"][self.name]["cannot_be_blocked"]
        self.detects_block_immune_target = setup["options"]["role_setting"][self.name]["detects_block_immune_target"]
        self.becomes_mafioso = setup["options"]["role_setting"][self.name]["becomes_mafioso"]


#
# class Disguiser(MafiaDeception, MafiaKilling):
#     name = "변장자"
#
#     def __init__(self):
#         super().__init__()
#         self.offense_level = 1


class Framer(MafiaDeception):
    name = "조작자"

    def __init__(self, setup):
        super().__init__()
        self.detection_immune = setup["options"]["role_setting"][self.name]["detection_immune"]
        self.becomes_mafioso = setup["options"]["role_setting"][self.name]["becomes_mafioso"]


class Godfather(MafiaKilling):
    name = "대부"

    def __init__(self, setup):
        super().__init__()
        self.offense_level = 1
        self.defense_level = setup["options"]["role_setting"][self.name]["defense_level"]
        self.cannot_be_blocked = setup["options"]["role_setting"][self.name]["cannot_be_blocked"]
        self.detection_immune = setup["options"]["role_setting"][self.name]["detection_immune"]
        self.killable_without_mafioso = setup["options"]["role_setting"][self.name]["killable_without_mafioso"]
        self.ability_opportunity = 999


class Janitor(MafiaDeception):
    name = "관리인"

    def __init__(self, setup):
        super().__init__()
        self.ability_opportunity = setup["options"]["role_setting"][self.name]["sanitize_chance"]
        self.becomes_mafioso = setup["options"]["role_setting"][self.name]["becomes_mafioso"]


class Kidnapper(MafiaKilling, MafiaSupport):
    name = "납치범"

    def __init__(self, setup):
        super().__init__()
        self.offense_level = 1
        self.ability_opportunity = 1
        self.can_jail_members = setup["options"]["role_setting"][self.name]["can_jail_members"]
        self.becomes_mafioso = setup["options"]["role_setting"][self.name]["becomes_mafioso"]


class Mafioso(MafiaKilling):
    name = "마피아 일원"

    def __init__(self, setup):
        super().__init__()
        self.offense_level = 1
        self.ability_opportunity = 999


# Triad
class Administrator(TriadSupport):
    name = "백지선"

    def __init__(self, setup):
        super().__init__()
        self.promoted_if_no_Dragonhead = setup["options"]["role_setting"][self.name]["promoted_if_no_Dragonhead"]
        self.detect_exact_role = setup["options"]["role_setting"][self.name]["detect_exact_role"]
        self.becomes_enforcer = setup["options"]["role_setting"][self.name]["becomes_enforcer"]

class Deceiver(TriadDeception):
    name = "사기꾼"

    def __init__(self, setup):
        super().__init__()
        self.ability_opportunity = setup["options"]["role_setting"][self.name]["hide_chance"]
        self.target_is_notified = setup["options"]["role_setting"][self.name]["target_is_notified"]
        self.can_hide_behind_member = setup["options"]["role_setting"][self.name]["can_hide_behind_member"]
        self.becomes_enforcer = setup["options"]["role_setting"][self.name]["becomes_enforcer"]


class DragonHead(TriadKilling):
    name = "용두"

    def __init__(self, setup):
        super().__init__()
        self.offense_level = 1
        self.defense_level = setup["options"]["role_setting"][self.name]["defense_level"]
        self.cannot_be_blocked = setup["options"]["role_setting"][self.name]["cannot_be_blocked"]
        self.detection_immune = setup["options"]["role_setting"][self.name]["detection_immune"]
        self.killable_without_enforcer = setup["options"]["role_setting"][self.name]["killable_without_enforcer"]
        self.ability_opportunity = 999


class Enforcer(TriadKilling):
    name = "홍곤"

    def __init__(self, setup):
        super().__init__()
        self.offense_level = 1
        self.ability_opportunity = 999


class Forger(TriadDeception):
    name = "위조꾼"

    def __init__(self, setup):
        super().__init__()
        self.detection_immune = setup["options"]["role_setting"][self.name]["detection_immune"]
        self.becomes_enforcer = setup["options"]["role_setting"][self.name]["becomes_enforcer"]


class IncenseMaster(TriadDeception):
    name = "향주"

    def __init__(self, setup):
        super().__init__()
        self.ability_opportunity = setup["options"]["role_setting"][self.name]["sanitize_chance"]
        self.becomes_enforcer = setup["options"]["role_setting"][self.name]["becomes_enforcer"]

#
# class Informant(TriadDeception, TriadKilling):
#     name = "밀고자"
#
#     def __init__(self, setup):
#         super().__init__()
#         self.offense_level = 1


class Interrogator(TriadKilling, TriadSupport):
    name = "심문자"

    def __init__(self, setup):
        super().__init__()
        self.offense_level = 1
        self.ability_opportunity = 1
        self.can_jail_members = setup["options"]["role_setting"][self.name]["can_jail_members"]
        self.becomes_enforcer = setup["options"]["role_setting"][self.name]["becomes_enforcer"]


class Liaison(TriadSupport):
    name = "간통범"

    def __init__(self, setup):
        super().__init__()
        self.cannot_be_blocked = setup["options"]["role_setting"][self.name]["cannot_be_blocked"]
        self.detects_block_immune_target = setup["options"]["role_setting"][self.name]["detects_block_immune_target"]
        self.becomes_enforcer = setup["options"]["role_setting"][self.name]["becomes_enforcer"]


class Silencer(TriadSupport):
    name = "침묵자"

    def __init__(self, setup):
        super().__init__()
        self.can_talk_during_trial = setup["options"]["role_setting"][self.name]["can_talk_during_trial"]
        self.becomes_enforcer = setup["options"]["role_setting"][self.name]["becomes_enforcer"]


class Vanguard(TriadSupport):
    name = "선봉"

    def __init__(self, setup):
        super().__init__()
        self.nights_between_shadowings = setup["options"]["role_setting"][self.name]["nights_between_shadowings"]
        self.becomes_enforcer = setup["options"]["role_setting"][self.name]["becomes_enforcer"]


# Neutral
class Amnesiac(NeutralBenign):
    team = "기억상실자"
    name = "기억상실자"

    def __init__(self, setup):
        super().__init__()
        self.revealed = setup["options"]["role_setting"][self.name]["revealed"]
        self.cannot_remember_town = setup["options"]["role_setting"][self.name]["cannot_remember_town"]
        self.cannot_remember_killing_role = setup["option"]["role_setting"][self.name]["cannot_remember_killing_role"]
        self.cannot_remember_mafia_and_triad = setup["options"]["role_setting"][self.name]["cannot_remember_mafia_and_triad"]


class Arsonist(NeutralKilling):
    team = "방화범"
    name = "방화범"

    def __init__(self, setup):
        super().__init__()
        self.offense_level = setup["options"]["role_setting"][self.name]["offense_level"]
        self.defense_level = setup["options"]["role_setting"][self.name]["defense_level"]
        self.fire_spreads = setup["options"]["role_setting"][self.name]["fire_spreads"]
        self.target_is_notified = setup["options"]["role_setting"][self.name]["target_is_notified"]
        self.douse_blocker = setup["options"]["role_setting"][self.name]["douse_blocker"]


class Auditor(NeutralEvil):
    team = "회계사"
    name = "회계사"

    def __init__(self, setup):
        super().__init__()
        self.ability_opportunity = setup["options"]["role_setting"][self.name]["audit_chance"]
        self.can_audit_mafia = setup["options"]["role_setting"][self.name]["can_audit_mafia"]
        self.can_audit_triad = setup["options"]["role_setting"][self.name]["can_audit_triad"]
        self.can_audit_night_immune = setup["options"]["role_setting"][self.name]["can_audit_night_immune"]


class Cultist(Cult):
    name = "이교도"

    def __init__(self, setup):
        super().__init__()
        self.can_convert_night_immune = setup["options"]["role_setting"][self.name]["can_convert_night_immune"]
        self.nights_between_conversion = setup["options"]["role_setting"][self.name]["nights_between_conversion"]


class Executioner(NeutralBenign):
    name = "처형자"

    def __init__(self, setup):
        super().__init__()
        self.becomes_Jester = setup["options"]["role_setting"][self.name]["becomes_Jester"]
        self.target_is_town = setup["options"]["role_setting"][self.name]["target_is_town"]
        self.win_if_survived = setup["options"]["role_setting"][self.name]["win_if_survived"]
        self.defense_level = setup["options"]["role_setting"][self.name]["defense_level"]

    def set_target(self, player_list):
        if self.target_is_town:
            self.target = random.choice([p for p in player_list if isinstance(p.role, Town)])
        else:
            self.target = random.choice([p for p in player_list if not isinstance(p.role, Jester)])


class Jester(NeutralBenign):
    name = "어릿광대"

    def __init__(self, setup):
        super().__init__()
        self.randomly_suicide = setup["options"]["role_setting"][self.name]["randomly_suicide"]


class Judge(NeutralEvil):
    team = "판사"
    name = "판사"

    def __init__(self, setup):
        super().__init__()
        self.ability_opportunity = setup["options"]["role_setting"][self.name]["court_chance"]
        self.nights_between_court = setup["options"]["role_setting"][self.name]["nights_between_court"]
        self.extra_votes = setup["options"]["role_setting"][self.name]["extra_votes"]
        self.cannot_open_court_until = 0

class MassMurderer(NeutralKilling):
    team = "대량학살자"
    name = "대량학살자"

    def __init__(self, setup):
        super().__init__()
        self.offense_level = 1
        self.defense_level = setup["options"]["role_setting"][self.name]["defense_level"]
        self.visitable_self = setup["options"]["role_setting"][self.name]["can_visit_self"]
        self.nights_between_murder = setup["options"]["role_setting"][self.name]["nights_between_murder"]
        self.detection_immune = setup["options"]["role_setting"][self.name]["detection_immune"]
        self.cannot_murder_until = 0


class Scumbag(NeutralEvil):
    team = "인간쓰레기"
    name = "인간쓰레기"

    def __init__(self, setup):
        super().__init__()


class SerialKiller(NeutralKilling):
    team = "연쇄살인마"
    name = "연쇄살인마"

    def __init__(self, setup):
        super().__init__()
        self.offense_level = 1
        self.defense_level = setup["options"]["role_setting"][self.name]["defense_level"]
        self.kill_blocker = setup["options"]["role_setting"][self.name]["kill_blocker"]
        self.win_if_1v1_with_Arsonist = setup["options"]["role_setting"][self.name]["win_if_1v1_with_Arsonist"]
        self.detection_immune = setup["options"]["role_setting"][self.name]["detection_immune"]


class Survivor(NeutralBenign):
    team = "생존자"
    name = "생존자"

    def __init__(self, setup):
        super().__init__()
        self.ability_opportunity = setup["options"]["role_setting"][self.name]["bulletproof_chance"]


class Witch(NeutralEvil):
    team = "마녀"
    name = "마녀"
    def __init__(self, setup):
        super().__init__()
        self.visitable_self = setup["options"]["role_setting"][self.name]["can_control_self"]
        self.target_is_notified = setup["options"]["role_setting"][self.name]["target_is_notified"]
        self.WitchDoctor_when_converted = setup["options"]["role_setting"][self.name]["WitchDoctor_when_converted"]
        self.ability_opportunity = 1


class WitchDoctor(Cult):
    name = "요술사"

    def __init__(self, setup):
        super().__init__()
        self.ability_opportunity = setup["options"]["role_setting"][self.name]["save_chance"]
        self.night_between_save = setup["options"]["role_setting"][self.name]["night_between_save"]
        self.detection_immune = setup["options"]["role_setting"][self.name]["detection_immune"]
        self.cannot_save_until = 0
