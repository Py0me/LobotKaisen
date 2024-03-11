# Un fucking lucky
import interactions
from interactions import listen, PermissionOverwrite, Permissions
import logging
import time
import asyncio
import random
import json
from .db import db
from .helpers.daycmp import same_minute
from .helpers.search import *
from .helpers.botvar import *

EXTENSION_LIST = (
	'voting',
	'vip_invite',
	'jjk_shitpost',
	'test_err',
)

STATUS_MSG = (
	'Join here: https://discord.gg/rD6JhbAPNp',
	'Lobotomizing your servers since 1987',
)

ROYAL_GIFS = {
	'sukuna' : ('7333648534605432939',),
	'gojo'   : ('22565583',),
	'toji'   : ('9488810019021905520',),
	'megumi' : ('20306105',),
	'nobara' : ('21684978',),
	'shoko'  : ('6843298019380912167',),
	'todo'   : ('20911000',),
	'mahito' : ('374772637974082172',),
	'geto'   : ('26781155',),
	'hakari' : ('11562479764200212001',),
	'yuji'   : ('14791240713988465127',),
}

@listen(interactions.events.Ready)
async def on_start(event: interactions.events.Ready):
	i = 0
	await db.init('lobotomy-db.sqlite')
	db.init_json('db/servers.json')
	async with db.db_conn.cursor() as db_cur:
		while True:
			await event.bot.change_presence(activity=STATUS_MSG[i])
			i = i + 1 if i + 1 < len(STATUS_MSG) else 0
			fetch_result = await get_botvar('last_day')
			next_time = time.time()
			json_obj = db.next_json()
			while (json_obj := db.next_json()) is not None:
				tieguild = await event.bot.fetch_guild(json_obj['id'])
				if tieguild is None:  # NOTE: if the guild fetch function fails we assume the bot is not part of the server
					continue
				candidates = []
				if fetch_result is None or not same_minute(time.gmtime(fetch_result), time.gmtime(next_time)):
					fetch_result = await get_botvar('king_id', json_obj['id'])
					if fetch_result is not None:
						tiebreaker = fetch_result
						tiemember = await tieguild.fetch_member(tiebreaker)
						await tiemember.remove_role(json_obj['roles']['Lobotomy King/Queen'])
					# TODO: externalize this to a function
					exec_result = await db_cur.execute(
						'SELECT candidate_id FROM votes WHERE vote_count = (SELECT max(vote_count) FROM votes)'
					)
					async for row in exec_result:
						candidates.append(row[0])
				if candidates:
					tiebreaker = random.choice(candidates)
					tiemember = await tieguild.fetch_member(tiebreaker) # FIXME: bot might crash if member leaves
					tiechannel = await tieguild.fetch_channel(json_obj['channels']['announcement'])
					tiechannel2 = await tieguild.fetch_channel(json_obj['channels']['royallobotomy'])
					gif = random.choice(tuple(ROYAL_GIFS.keys()))
					await tiechannel.send(
						'Congratulations, <@%d>, you are now the Lobotomy King/Queen for today.\n'
						'Be sure to leave a royal message for everyone to see in <#%d>!\n'
						'\n'
						'[%s is proud of you](https://tenor.com/view/%s)' %
						(tiemember.id, tiechannel2.id, gif, random.choice(ROYAL_GIFS[gif]))
					)
					perm_over = PermissionOverwrite.for_target(await tieguild.fetch_role(json_obj['roles']['Lobotomy King/Queen']))
					perm_over.add_allows(Permissions.SEND_MESSAGES)
					await tiechannel2.edit_permission(perm_over)
					await set_botvar('msg_id_lobotomyking', 0, json_obj['id'])
					await tiemember.add_role(json_obj['roles']['Lobotomy King/Queen']) # in tieguild due the tiebreaker (what?????)
					await set_botvar('king_id', int(tiemember.id), json_obj['id'])

					# FIXME: may no longer drop the entire table, as that would remove all global votes (gg)
					exec_result = await db_cur.execute( #dropz za(za) @kkkingk👑👑👑 #hashtagg frnz revloutin 🤑🤑🤑🥵 I make better videos than penguinz0 -> https://youtu.be/-WdGSqeXCA0
						'DROP TABLE votes'
					)
					with open('db/voting.sql', 'r', encoding='utf-8') as script_file:
						await db_cur.executescript(script_file.read())
			await set_botvar('last_day', int(next_time))
			await db.db_conn.commit()
			await asyncio.sleep(10)

@listen(interactions.api.events.MessageCreate)
async def on_message(event: interactions.api.events.MessageCreate):
	# TODO: add reentrant JSON connections to avoid `next_json()` race conditions

	guild = search_guild(event.bot.guilds, 'Bot Development')
	tuple2 = (int(event.message.channel.id), search_channelid(guild.channels, 'royallobotomy'), int(event.message.author.id), await get_botvar('king_id'))
	event.bot.logger.debug('channel_id: %d; guild.channels: %s; author_id: %d; king_id: %d' % tuple2)
	if not (tuple2[0] == tuple2[1] and tuple2[2] == tuple2[3]):
		return
	event.bot.logger.debug('Removing royal permissions')
	perm_over = PermissionOverwrite.for_target(search_rolelistid(guild.roles, 'Lobotomy King/Queen of the Day'))
	perm_over.add_denies(Permissions.SEND_MESSAGES)
	await event.message.channel.edit_permission(perm_over)

@listen(interactions.api.events.CommandError, disable_default_listeners= True)
async def on_error(event: interactions.api.events.CommandError):
	await event.ctx.send('Wowzers! Something went wrong on our side. Sorry for that. Try again later or ask a <@&1208851554850045982>. Happy Lobotomizing!', ephemeral=True)

def main():
	logging.basicConfig()
	cls_log = logging.getLogger('LogKaisen')
	cls_log.setLevel(logging.DEBUG)

	bot = interactions.Client(
		intents=interactions.Intents.DEFAULT | interactions.Intents.MESSAGE_CONTENT,
		sync_interactions=True,
		asyncio_debug=True,
		logger=cls_log
	)

	for ext in EXTENSION_LIST:
		bot.load_extension('.bot_cmd.%s' % ext, __package__)

	with open('token', 'r', encoding='utf8') as tok_file:
		token = tok_file.readline().strip()

	bot.start(token)

if __name__ == '__main__':
	exit(main())