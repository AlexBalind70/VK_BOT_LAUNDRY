# -*- coding: utf-8 -*-

import mysql.connector

class PositionUser:
    def __init__(self):
        # self.laundry_db = LaundryScheduler()

        self.conn_position = mysql.connector.connect(
            host='localhost',
            port='3306',
            user='root',
            password='masterDB_70',
            database='position_user'
        )
        self.cursor_position = self.conn_position.cursor()
        self.cursor_position.execute('CREATE DATABASE IF NOT EXISTS position_user')
        self.create_new_table()

    def create_new_table(self):
        self.cursor_position.execute('''CREATE TABLE IF NOT EXISTS position_user (iduser VARCHAR(20),room VARCHAR(5), station VARCHAR(5),ban VARCHAR(5),
                                        PRIMARY KEY (iduser))''')

    def user_exists(self, id_user):
        sql_promt = 'SELECT iduser FROM position_user WHERE iduser = %s'
        self.cursor_position.execute(sql_promt, (id_user,))
        user = self.cursor_position.fetchone()
        return user is not None

    def add_new_user(self, id_user):
        if not self.user_exists(id_user):
            sql_promt = 'INSERT INTO position_user(iduser, room, station, ban) VALUES (%s, %s, %s, %s)'
            self.cursor_position.execute(sql_promt, (id_user, "0", "1", "0"))
            self.conn_position.commit()
        else:
            pass

        return

    def delete_user(self, id_user):
        sql_promt = "DELETE from position_user WHERE iduser = %s"
        self.cursor_position.execute(sql_promt, (id_user,))
        self.conn_position.commit()

    def update_position(self, id_user, new_position):
        sql_promt = 'UPDATE position_user SET station = %s WHERE iduser = %s'
        self.cursor_position.execute(sql_promt, (new_position, id_user))
        self.conn_position.commit()

        return

    def update_ban(self, id_user, ban):
        sql_promt = 'UPDATE position_user SET ban = %s WHERE iduser = %s'
        self.cursor_position.execute(sql_promt, (ban, id_user))
        self.conn_position.commit()

        return


    def take_position(self, id_user):
        sql_promt = 'SELECT station FROM position_user WHERE iduser = %s'
        self.cursor_position.execute(sql_promt, (id_user,))
        line = self.cursor_position.fetchone()

        if line is None:
            return_count = 0
        else:
            return_count = line[0]
        self.conn_position.commit()

        return return_count

    def take_ban(self, id_user):
        sql_promt = 'SELECT ban FROM position_user WHERE iduser = %s'
        self.cursor_position.execute(sql_promt, (id_user,))
        count_ban = self.cursor_position.fetchone()
        count_ban = count_ban[0]
        self.conn_position.commit()

        return count_ban

    def update_room(self, id_user, value_room):
        take_room = self.take_room(id_user)
        if take_room == "0":
            sql_promt = 'UPDATE position_user SET room = %s WHERE iduser = %s'
            self.cursor_position.execute(sql_promt, (value_room, id_user))
        else:
            pass
        self.conn_position.commit()

        return

    def change_room(self, id_user, room):
        sql_promt = 'UPDATE position_user SET room = %s WHERE iduser = %s'
        self.cursor_position.execute(sql_promt, (room, id_user))
        self.conn_position.commit()

        return

    def take_room(self, id_user):
        sql_promt = 'SELECT room FROM position_user WHERE iduser = %s'
        self.cursor_position.execute(sql_promt, (id_user,))
        line = self.cursor_position.fetchone()
        return_room = line[0]
        self.conn_position.commit()

        return return_room

    def display_all_users(self):
        self.cursor_position.execute('SELECT * FROM position_user')
        all_users = self.cursor_position.fetchall()
        if all_users:
            for user in all_users:
                user_id = user[0]
                value_room = user[1]
                value_position = user[2]
        else:
            pass











