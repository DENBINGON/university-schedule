
from config import Keyboards
import random
import db
import validate
import messages
import api
import pendulum

class Bot:
    database = db.DataBase()
    user_id = None
    session = None
    commands_main = ["РАСПИСАНИЕ", "НАСТРОЙКИ", "ИНФОРМАЦИЯ", "ПРЕПОДАВАТЕЛЬ"]
    commands_rasp = ["СЕГОДНЯ", "ЗАВТРА", "НЕДЕЛЯ", "ДАТА", "НАЗАД", "ДЕНЬ НЕДЕЛИ"]
    commands_week = ["ЧЕТНАЯ", "НЕЧЕТНАЯ", "НАЗАД", "В МЕНЮ"]
    commands_info = ["О БОТЕ", "КОМАНДЫ", "НАЗАД"]
    commands_sett = ["ИЗМЕНИТЬ ГРУППУ", "НАЗАД"]
    commands_days = ["", "ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА", "СУББОТА"]

    def Parse(self, user_id, msg, session):
        self.session = session
        date = pendulum.now("Europe/Moscow")
        msg = msg.upper()
        _api = api.Api()
        answer = messages.dont_know
        keyboard = "{}"
        # If user doesnt exist in database
        if not self.database.check_user(user_id):
            user_info = self.get_user_information(user_id)[0]
            try:
                self.database.add_user(user_id, user_info['first_name'],
                                       user_info['last_name'], user_info['bdate'],
                                       user_info['sex'], user_info['country'],
                                       user_info['city'], user_info['verified'], last_activity="ENTGRP")
            except:
                self.database.add_user(user_id, user_info['first_name'],
                                       user_info['last_name'], 'bdate',
                                       user_info['sex'], {'id': 1, 'title': 'Россия'},
                                       {'id': 72, 'title': 'Краснодар'}, user_info['verified'], last_activity="ENTGRP")

            return [messages.hello(self.database.get_user_info(user_id, 'name')), messages.welcome, messages.edit_group], keyboard
        # Get last activity
        last_activity = self.database.check_activity(user_id)
        # If user must to add group id
        if last_activity == "ENTGRP":
            if validate.group_validate(msg):
                self.database.edit_user(user_id, 'user_group', msg)
                self.database.edit_user(user_id, 'last_activity', "MAIN")
                return [messages.success_group + msg, messages.to_main], Keyboards.main
            else:
                return [messages.unknown_group_code], '{}'

        # FUNCTIONS DOWN WRITABLE

        # MAIN VIEW
        # To schedule
        if last_activity == "MAIN" and msg == self.commands_main[0]:
            self.database.edit_user(user_id, 'last_activity', "RASP")
            return [messages.to_rasp], Keyboards.schedule_main
        # To settings
        if last_activity == "MAIN" and msg == self.commands_main[1]:
            self.database.edit_user(user_id, 'last_activity', "SETT")
            return [messages.to_sett], Keyboards.settings
        # To information
        if last_activity == "MAIN" and msg == self.commands_main[2]:
            self.database.edit_user(user_id, 'last_activity', "INFO")
            return [messages.to_info], Keyboards.info
        # To teachers
        if last_activity == "MAIN" and msg == self.commands_main[3]:
            self.database.edit_user(user_id, 'last_activity', "FINDTEAC")
            return [messages.teacher_main], Keyboards.clear
        if last_activity == "MAIN":
            return  [answer], Keyboards.main

        # INFORMATION VIEW
        # About this bot
        if last_activity == "INFO" and msg == self.commands_info[0]:
            return [messages.about_bot], Keyboards.info
        # About bot commands
        if last_activity == "INFO" and msg == self.commands_info[1]:
            return [messages.about_bot_commands], Keyboards.info
        # Return
        if last_activity == "INFO" and msg == self.commands_info[2]:
            self.database.edit_user(user_id, 'last_activity', "MAIN")
            return [messages.to_main], Keyboards.main
        if last_activity == "INFO":
            return  [answer], Keyboards.info

        # SETTINGS VIEW
        # Update user group
        if last_activity == "SETT" and msg == self.commands_sett[0]:
            self.database.edit_user(user_id, 'last_activity', "ENTGRP")
            return [messages.edit_group], Keyboards.clear
        # Return
        if last_activity == "SETT" and msg == self.commands_sett[1]:
            self.database.edit_user(user_id, 'last_activity', "MAIN")
            return [messages.to_main], Keyboards.main
        if last_activity == "SETT":
            return  [answer], Keyboards.settings

        # TEACHERS VIEW
        if last_activity == "FINDTEAC":
            self.database.edit_user(user_id, 'last_activity', "GETTEACRASP")
            return [messages.teacher_select], _api.get_teachers_on_keyboard(msg)


        # SCHEDULE VIEW
        # Today
        if last_activity == "RASP" and msg == self.commands_rasp[0]:
            return [_api.get_schedule_today(self.database.get_user_group(user_id),
                                           date.day_of_week,
                                           date.week_of_year%2)], Keyboards.schedule_main
        # Tomorrow
        if last_activity == "RASP" and msg == self.commands_rasp[1]:
            date = date.add(days=1)
            return [_api.get_schedule_tomorrow(self.database.get_user_group(user_id),
                                              date.day_of_week,
                                              date.week_of_year%2)], Keyboards.schedule_main
        # Week
        if last_activity == "RASP" and msg == self.commands_rasp[2]:
            self.database.edit_user(user_id, 'last_activity', "EVEN")
            return [messages.select_even, f"Сейчас {'четная' if date.week_of_year%2 == 0 else 'нечетная'} неделя"], Keyboards.schedule_even
        # Date
        if last_activity == "RASP" and msg == self.commands_rasp[3]:
            return ["Будет позднее..."], Keyboards.schedule_main
        # Return
        if last_activity == "RASP" and msg == self.commands_rasp[4]:
            self.database.edit_user(user_id, 'last_activity', "MAIN")
            return [messages.to_main], Keyboards.main
        # Week day select
        if last_activity == "RASP" and msg == self.commands_rasp[5]:
            self.database.edit_user(user_id, 'last_activity', "DAYS")
            return  [messages.to_week_day_select], Keyboards.schedule_days
        if last_activity == "RASP":
            return  [answer], Keyboards.schedule_main

        # SCHEDULE EVEN VIEW
        # Even
        if last_activity == "EVEN" and msg == self.commands_week[0]:
            rasp = _api.get_schedule_week(self.database.get_user_group(user_id), 2)
            self.database.edit_user(user_id, 'last_activity', "MAIN")
            return [rasp], Keyboards.main
        # Odd
        if last_activity == "EVEN" and msg == self.commands_week[1]:
            rasp = _api.get_schedule_week(self.database.get_user_group(user_id), 1)
            self.database.edit_user(user_id, 'last_activity', "MAIN")
            return [rasp], Keyboards.main
        # Return
        if last_activity == "EVEN" and msg == self.commands_week[2]:
            self.database.edit_user(user_id, 'last_activity', "RASP")
            return [messages.to_rasp], Keyboards.schedule_main
        # To main
        if last_activity == "EVEN" and msg == self.commands_week[3]:
            self.database.edit_user(user_id, 'last_activity', "MAIN")
            return [messages.to_main], Keyboards.main
        if last_activity == "EVEN":
            return  [answer], Keyboards.schedule_even

        # SCHEDULE WEEK DAYS SELECT VIEW
        # Select
        if last_activity == "DAYS" and msg in self.commands_days:
            self.database.edit_user(user_id, 'last_activity', f"DAEV{self.commands_days.index(msg)}")
            return [messages.select_even, f"Сейчас {'четная' if date.week_of_year%2 == 0 else 'нечетная'} неделя"], Keyboards.schedule_even
        # Return
        if last_activity == "DAYS" and msg == self.commands_week[2]:
            self.database.edit_user(user_id, 'last_activity', "RASP")
            return [messages.to_rasp], Keyboards.schedule_main
        # To main
        if last_activity == "DAYS" and msg == self.commands_week[3]:
            self.database.edit_user(user_id, 'last_activity', "MAIN")
            return [messages.to_main], Keyboards.main
        if last_activity == "DAYS":
            return  [answer], Keyboards.schedule_days

        # DAYS WEEK SELECT VIEW
        # Even
        if last_activity[:4] == "DAEV" and msg == self.commands_week[0]:
            rasp = _api.get_schedule_on_date(self.database.get_user_group(user_id), int(last_activity[-1]), 2)
            self.database.edit_user(user_id, 'last_activity', "DAYS")
            return [rasp], Keyboards.schedule_days
        # Odd
        if last_activity[:4] == "DAEV" and msg == self.commands_week[1]:
            rasp = _api.get_schedule_on_date(self.database.get_user_group(user_id), int(last_activity[-1]), 1)
            self.database.edit_user(user_id, 'last_activity', "DAYS")
            return [rasp], Keyboards.schedule_days
        # Return
        if last_activity[:4] == "DAEV" and msg == self.commands_week[2]:
            self.database.edit_user(user_id, 'last_activity', "DAYS")
            return [messages.to_rasp], Keyboards.schedule_days
        # To main
        if last_activity[:4] == "DAEV" and msg == self.commands_week[3]:
            self.database.edit_user(user_id, 'last_activity', "MAIN")
            return [messages.to_main], Keyboards.main
        if last_activity[:4] == "DAEV":
            return [answer], Keyboards.schedule_even

        # ANY WAY EXIT
        return [answer], keyboard

    def get_user_information(self, user_id):
        return self.session.method('users.get',
                                   {'user_id': user_id, 'random_id': random.random() * 1000,
                                    'fields': 'bdate, sex, country, city, verified'})

    def reformat_schedule_to_message(self, period):
        return period

