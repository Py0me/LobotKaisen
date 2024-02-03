from interactions import slash_command, SlashCommand, Extension
import interactions

class SyncExt(Extension):
	@slash_command(name='sync', description='Owner only', scopes=931930956284178512)
	async def sync(self, interaction: interactions.Interaction):
		if interaction.user.id == 538770497056538624:
			# sync shit (fuck you)
			print('Command synced.')
		else:
			await interaction.response.send_message('You must be the owner to use this command!')

def setup(bot):
	SyncExt(bot)