class GameRoom:
  def __init__(self, title, capacity, host, private=False, password=None):
    assert type(title) is str
    assert type(capacity) is int
    assert type(private) is bool
    assert type(password) is str or password is None
    self.title = title
    self.capacity = capacity
    self.members = []
    self.private = private
    self.password = password
    self.inGame = False

  def isFull(self):
    return len(self.members)>=self.capacity
