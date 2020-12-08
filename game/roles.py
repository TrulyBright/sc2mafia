class Role:
    def __init__(self):
        self.detection_immune = False


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


class MafiaKilling(Mafia):
    pass


class NeutralBenign(Neutral):
    pass


class NeutralEvil(Neutral):
    pass


class NeutralKilling(NeutralEvil):
    pass


class Cult(NeutralEvil):
    category = '이교도'


"""
==========
Roles
==========
"""


class Mafioso(MafiaKilling):
    name = '마피아 일원'

    def __init__(self):
        super().__init__()
        self.attack_level = 1

    def visit(self, visited):
        if visited.role.defense_level >= self.attack_level:
            return False
        visited.die()
        return True


class Citizen(TownGovernment):
    name = '시민'


class Doctor(TownProtective):
    name = '의사'


class Sheriff(TownInvestigative):
    name = '보안관'

    def check(self, checked):
        if checked.role.detection_immune:
            return False
        if isinstance(checked.role, Mafia):
            return checked.role.team
        if isinstance(checked.role, Triad):
            return checked.role.team
        if isinstance(checked.role, Cult):
            return checked.role.category
        if isinstance(checked.role, NeutralKilling):
            return checked.role.name
        return False


class Witch(NeutralEvil):
    name = '마녀'
