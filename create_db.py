import mysql.connector
from datetime import datetime, timedelta

conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="masterDB_70"
)

cursor = conn.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS laundry_scheduler")
conn.database = "laundry_scheduler"


cursor.execute('''CREATE TABLE IF NOT EXISTS laundry (
                    date VARCHAR(20),
                    time VARCHAR(20),
                    slot1 VARCHAR(20),
                    slot2 VARCHAR(20),
                    PRIMARY KEY (date, time)
                )''')

today = datetime.now().date()
end_date = datetime(2027, 12, 31).date()

delta = timedelta(days=1)
while today <= end_date:
    cursor.execute("SELECT * FROM laundry WHERE date = %s", (today.strftime('%d.%m.%Y'),))
    existing_rows = cursor.fetchall()

    if not existing_rows:
        cursor.execute("INSERT INTO laundry VALUES (%s, %s, 'Свободно', 'Свободно')", (today.strftime('%d.%m.%Y'), '9:00-11:00'))
        cursor.execute("INSERT INTO laundry VALUES (%s, %s, 'Свободно', 'Свободно')", (today.strftime('%d.%m.%Y'), '12:00-14:00'))
        cursor.execute("INSERT INTO laundry VALUES (%s, %s, 'Свободно', 'Свободно')", (today.strftime('%d.%m.%Y'), '15:00-17:00'))
        cursor.execute("INSERT INTO laundry VALUES (%s, %s, 'Свободно', 'Свободно')", (today.strftime('%d.%m.%Y'), '18:00-20:00'))
        cursor.execute("INSERT INTO laundry VALUES (%s, %s, 'Свободно', 'Свободно')", (today.strftime('%d.%m.%Y'), '21:00-23:00'))

    today += delta


conn.commit()
conn.close()
