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
	'Sukuna' : ('7333648534605432939',),
	'Gojo'   : ('22565583',),
	'Toji'   : ('9488810019021905520',),
	'Megumi' : ('20306105',),
	'Nobara' : ('21684978',),
	'Shoko'  : ('6843298019380912167',),
	'Todo'   : ('20911000',),
	'Mahito' : ('374772637974082172',),
	'Geto'   : ('26781155',),
	'Hakari' : ('11562479764200212001',),
	'Yuji'   : ('14791240713988465127',),
}

@listen(interactions.events.Ready)
async def on_start(event: interactions.events.Ready):
	status_iter = iter(STATUS_MSG, None)

	# TODO: replace those with connection objects (see `__main__.py:on_message()`)
	await db.init('lobotomy-db.sqlite')
	db.init_json('db/servers.json')

	async with db.db_conn.cursor() as db_cur:
		while True:
			status_msg = next(status_iter)

			if status_msg is None:
				status_iter = iter(STATUS_MSG, None)
				continue

			await event.bot.change_presence(activity=status_msg)

			previous_time = await get_botvar('last_day')
			current_time = time.time()
			json_obj = db.next_json()

			while (json_obj := db.next_json()) is not None:
				current_guild = await event.bot.fetch_guild(json_obj['id'])

				if current_guild is None:  # NOTE: if the guild fetch function fails we assume the bot is not part of the server and skip to next guild
					continue

				candidates = []

				if previous_time is None or not same_minute(previous_time, current_time):
					king_id = await get_botvar('king_id', json_obj['id'])

					if king_id is not None:
						elected_king = await current_guild.fetch_member(king_id)
						await elected_king.remove_role(json_obj['roles']['Lobotomy King/Queen'])

					# TODO: externalize this to a function
					exec_result = await db_cur.execute(
						'SELECT candidate_id FROM votes WHERE vote_count = (SELECT max(vote_count) FROM votes)'
					)

					async for row in exec_result:
						candidates.append(row[0])

				if candidates:
					elected_king = await current_guild.fetch_member(random.choice(candidates)) # FIXME: bot might crash if member leaves
					announce_channel = await current_guild.fetch_channel(json_obj['channels']['announcement'])
					royal_channel = await current_guild.fetch_channel(json_obj['channels']['royallobotomy'])

					gif_character = random.choice(tuple(ROYAL_GIFS.keys()))

					await announce_channel.send(
						'Congratulations, <@%d>, you are now the Lobotomy King/Queen for today.\n'
						'Be sure to leave a royal message for everyone to see in <#%d>!\n'
						'\n'
						'[%s is proud of you](https://tenor.com/view/%s)' %
						(elected_king.id, roayal_channel.id, gif_character, random.choice(ROYAL_GIFS[gif_character]))
					)

					perm_over = PermissionOverwrite.for_target(await current_guild.fetch_role(json_obj['roles']['Lobotomy King/Queen']))
					perm_over.add_allows(Permissions.SEND_MESSAGES)
					await royal_channel.edit_permission(perm_over)

					await set_botvar('msg_id_lobotomyking', 0, json_obj['id'])
					await elected_king.add_role(json_obj['roles']['Lobotomy King/Queen']) # in tieguild due the tiebreaker (what?????)
					await set_botvar('king_id', int(elected_king.id), json_obj['id'])

					# FIXME: may no longer drop the entire table, as that would remove all global votes (gg)
					# BEGIN FIXME BLOCK
					exec_result = await db_cur.execute( #dropz za(za) @kkkingk👑👑👑 #hashtagg frnz revloutin 🤑🤑🤑🥵 I make better videos than penguinz0 -> https://youtu.be/-WdGSqeXCA0
						'DROP TABLE votes'
					)

					with open('db/voting.sql', 'r', encoding='utf-8') as script_file:
						await db_cur.executescript(script_file.read())
					# END FIXME BLOCK

			await set_botvar('last_day', int(current_time))
			await db.db_conn.commit()
			await asyncio.sleep(10)

@listen(interactions.api.events.MessageCreate)
async def on_message(event: interactions.api.events.MessageCreate):
	# TODO: add reentrant JSON connections to avoid `next_json()` race conditions
	raise NotImplementedError('TODO: add reentrant JSON connections to avoid `next_json()` race conditions')

	# NOTE: variable names here are not fixed, as the entire logic
	#       in this function block will have to be rewired in the
	#       first place (see IMPL, TODO)

	# IMPL: The function is defined to revoke SEND_MESSAGES permissions
	#       of the Lobotomy King role after the daily message has been
	#       posted to the royal channel. The rights will only be restored
	#       after the next king is elected.
	messaged_guild = event.message.channel.guild
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