import json
from functools import total_ordering


@total_ordering
class Message:
    def __init__(self, id, message):
        self.id = id
        self.message = message

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
  
    def __ge__(self, obj):
        return ((self.id) >= (obj.id))

    def __repr__(self):
        return f'Message({self.id}, {self.message[:10]})'