from interactions import (
	slash_command,
	slash_option,
	SlashContext,
	OptionType,
	User,
	Extension,
)
import interactions

class VoteExt(Extension):
	@slash_command(name='vote', description='Vote for the next Lobotomy King/Queen', scopes=[931930956284178512])
	@slash_option(name='candidate', description='The server member you want to vote for', opt_type=OptionType.USER, required=True)
	async def vote(self, ctx: SlashContext, candidate: User):
		await ctx.defer(ephemeral=True)
		vote_stats_channel = ctx.guild.get_channel(1203409239352025209)
		await vote_stats_channel.send('1 vote for %s' % candidate.display_name)
		await ctx.send('Your vote has been submitted', ephemeral=True)


def setup(bot):
	VoteExt(bot)