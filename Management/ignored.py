from typing import Dict, List
import sqlite3
from discord import TextChannel
# create the DB and the table if it's not here
connexion = sqlite3.connect("Management/ignored.db")
cursor = connexion.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS IgnoredChan (guildID integer, chanID integer)")
connexion.commit()
connexion.close()
# the cache object: <guildID, [chanID, ...]>
cache: Dict[int, List[int]] = {}


def ignore(chan: TextChannel):
	# if there's a cache for the guild
	if chan.guild.id in cache:
		# add the new channel to it
		cache[chan.guild.id].append(chan.id)
	# add the channel to the DB
	conn = sqlite3.connect("Management/ignored.db")
	cur = conn.cursor()
	cur.execute("INSERT INTO IgnoredChan VALUES(?, ?)", (chan.guild.id, chan.id))
	conn.commit()
	conn.close()


def unignore(chan: TextChannel):
	# if there's a cache for the guild
	if chan.guild.id in cache:
		# remove the new channel from it
		cache[chan.guild.id].remove(chan.id)
	# remove the channel from the DB
	conn = sqlite3.connect("Management/ignored.db")
	cur = conn.cursor()
	cur.execute("DELETE FROM IgnoredChan WHERE chanID=?", (chan.id, ))
	conn.commit()
	conn.close()


def ignore_list(guildid: int) -> List[int]:
	# if there's a cache for the guild
	if guildid in cache:
		# we return it instead of querrying the DB
		return cache[guildid]
	# there's no cache for the guild, we querry the DB
	conn = sqlite3.connect("Management/ignored.db")
	cur = conn.cursor()
	cur.execute("SELECT chanID FROM IgnoredChan WHERE guildID=?", (guildid, ))
	res = [chanid for (chanid, ) in cur.fetchall()]
	conn.close()
	# update the cache
	cache[guildid] = res
	return res
