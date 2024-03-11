from interactions import (
	slash_command,
	slash_option,
	SlashContext,
	OptionType,
	User,
	Extension,
)
import interactions

class TestErrExt(Extension):
	@slash_command(name='testerror', description='Test Error Handling', scopes=[931930956284178512])
	async def testerror(self, ctx: SlashContext):
		raise Exception

def setup(bot):
	TestErrExt(bot)