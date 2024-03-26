# Un fucking lucky
import interactions
from interactions import listen, PermissionOverwrite, Permissions
import logging
import time
import asyncio
import random
import json
from .db import db
from .helpers.daycmp import same_minute, same_day

EXTENSION_LIST = (
	'voting',
	'vip_invite',
	'jjk_shitpost',
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
	status_iter = iter(STATUS_MSG)

	sql_db = await db.SQLConnection('lobotomy-db.sqlite')
	await sql_db.db_init('db/setup.sql')
	json_db = await db.JSONConnection('db/servers.json')

	while True:
		status_msg = next(status_iter, None)

		if status_msg is None:
			status_iter = iter(STATUS_MSG)
			continue

		await event.bot.change_presence(activity=status_msg)

		previous_time = await sql_db['bot_vars'].get_variable('last_day', 0)
		current_time = time.time()

		for json_obj in json_db:
			sql_db.db_jump(json_obj['id'])

			current_guild = await event.bot.fetch_guild(json_obj['id'])

			if current_guild is None:  # NOTE: if the guild fetch function fails we assume the bot is not part of the server and skip to next guild
				continue

			candidates = None

			if previous_time is None or not same_minute(previous_time, current_time):  # NOTE: same_minute() should be replaced with same_day() in the production version
				king_id = await sql_db['bot_vars'].get_variable('king_id')

				if king_id is not None:
					elected_king = await current_guild.fetch_member(king_id)
					await elected_king.remove_role(json_obj['roles']['Lobotomy King/Queen'])

				candidates = await sql_db['votes'].get_election_result()

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
					(elected_king.id, royal_channel.id, gif_character, random.choice(ROYAL_GIFS[gif_character]))
				)

				perm_over = PermissionOverwrite.for_target(await current_guild.fetch_role(json_obj['roles']['Lobotomy King/Queen']))
				perm_over.add_allows(Permissions.SEND_MESSAGES)
				await royal_channel.edit_permission(perm_over)

				await sql_db['bot_vars'].set_variable('msg_id_lobotomyking', 0)
				await sql_db['bot_vars'].set_variable('king_id', elected_king.id)
				await sql_db['votes'].dispose_old_election() #dropz za(za) @kkkingk👑👑👑 #hashtagg frnz revloutin 🤑🤑🤑🥵 I make better videos than penguinz0 -> https://youtu.be/-WdGSqeXCA0

				await elected_king.add_role(json_obj['roles']['Lobotomy King/Queen']) # in tieguild due the tiebreaker (what?????)

		await sql_db['bot_vars'].set_variable('last_day', current_time, 0)
		await sql_db.commit()
		await asyncio.sleep(10)

@listen(interactions.api.events.MessageCreate)
async def on_message(event: interactions.api.events.MessageCreate):
	messaged_guild = event.message.channel.guild

	sql_db = await db.SQLConnection('lobotomy-db.sqlite')
	sql_db.db_jump(messaged_guild.id)
	json_db = await db.JSONConnection('db/servers.json')
	json_obj = json_db.get_json(messaged_guild.id)  # FIXME: verify returned value is not None

	if not (event.message.channel.id == json_obj['channels']['royallobotomy'] and event.message.author.id == await sql_db['bot_vars'].get_variable('king_id')):
		return

	perm_over = PermissionOverwrite.for_target(json_obj['roles']['Lobotomy King/Queen'])
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