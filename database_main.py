import mysql.connector
from datetime import datetime, timedelta
import re


class LaundryScheduler:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='masterDB_70',
            database='laundry_scheduler'
        )
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS laundry
                               (date VARCHAR(20), time VARCHAR(20), slot1 VARCHAR(20), slot2 VARCHAR(20))''')

    @staticmethod
    def is_valid_number(value):
        try:
            valid_numbers = [str(num) for num in range(501, 539)] + ['512а'] + [str(num) for num in range(602, 639)] + [
                '612а', '628а', '902', '919', '921', '923', '925', '931']
            return value in valid_numbers
        except ValueError:
            return False

    @staticmethod
    def is_valid_date(date):
        try:
            datetime.strptime(date, '%d.%m.%Y')
            return True
        except ValueError:
            return False

    @staticmethod
    def is_past_date(date):
        current_date = datetime.now().date()
        input_date = datetime.strptime(date, '%d.%m.%Y').date()
        return input_date < current_date

    @staticmethod
    def validate_time_format(time):
        pattern = r'^\d{1,2}:\d{2}-\d{1,2}:\d{2}$'
        if re.match(pattern, time):
            return True
        return False

    @staticmethod
    def get_time_range(time):
        start_time, end_time = time.split('-')
        return start_time.strip(), end_time.strip()

    def find_available_slots(self, search_date, search_time):
        available_dates = []

        current_date = datetime.strptime(search_date, '%d.%m.%Y').date()
        end_date = current_date + timedelta(days=4)  # Check for available slots within 5 days

        while current_date <= end_date:
            current_date_str = current_date.strftime('%d.%m.%Y')

            self.cursor.execute("SELECT * FROM laundry WHERE date = %s AND time = %s", (current_date_str, search_time))
            result = self.cursor.fetchall()

            if not result:
                available_dates.append(current_date_str)
            else:
                for row in result:
                    slot1, slot2 = row[2], row[3]
                    if slot1 == "Свободно" or slot2 == "Свободно":
                        available_dates.append(current_date_str)
                        break

            current_date += timedelta(days=1)

        return available_dates

    def check_weekly_limit(self, value, search_date):
        date = datetime.strptime(search_date, '%d.%m.%Y').date()
        start_date = date - timedelta(days=date.weekday())
        week_values = self.get_week_values(start_date)

        count = 0
        for row in week_values:
            slot1, slot2 = row
            if value in [slot1, slot2]:
                count += 1
        return count >= 2

    def get_week_values(self, start_date):
        end_date = start_date + timedelta(days=6)
        query = "SELECT slot1, slot2 FROM laundry WHERE STR_TO_DATE(date, '%d.%m.%Y') BETWEEN %s AND %s"
        self.cursor.execute(query, (start_date, end_date))
        data_from_db = self.cursor.fetchall()
        return data_from_db

    def get_laundry_values(self, start_date, end_date):
        query = "SELECT * FROM laundry WHERE STR_TO_DATE(date, '%d.%m.%Y') BETWEEN %s AND %s"

        self.cursor.execute(query, (start_date, end_date))
        data_from_db = self.cursor.fetchall()

        return data_from_db

    def is_slot_available(self, search_date, search_time, slot):
        self.cursor.execute(
            "SELECT slot{0} FROM laundry WHERE date = %s AND time = %s".format(slot),
            (search_date, search_time)
        )
        result = self.cursor.fetchone()
        return result[0] == "Свободно"



