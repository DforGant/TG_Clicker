import json

# класс для передачи данных 
class Message:
    def __init__(self,header,content):
        self.header = header
        self.content = content

    def to_json(self):
        return json.dumps(self.__dict__)
