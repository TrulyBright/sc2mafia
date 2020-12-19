class Role:
    def __init__(self):
        self.detection_immune = False
        self.offense_level = 0
        self.defense_level = 0


"""
==========
Teams
==========
"""


class Town(Role):
    team = '시민'


class Mafia(Role):
    team = '마피아'


class Triad(Role):
    team = '삼합회'


class Neutral(Role):
    team = '중립'


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
    def __init__(self):
        super().__init__()
        self.offense_level = 2


class BusDriver(TownProtective, TownPower):
    name = "버스기사"


class Citizen(TownGovernment):
    name = "시민"


class Coroner(TownInvestigative):
    name = "검시관"


class Crier(TownGovernment):
    name = "포고꾼"


class Detective(TownInvestigative):
    name = "형사"

    def check(self, target):
        return None if target.target1 is None else target.target1.nickname


class Doctor(TownProtective):
    name = "의사"


class Escort(TownProtective):
    name = "기생"


class Investigator(TownInvestigative):
    name = "탐정"
    def check(self, target):
        return target.crimes


class Jailor(TownPower, TownKilling):
    name = "간수"


class Lookout(TownInvestigative):
    name = "감시자"
    def check(self, target):
        return target.visited_by


class Marshall(TownGovernment):
    name = "원수"


class Mason(TownGovernment):
    name = "비밀조합원"


class MasonLeader(TownGovernment):
    name = "비밀조합장"
    def __init__(self):
        super().__init__()
        self.offense_level = 1


class Mayor(TownGovernment):
    name = "시장"


class Sheriff(TownInvestigative):
    name = "보안관"
    def check(self, target):
        role = target.role
        if isinstance(role, Mafia):
            return Mafia.team
        if isinstance(role, Triad):
            return Triad.team
        if isinstance(role, Cult):
            return Cult.team
        for killing in (SerialKiller,
                        MassMurderer,
                        Arsonist):
            if isinstance(role, killing):
                return killing.name
        return False


class Spy(TownPower):
    name = "정보원"


class Stump(TownGovernment):
    name = "나무 그루터기"


class Veteran(TownKilling, TownPower):
    name = "퇴역군인"


class Vigilante(TownKilling):
    name = "자경대원"
    def __init__(self):
        super().__init__()
        offense_level = 1


# Mafia

class Agent(MafiaSupport):
    name = "요원"


class Beguiler(MafiaDeception):
    name = "잠입자"


class Blackmailer(MafiaSupport):
    name = "협박자"


class Consigliere(MafiaSupport):
    name = "조언자"
    def check(self, target):
        return target.role.name


class Consort(MafiaSupport):
    name = "매춘부"


class Disguiser(MafiaDeception, MafiaSupport):
    name = "변장자"
    offense_level = 1


class Framer(MafiaDeception):
    name = "조작자"


class Godfather(MafiaKilling):
    name = "대부"
    def __init__(self):
        super().__init__()
        self.offense_level = 1


class Janitor(MafiaDeception):
    name = "관리인"


class Kidnapper(MafiaKilling, MafiaSupport):
    name = "납치범"


class Mafioso(MafiaKilling):
    name = "마피아 일원"
    def __init__(self):
        super().__init__()
        self.offense_level = 1


#Triad
class Administrator(TriadSupport):
    name = "백지선"
    def check(self, target):
        return target.role.name


class Deceiver(TriadDeception):
    name = "사기꾼"


class DragonHead(TriadKilling):
    name = "용두"
    def __init__(self):
        super().__init__()
        self.offense_level = 1
        self.defense_level = 1


class Enforcer(TriadKilling):
    name = "홍곤"
    def __init__(self):
        super().__init__()
        self.offense_level = 1


class Forger(TriadDeception):
    name = "위조꾼"


class IncenseMaster(TriadDeception):
    name = "향주"


class Informant(TriadDeception, TriadKilling):
    name = "밀고자"
    def __init__(self):
        super().__init__()
        self.offense_level = 1


class Interrogator(TriadKilling, TriadSupport):
    name = "심문자"


class Liaison(TriadSupport):
    name = "간통범"


class Silencer(TriadSupport):
    name = "침묵자"


class Vanguard(TriadSupport):
    name = "선봉"


# Neutral
class Amnesiac(NeutralBenign):
    name = "기억상실자"


class Arsonist(NeutralKilling):
    name = "방화범"
    def __init__(self):
        super().__init__()
        self.offense_level = 1
        self.defense_level = 1


class Auditor(NeutralEvil):
    name = "회계사"


class Cultist(Cult):
    name = "이교도"


class Executioner(NeutralBenign):
    name = "처형자"


class Jester(NeutralBenign):
    name = "어릿광대"


class Judge(NeutralEvil):
    name = "판사"


class MassMurderer(NeutralKilling):
    name = "대량 학살자"
    def __init__(self):
        super().__init__()
        self.offense_level = 1
        self.defense_level = 1


class Scumbag(NeutralEvil):
    name = "인간쓰레기"


class SerialKiller(NeutralKilling):
    name = "연쇄살인마"
    def __init__(self):
        super().__init__()
        self.offense_level = 1
        self.defense_level = 1


class Survivor(NeutralBenign):
    name = "생존자"


class Witch(NeutralEvil):
    name = "마녀"


class WitchDoctor(Cult):
    name = "요술사"
