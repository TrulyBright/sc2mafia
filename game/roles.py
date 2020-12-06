class Role:
  pass

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


"""
==========
Roles
==========
"""


class Mafioso(MafiaKilling):
  name='마피아 일원'

class Citizen(TownGovernment):
  name='시민'

class Doctor(TownProtective):
  name='의사'

class Sheriff(TownInvestigative):
  name='보안관'
