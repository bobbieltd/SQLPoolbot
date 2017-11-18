#!/usr/bin/python3
import MySQLdb
from time import sleep

db=MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")

cursor=db.cursor()
#table="users"
#cursor.execute("SELECT * FROM " + table)
cursor.execute("INSERT INTO users (name, wallet) VALUES ('trite', 'wallet')")
#msg=cursor.fetchone()
#print(str(msg[2]))

db.commit()

