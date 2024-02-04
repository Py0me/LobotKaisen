from interactions import slash_command, SlashCommand, Extension, SlashContext, OptionType
import interactions

class VoteExt(Extension):
	@slash_command(name='vote', description='Vote for the Lobotomy King/Queen', scopes=[931930956284178512])
	@slash_option(name='username', description='who are you voting for?', opt_type=OptionType.USER)
	async def vote(self, ctx: SlashContext, **kwargs):
		vote_stats_channel = ctx.guild.fetch_channel(1203409239352025209)
		# sql wizard
		await vote_stats_channel.send()
def setup(bot):
	VoteExt(bot)