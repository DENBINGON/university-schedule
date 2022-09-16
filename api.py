import requests
import json

class Api:

    URL = "https://files.ruslansoloviev.ru/groups/"

    days = [
        'Воскресенье',
        'Понедельник',
        'Вторник',
        'Среда',
        'Четверг',
        'Пятница',
        'Суббота'
    ]
    days_have_not_pairs = [
        'В воскресенье',
        'В понедельник',
        'Во вторник',
        'В среду',
        'В четверг',
        'В пятницу',
        'В субботу'
    ]

    def check_group(self, findable_group):
        depends_array = json.loads(self.get_json("", 1))
        for depend in depends_array:
            if findable_group in depend['groups']:
                return True
        return False

    def get_depend_code(self, group):
        depends_array = json.loads(self.get_json("", 1))
        for depend in depends_array:
            if group in depend['groups']:
                return depend['code']
        return None

    def get_schedule_today(self, group, day, even):
        return  self.get_schedule_on_date(group, day, even)

    def get_schedule_tomorrow(self, group, day, even):
        return  self.get_schedule_on_date(group, day, even)

    def get_schedule_week(self, group, even):
        compaired = ""
        weeks_array = json.loads(self.get_json(group))
        this_week = weeks_array[even - 1]['schedule']
        for day in this_week:
            compaired += self.get_pairs(day)
        return compaired

    def get_pairs(self, day):
        compaired = ""
        if not day == [{'day': None, 'pairs': None}]:
            pair_con = 0
            compaired += day['day'].upper() + ":\n\n"
            for pair in day['pairs']:
                pair_con += 1
                compaired += f"[{pair_con}] {pair['title']} - {pair['type']}\n" \
                             f"> {pair['time']}\n> Аудитория: {pair['classroom']}\n" \
                             f"> {pair['teacher']}\n" \
                             f"> {pair['period']}\n" \
                             f"------\n"
            compaired = compaired[:-7] + "\n"
        return compaired

    def get_schedule_on_date(self, group, date, even):
        try:
            day_name = self.days[date]
            if even == 0: even = 2
            for day in json.loads(self.get_json(group))[even - 1]['schedule']:
                try:
                    if day['day'] == day_name:
                        return self.get_pairs(day)
                except:pass
        except:
            pass

        return f"{self.days_have_not_pairs[date]} пар нет"

    def get_json(self, group, type = 0):
        # types: 0 -> schedule; 1 -> groups.json
        if type == 0 :
            return requests.get(f"{self.URL}{self.get_depend_code(group)}/{group}.json").text
        else:
            return requests.get(f"{self.URL}groups.json").text

