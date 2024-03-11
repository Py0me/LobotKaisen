from interactions import SlashContext, Guild, Member, Role, GuildChannel

def search_role(ctx: SlashContext, name: str) -> int:
	for role in ctx.guild.roles:
		if role.name == name:
			return int(role.id)
	return None
	
def search_rolelistid(ctx: list[Role], name: str) -> Role:
	for role in ctx:
		if role.name == name:
			return role
	return None

def search_memberid(ctx: list[Member], member_id: int) -> Member:
	for member in ctx:
		if int(member.id) == member_id:
			return member
	return None

def search_channel(ctx: SlashContext, name: str) -> int:
	for channel in ctx.guild.channels:
		if channel.name == name:
			return int(channel.id)
	return None

def search_channelid(ctx: list[GuildChannel], name: str) -> GuildChannel:
	for channel in ctx:
		if channel.name == name:
			return channel
	return None

def search_channelid2(ctx: list[GuildChannel], name: str) -> int:
	for channel in ctx:
		if channel.name == name:
			return int(channel.id)
	return None

def search_guild(ctx: list[Guild], name: str) -> Guild:
	for guild in ctx:
		if guild.name == name:
			return guild
	return None