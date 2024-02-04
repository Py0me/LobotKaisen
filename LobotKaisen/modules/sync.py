from interactions import slash_command, SlashCommand, Extension, SlashContext
import interactions

class SyncExt(Extension):
	@slash_command(name='sync', description='Owner only', scopes=[931930956284178512])
	async def sync(self, ctx: SlashContext, **kwargs):
		if  ctx.author_id == 538770497056538624:
			await ctx.send('You are the owner to use this command!',ephemeral=True)
			# sync shit (fuck you)
			print('Command synced.')
		else:
			await ctx.send('You must be the owner to use this command!',ephemeral=True)

def setup(bot):
	SyncExt(bot)