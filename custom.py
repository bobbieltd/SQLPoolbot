#!/usr/bin/python3
import json
import re
from datetime import datetime
import requests


# MYSQL
import MySQLdb

import ch

apiUrlXMR = "https://supportxmr.com/api/"

def prettyTimeDelta(seconds):
  seconds = int(seconds)
  days, seconds = divmod(seconds, 86400)
  hours, seconds = divmod(seconds, 3600)
  minutes, seconds = divmod(seconds, 60)
  if days > 0:
      return '%dd %dh' % (days, hours)
  elif hours > 0:
      return '%dh %dm' % (hours, minutes)
  elif minutes > 0:
      return '%dm %ds' % (minutes, seconds)
  else:
      return '%ds' % (seconds,)

class bot(ch.RoomManager):
  _lastFoundBlockNum = 0
  _lastFoundBlockLuck = 0
  _lastFoundBlockValue = 0
  _lastFoundBlockTime = 0
  NblocksNum = 0
  NblocksAvg = 0
  Nvalids = 0

  def onInit(self):
    self.setNameColor("CC6600")
    self.setFontColor("000000")
    self.setFontFace("0")
    self.setFontSize(11)

  def onConnect(self, room):
    print("Connected")
     
  def onReconnect(self, room):
    print("Reconnected")
     
  def onDisconnect(self, room):
    print("Disconnected")
    for room in self.rooms:
      room.reconnect()
    room.message("Warning: self-destruction cancelled. Systems online")

  def onMessage(self, room, user, message):

    if self.user == user: return

    try: 
      cmds = ['/triteregister', '/triteremove', '/tritelog', '/triteshow', '/trite']
      hlps = ['?triteregister', '?triteremove', '?tritelog', '?triteshow', '?trite']
      searchObj = re.findall(r'(\/\w+)(\.\w+)?|(\?\w+)', message.body, re.I)
      searchObjCmd = []
      searchObjArg = []
      searchObjArg2 = []
      searchObjHlp = []
      for i in range(len(searchObj)):
        for j in range(len(cmds)):
          if searchObj[i][0] == cmds[j]:
            searchObjCmd.append(searchObj[i][0])
            searchObjArg.append(searchObj[i][1])
            #searchObjArg2.append(searchObj[i][2])
        if searchObj[i][2]:
          searchObjHlp.append(searchObj[i][2])
      command = searchObjCmd
      argument = searchObjArg
      #argument2 = searchObjArg2
      helper = searchObjHlp
    except:
      room.message("I dont know what to do. ".format(user.name))

    for i in range(len(helper)):
      hlp = helper[i]
      if hlp in hlps:
        hlp = hlp[1:]

        if hlp.lower() == "triteregister":
            room.message("Usage (/command): triteregister.wallet")

        if hlp.lower() == "triteremove":
            room.message("Usage (/command): triteremove")

        if hlp.lower() == "tritelog":
            room.message("Usage (/command): tritelog")

        if hlp.lower() == "tritereshow":
            room.message("Usage (/command): triteshow")

        if hlp.lower() == "trite":
            room.message("Usage (/command): (?command)")
            
    for i in range(len(command)):
      cmd = command[i]
      arg = argument[i]
      #arg2 = argument2[i]
      cmd = cmd[1:]
      arg = arg[1:]
      #arg2 = arg2[1:]

      try:
        
        if cmd.lower() == "triteregister":
          chatango_nick = user.name
          pattern = re.compile("^(Anon[0-9]+)")
          if pattern.match(chatango_nick):
            room.message("Please log in to Chatango before trying to register with me.")
            break
          db=MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
          cursor = db.cursor()
          cursor.execute("SELECT EXISTS(SELECT name FROM users WHERE name='" + chatango_nick + "')")
          output=cursor.fetchone()
          #print(str(output[0]), "Check name against chatango_nick")
          #cursor.close()
          if output[0] == 1:
            room.message("You already have an account.")
            #print(str("already exists"))
          elif output[0] == 0:
            db = MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
            cursor = db.cursor()
            #print(str("Trying to INSERT INTO db."))
            cursor.execute("INSERT INTO users (name, wallet) VALUES ('" + chatango_nick + "', '" + arg + "')")
            db.commit()
            room.message("You have been registered.")
            #cursor.close()
          #print(str(chatango_nick), str(arg))
          cursor.close()

        if cmd.lower() == "triteremove":
          chatango_nick = user.name
          pattern = re.compile("^(Anon[0-9]+)")
          if pattern.match(chatango_nick):
            room.message("Please log in to Chatango before trying to register with me.")
            break
          db=MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
          cursor = db.cursor()
          cursor.execute("SELECT id FROM users WHERE name='" + chatango_nick + "'")
          output=cursor.fetchone()
          id=output[0]
          cursor.close()
          db=MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
          cursor = db.cursor()
          cursor.execute("DELETE FROM data WHERE uid='" + str(id) + "'")
          db.commit()
          cursor.close()
          db = MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
          cursor = db.cursor()
          cursor.execute("DELETE FROM users WHERE name='" + chatango_nick + "'")
          db.commit()
          room.message("Your user has been removed.")
          cursor.close()

        if cmd.lower() == "tritelog":
          chatango_nick = user.name
          db = MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
          cursor = db.cursor()
          cursor.execute("SELECT EXISTS(SELECT name FROM users WHERE name='" + chatango_nick + "')")
          output = cursor.fetchone()
          #print(str(output[0]), "Check name against chatango_nick")
          if output[0] == 1:
            cursor.close()
            db = MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
            cursor = db.cursor()
            cursor.execute("SELECT id FROM users WHERE name='" + chatango_nick + "'")
            output = cursor.fetchone()
            userID=output[0]
            cursor.close()
            time = datetime.now()
            time = time.strftime('%Y-%m-%d %H:%M:%S')
            db = MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
            cursor = db.cursor()
            cursor.execute("SELECT wallet FROM users WHERE name='" + chatango_nick + "'")
            output = cursor.fetchone()
            wallet= str(output[0])
            xmrWalletAPI = requests.get(apiUrlXMR + "miner/" + wallet + "/stats").json()
            shares = xmrWalletAPI['validShares']
            #print(str(shares), str(wallet))
            cursor.close()
            db = MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
            cursor = db.cursor()
            cursor.execute("INSERT INTO data (uid, shares, time) VALUES ('" + str(userID) + "', '" + str(shares) + "', '" + str(time) + "')")
            db.commit()
            room.message("Logged shares and time.")
          elif output[0] == 0:
            room.message("You are not registered.")
          cursor.close()

        if cmd.lower() == "triteshow":
          chatango_nick = user.name
          db=MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
          cursor = db.cursor()
          try:
            cursor.execute("SELECT id FROM users WHERE name='" + chatango_nick + "'")
          except:
            room.message("It seems you are not registered.")
            break
          output=cursor.fetchone()
          try:
            uid=output[0]
          except:
            room.message("It seems you are not registered.")
            break
          cursor.close()
          db = MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
          cursor = db.cursor()
          cursor.execute("SELECT * FROM data WHERE uid='" + str(uid) + "'")
          msg = "Showing logged shares for @" + chatango_nick + ":\n"
          for row in cursor.fetchall():
            msg = msg + "ID: " + str(row[1]) + " Shares: " + str(row[2]) + " Time: " + str(row[3]) + "\n"
          room.message(str(msg))
          cursor.close()

        if cmd.lower() == "trite":
          room.message("Commands (?,/): trite, triteregister, tritelog, triteremove, triteshow.")


      except json.decoder.JSONDecodeError:
        print("There was a json.decoder.JSONDecodeError while attempting /" + str(cmd.lower()) + " (probably due to /pool/stats/)")
        room.message("JSON Bourne is trying to kill me!")
      #except:
      #  print("Error while attempting /" + str(cmd.lower()))
      #  room.message("Main Cmd/Msg Function Except.")

rooms = ["supportxmr"]
username = "trite2k2"
password = ""

try:
  bot.easy_start(rooms,username,password)
except KeyboardInterrupt:
  print("\nStopped")
