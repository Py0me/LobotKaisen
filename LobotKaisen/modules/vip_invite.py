from interactions import (
	slash_command,
	slash_option,
	SlashContext,
	OptionType,
	User,
	Extension,
)
import interactions

class VIPInviteExt(Extension):
	@slash_command(name='invite', description='Invite another user to join the lobotomy and receive VIP rank for 1 week in return', scopes=[931930956284178512])
	@slash_option(name='vip_receiver', description='The user which should be rewarded with the VIP rank', opt_type=OptionType.USER, required=False)
	async def invite(self, ctx: SlashContext, vip_receiver: User):
		if vip_receiver is None:
			vip_receiver = ctx.user
		if ctx.guild.get_member(vip_receiver.id).has_role(VIP_ROLE):
			await ctx.send('VIP rank is already in effect!', ephemeral=True)
			return
		if int(vip_receiver.id) in VIP_PENDING:
			# TODO: fetch the old invite link from the database
			await ctx.send('You have already applied for the VIP queue! Here is your old invite link again: %s', ephemeral=True)
			return
		# TODO: generate invite link and insert it into the response
		await ctx.send('Here is your new invite link (max. 1 use, expires after 24 hours): %s', ephemeral=True)


def setup(bot):
	VIPInviteExt(bot)
