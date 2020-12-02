class Room:
  def __init__(self, title, capacity, private):
    assert type(title) is str
    assert type(capacity) is int
    assert type(private) is bool
    self.title = title
    self.capacity = capacity
    self.private = private
