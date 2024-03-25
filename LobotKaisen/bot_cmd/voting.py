from interactions import (
	slash_command,
	slash_option,
	SlashContext,
	OptionType,
	User,
	Extension,
)
import interactions
from time import time
from ..db import db
from ..helpers.daycmp import same_day

DEVELOPER_IDS = (
	760876025830703185, # rgwy
	538770497056538624, # pyome
)

class VoteExt(Extension):
	@slash_command(name='vote', description='Vote for the next Lobotomy King/Queen')
	@slash_option(name='candidate', description='The server member you want to vote for', opt_type=OptionType.USER, required=True)
	async def vote(self, ctx: SlashContext, candidate: User):
		await ctx.defer(ephemeral=True)

		json_db = await db.JSONConnection('db/servers.json')
		json_obj = json_db.get_json(ctx.guild.id)

		if json_obj is None:
			await ctx.send(
				'This server does not support the requested feature!\n'
				'Please open a new issue [here](https://github.com/Py0me/LobotKaisen/issues) with the ID and name of the current server.'
			)
			return

		sql_db = await db.SQLConnection('lobotomy-db.sqlite')
		sql_db.db_jump(json_obj['id'])

		vote_timestamp = await sql_db['votes'].get_timestamp(ctx.user.id)
		current_time = time()

		if vote_timestamp is not None and same_day(vote_timestamp, current_time) and ctx.user.id not in DEVELOPER_IDS:
			await ctx.send('You have already used your daily vote! Vote again tomorrow!', ephemeral=True)
			return

		await sql_db['votes'].submit_vote(candidate.id, ctx.user.id, current_time)

		announce_channel = await ctx.guild.fetch_channel(json_obj['channels']['announcement'])

		lb_candidates = await sql_db['votes'].get_leaderboard(15)
		lb_info = []
		name_max = 0

		LB_COLORS = (33, 37, 31)

		for rank, candidate_info in enumerate(lb_candidates):
			info_obj = {
				    'color' : LB_COLORS[rank] if rank <= len(LB_COLORS) else 34,
				     'rank' : rank + 1,
				'candidate' : (await ctx.guild.fetch_member(candidate_info[0])).display_name,
				    'votes' : candidate_info[1],
			}

			if (name_len := len(info_obj['candidate'])) > name_max:
				name_max = name_len

			lb_info.append(info_obj)

		leaderboard = (
			'Top 15 Candidates for <@&%d>:\n'
			'```ansi\n'
			'%s\n'
			'```\n'
			'Vote for your own candidate in <#%d>'
		) % (
			json_obj['roles']['Lobotomy King/Queen'],
			'\n'.join([(
				'\033[%(color)dm  %(rank)2d. %(candidate)-' + str(name_max) + 's : %(votes)d Votes'
			) % info_obj for info_obj in lb_info]),
			json_obj['channels']['voting']
		)

		msg_id = await sql_db['bot_vars'].get_variable('msg_id_lobotomyking')
		vote_msg = None

		if msg_id is not None:
			vote_msg = await announce_channel.fetch_message(msg_id)
		if vote_msg is not None:
			await vote_msg.edit(content=leaderboard)
		else:
			vote_msg = await announce_channel.send(leaderboard)
			await sql_db['bot_vars'].set_variable('msg_id_lobotomyking', vote_msg.id)

		await ctx.send('Your vote for <@%d> has been submitted' % candidate.id, ephemeral=True)

def setup(bot):
	VoteExt(bot)