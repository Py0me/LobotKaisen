import interactions
import logging

EXTENSION_LIST = (
	'voting',
	'vip_invite',
	#'jjk_shitpost',
)

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
