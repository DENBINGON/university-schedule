import sqlite3


class DataBase:
    connection = None
    cursor = None

    def __int__(self):
        self.connection = sqlite3.connect("db.sqlite3")
        self.cursor = self.connection.cursor()

    def check_user(self, user_id):
        if self.cursor.execute(f"SELECT * FROM users WHERE user_id={user_id}").fetchall() == []:
            return False
        else:
            return True

    def check_group(self, user_id):
        if self.cursor.execute(f"SELECT user_group FROM users WHERE user_id={user_id}").fetchall()[0][3] == '':
            return False
        else: return True

    def check_activity(self, user_id):
        return self.cursor.execute(f"SELECT last_activity FROM users WHERE user_id={user_id}").fetchall()[0][0]

    def add_user(self, user_id, name, surname, bdate, sex, country, city, verified, group="", last_activity=""):
        self.cursor.execute(f"INSERT INTO users VALUES ({user_id}, '{name}', '{surname}', '{group}', '{last_activity}',"+
                            f" '{bdate}', {sex}, {country['id']}, '{country['title']}', {city['id']}," +
                            f" '{city['title']}', {verified})")
        self.connection.commit()

    def get_user_group(self, user_id):
        return self.cursor.execute(f"SELECT user_group FROM users WHERE user_id={user_id}").fetchall()[0][0]

    def get_user_info(self, user_id, select_param):
        return self.cursor.execute(f"SELECT {select_param} FROM users WHERE user_id={user_id}")

    def remove_user(self, user_id):
        self.cursor.execute(f"DELETE FROM users WHERE user_id={user_id}")
        self.connection.commit()

    def edit_user(self, user_id, editable_param, new_value):
        self.cursor.execute(f"UPDATE users SET {editable_param}='{new_value}' WHERE user_id={user_id}")
        self.connection.commit()

    def create_data_base_file(self):
        self.cursor.execute(f"CREATE TABLE users (user_id INT UNIQUE, name TEXT, surname TEXT, user_group TEXT, last_activity TEXT, bdate TEXT, sex INT, country_id INT, country_title TEXT, city_id INT, city_title TEXT, verified INT)")
        self.connection.commit()

    def disconnect(self):
        self.connection.commit()
        self.connection.close()
