import MySQLdb


db = MySQLdb.connect("localhost","root","")
cursor = db.cursor()

cursor.execute("DROP DATABASE laundry_scheduler")

print('Database dropped');

db.close()

