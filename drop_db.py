import MySQLdb


db = MySQLdb.connect("localhost","root","masterDB_70")
cursor = db.cursor()

cursor.execute("DROP DATABASE laundry_scheduler")

print('Database dropped');

db.close()

