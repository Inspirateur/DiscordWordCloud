from typing import List
import sqlite3
from discord import TextChannel
# create the DB and the table if it's not here
conn = sqlite3.connect("Management/ignored.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS IgnoredChan (guildID integer, chanID integer)")
conn.commit()
conn.close()


def ignore(chan: TextChannel):
	conn = sqlite3.connect("Management/ignored.db")
	cur = conn.cursor()
	cur.execute("INSERT INTO IgnoredChan VALUES(?, ?)", (chan.guild.id, chan.id))
	conn.commit()
	conn.close()


def unignore(chan: TextChannel):
	conn = sqlite3.connect("Management/ignored.db")
	cur = conn.cursor()
	cur.execute("DELETE FROM IgnoredChan WHERE chanID=?", (chan.id, ))
	conn.commit()
	conn.close()


def ignore_list(guildid: int) -> List[int]:
	conn = sqlite3.connect("Management/ignored.db")
	cur = conn.cursor()
	cur.execute("SELECT chanID FROM IgnoredChan WHERE guildID=?", (guildid, ))
	res = [chanid for (chanid, ) in cur.fetchall()]
	conn.close()
	return res
