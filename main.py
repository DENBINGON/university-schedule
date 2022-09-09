from vk_api.longpoll import VkLongPoll, VkEventType
from parser import Bot
import vk_api
import random
import json
import os
import db

class Program:
    config = None
    session = None
    longpoll = None
    database = None
    def __int__(self):
        self.config = json.loads(open("config/config.json", "r").read())[0]
        self.session = vk_api.VkApi(token=self.config["KEY"])
        self.session._auth_token()
        self.longpoll = VkLongPoll(self.session)
        if not os.path.exists("db.sqlite3"):
            self.database = db.DataBase()
            self.database.__int__()
            self.database.create_data_base_file()
            self.database.disconnect()
            self.database = None

    def start(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me and self.config["PERSONAL"]:
                    answers, keyboard = Bot().Parse(event.user_id, event.message, self.session)
                    for answer in answers:
                        self.WriteMessage(event.user_id, answer, keyboard)

    def WriteMessage(self, user_id, message, keyboard='{}'):
        self.session.method('messages.send',
                            {'user_id': user_id, 'message': message, 'random_id': random.random() * 1000,
                             'keyboard': keyboard})

if __name__ == "__main__":
    if os.path.exists("config/config.json"):
        daemon = Program()
        daemon.__int__()
        daemon.start()
    else:
        exit(1)
