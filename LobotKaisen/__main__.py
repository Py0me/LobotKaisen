# Un fucking lucky
import interactions
from interactions import listen, PermissionOverwrite, Permissions
import logging
import time
import asyncio
import random
import json
import sys
from .db import db
from .helpers.daycmp import same_minute, same_day

if sys.platform == 'win32':
	from ctypes import windll
	kernel32 = windll.LoadLibrary('kernel32')
	# NOTE: enables support for ANSI color codes on windows
	kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

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

			if previous_time is None or not same_day(previous_time, current_time):  # NOTE: same_minute() should be replaced with same_day() in the production version
				king_id = await sql_db['bot_vars'].get_variable('king_id')

				elected_king = (await current_guild.fetch_member(king_id)) if king_id is not None else None

				if elected_king is not None:
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

	perm_over = PermissionOverwrite.for_target(await messaged_guild.fetch_role(json_obj['roles']['Lobotomy King/Queen']))
	perm_over.add_denies(Permissions.SEND_MESSAGES)
	await event.message.channel.edit_permission(perm_over)

@listen(interactions.api.events.CommandError, disable_default_listeners= True)
async def on_error(event: interactions.api.events.CommandError):
	json_db = await db.JSONConnection('db/servers.json')
	json_obj = json_db.get_json(event.ctx.guild.id)

	dev_role = None if json_obj is None else json_obj['roles']['Developer']

	try:
		raise event.error
	except Exception as tb:
		event.bot.logger.exception(tb)

	await event.ctx.send(
		'Wowzers! Something went wrong on our side. Sorry for that.\n'
		'%s. Happy Lobotomizing!' %
		(('Try again later or ask a <@&%s>' % dev_role) if dev_role is not None else 'Try again later or open a new issue [here](https://github.com/Py0me/LobotKaisen/issues)'),
		ephemeral=True
	)

def main():
	cls_log = logging.getLogger('LogKaisen')
	cls_log.setLevel(logging.DEBUG)

	ANSI = '\033[%dm'
	ANSI_NUL = ANSI % 0
	ANSI_RED = ANSI % 31
	ANSI_GRN = ANSI % 32
	ANSI_YEL = ANSI % 33
	ANSI_BLU = ANSI % 34

	log_formatter = logging.Formatter('[%(asctime)s] %(name)s##%(levelname)s: %(message)s')
	log_ansi_formatter = logging.Formatter('[' + ANSI_GRN + '%(asctime)s' + ANSI_NUL + '] ' + ANSI_BLU + '%(name)s' + ANSI_NUL + '##' + ANSI_RED + '%(levelname)s' + ANSI_NUL + ': %(message)s')

	log_console_handler = logging.StreamHandler()
	log_console_handler.setLevel(logging.INFO)
	log_console_handler.setFormatter(log_ansi_formatter)
	cls_log.addHandler(log_console_handler)

	log_file_handler = logging.FileHandler('lobotomy.log')
	log_file_handler.setLevel(logging.DEBUG)
	log_file_handler.setFormatter(log_formatter)
	cls_log.addHandler(log_file_handler)

	bot = interactions.Client(
		intents=interactions.Intents.DEFAULT | interactions.Intents.MESSAGE_CONTENT,
		sync_interactions=True,
		delete_unused_application_cmds=True,
		asyncio_debug=True,
		send_command_tracebacks=False,
		logger=cls_log
	)

	for ext in EXTENSION_LIST:
		bot.load_extension('.bot_cmd.%s' % ext, __package__)

	with open('token', 'r', encoding='utf8') as tok_file:
		token = tok_file.readline().strip()

	bot.start(token)

if __name__ == '__main__':
	exit(main())