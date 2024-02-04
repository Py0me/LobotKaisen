import interactions


def main():
	with open('token', 'r', encoding='utf8') as tok_file:
		token = tok_file.readline().strip()

	bot = interactions.Client(
		intents=interactions.Intents.DEFAULT | interactions.Intents.MESSAGE_CONTENT,
		sync_interactions=True,
		asyncio_debug=True,
	)

#	@slash_command(name="gainaccess", description="Gain Access to the Secret Chat by inviting someone!", scopes=[870046872864165888])
#	async def gainaccess(ctx: SlashContext):
#		await ctx.send("test")

	bot.load_extension('modules.sync')
	bot.load_extension('modules.voting')
	bot.start(token)

if __name__ == '__main__':
	exit(main())
