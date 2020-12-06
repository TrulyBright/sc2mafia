class Role:
  pass



class Mafia(Role):
  pass

class Town(Role):
  pass



class Mafioso(Mafia):
  name='마피아 일원'

class Citizen(Town):
  name='시민'

class Doctor(Town):
  name='의사'

class Sheriff(Town):
  name='보안관'
