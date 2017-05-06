import sqlite3
import time
import datetime
import random
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import style
style.use('fivethirtyeight')



conn = sqlite3.connect('tutorial.db')
c = conn.cursor()

def create_table():
	c.execute("CREATE TABLE IF NOT EXISTS stuffTOPlot(unix REAL, datestamp TEXT, keyword TEXT, value REAL)")


def data_entry():
	c.execute("INSERT INTO stuffToPlot VALUES(145123542, '2016-01-01', 'Python', 5)")
	conn.commit()
	c.close()
	conn.close()


def dynamic_data_entry():
	unix = time.time()
	date = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
	keyword = 'Python'
	value = random.randrange(0,10)
	c.execute("INSERT INTO stuffToPlot (unix, datestamp, keyword, value) VALUES (?, ?, ?, ?)",
		(unix, date, keyword, value))
	#musql uses %s instead of a ?
	conn.commit()


def read_from_db():
	# c.execute("SELECT * FROM stuffToPlot WHERE value=3 AND keyword='Python' ")
	# c.execute("SELECT * FROM stuffToPlot WHERE unix>1492719159.96083 AND unix<1492719163.96083 ")
	c.execute("SELECT keyword, unix FROM stuffToPlot WHERE unix>1492719159.96083 AND unix<1492719163.96083 ")
	for row in c.fetchall():
		print(row) #prints all rowns, each row is a tuple 
		print(row[0]) #will print unix, since we know the order 


def del_and_update():
	c.execute('SELECT * FROM stuffToPlot')
	c.execute('UPDATE stuffToPlot SET value=99 WHERE value=8')
	conn.commit()
	c.execute('SELECT * FROM stuffToPlot')



create_table()
data_entry()
# for i in range(10):
# 	dynamic_data_entry()
# 	time.sleep(1)
read_from_db()
c.close()
conn.close()












# def create_table():
# 	c.execute("CREATE TABLE IF NOT EXISTS stuffTOPlot(unix REAL, datestamp TEXT, keyword TEXT, value REAL)")


# def dynamic_data_entry():
# 	unix = time.time()
# 	date = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
# 	keyword = 'Python'
# 	value = random.randrange(0,10)
# 	c.execute("INSERT INTO stuffToPlot (unix, datestamp, keyword, value) VALUES (?, ?, ?, ?)",
# 		(unix, date, keyword, value))
# 	#musql uses %s instead of a ?
# 	conn.commit()


# def dBase():
# 	conn = sqlite3.connect('invoiceStorage.db')
# 	c = conn.cursor()
# 	create_table()
# 	dynamic_data_entry()
