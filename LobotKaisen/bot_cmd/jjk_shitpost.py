from interactions import (
	slash_command,
	slash_option,
	SlashCommand,
	SlashContext,
	OptionType,
	User,
	Extension,
)
import interactions

class JJKShitpostExt(Extension):
	jjk_shitpost = SlashCommand(name='jjk-shitpost', description='Includes all of the Lobotomy essentials!', scopes=[931930956284178512])

	@jjk_shitpost.subcommand(sub_cmd_name='fill-quote-a', sub_cmd_description='Are you X because you are Y, or are you Y because you are X?')
	@slash_option(name='first-insert', argument_name='first', description='The first term to insert into the template', opt_type=OptionType.STRING, required=True)
	@slash_option(name='second-insert', argument_name='second', description='The second term to insert into the template', opt_type=OptionType.STRING, required=True)
	@slash_option(name='public', description='Wether to post the generated quote publicly or not', opt_type=OptionType.BOOLEAN, required=False)
	async def fill_quote_a(self, ctx: SlashContext, first: str, second: str, public: bool):
		await ctx.send('Are you %(first)s because you are %(second)s, or are you %(second)s because you are %(first)s?' % {'first': first, 'second': second}, ephemeral=not public if public is not None else True)


def setup(bot):
	JJKShitpostExt(bot)
