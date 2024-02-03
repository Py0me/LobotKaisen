import interactions
from interactions import slash_command, SlashContext
import discord
from discord import app_commands
from modules import voting

def main():
	with open('token', 'r', encoding='utf8') as tok_file:
		token = tok_file.readline().strip()

	bot = interactions.Client(token=token)

	@slash_command(name='sync', description='Owner only')
	async def sync(interaction: discord.Interaction):
		if interaction.user.id == 538770497056538624:
			# sync shit (fuck you)
			print('Command synced.')
		else:
			await interaction.response.send_message('You must be the owner to use this command!')

#	@slash_command(name="gainaccess", description="Gain Access to the Secret Chat by inviting someone!", scopes=[870046872864165888])
#	async def gainaccess(ctx: SlashContext):
#		await ctx.send("test")

	bot.start()

if __name__ == '__main__':
	exit(main())