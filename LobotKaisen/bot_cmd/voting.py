from interactions import (
	slash_command,
	slash_option,
	SlashContext,
	OptionType,
	User,
	Extension,
)
import interactions
from time import time, gmtime
from ..db import db
from ..helpers.daycmp import same_day
from ..helpers.search import *
from ..helpers.botvar import *
from ..helpers.votes import *
from ..helpers.submitted_votes import *

class VoteExt(Extension):
	@slash_command(name='vote', description='Vote for the next Lobotomy King/Queen', scopes=[931930956284178512])
	@slash_option(name='candidate', description='The server member you want to vote for', opt_type=OptionType.USER, required=True)
	async def vote(self, ctx: SlashContext, candidate: User):
		await ctx.defer(ephemeral=True)
		await db.init('lobotomy-db.sqlite')
		async with db.db_conn.cursor() as db_cur:
			exec_result = await db_cur.execute(
				'SELECT vote_timestamp FROM submitted_votes WHERE voter_id = ?',
				(int(ctx.user.id),)
			)
			fetch_result = await exec_result.fetchone()
			if fetch_result is not None and same_day(gmtime(fetch_result[0]), gmtime()) and ctx.user.id not in (760876025830703185, 538770497056538624):
				await ctx.send('You have already used your daily vote! Vote again tomorrow!', ephemeral=True)
				return
			exec_result = await update_votes(int(candidate.id))
			exec_result = await update_submitted_votes(int(ctx.user_id))
			exec_result = await db_cur.execute(
				'INSERT INTO submitted_votes('
					'voter_id,'
					'vote_timestamp'
				') VALUES('
					'?,'
					'?'
				') ON CONFLICT(voter_id) DO UPDATE SET vote_timestamp = ?',
				(int(ctx.user.id), int(time()), int(time()))
			)
			vote_stats_channel = search_channelid(ctx.guild.channels, 'lobotkaisen-announce')
			exec_result = await db_cur.execute(
				'SELECT candidate_id, vote_count FROM votes ORDER BY vote_count DESC LIMIT 15'
			)
			leaderboard_val = []
			i = 1
			colors = (33, 37, 31)
			async for row in exec_result:
				leaderboard_val.append({
					    'color' : colors[i - 1] if i <= len(colors) else 34,
					     'rank' : i,
					'candidate' : (await ctx.guild.fetch_member(row[0])).display_name,
					    'votes' : row[1],
				})
				i += 1
			max_len = 0
			for row in leaderboard_val:
				if len(row['candidate']) > max_len:
					max_len = len(row['candidate'])
			leaderboard = []
			for row in leaderboard_val:
				leaderboard.append('\033[%%(color)dm  %%(rank)2d. %%(candidate)-%ds : %%(votes)d Votes' % max_len % row)
			leaderboard = (
				'Top 15 Candidates for <@&%d>:\n'
				'```ansi\n%s\n```'
				'\n'
				'Vote for your own candidate in <#%d>'
			) % (search_role(ctx, 'Lobotomy King/Queen of the Day'), '\n'.join(leaderboard), search_channel(ctx, 'lobotkaisen-voting'))
			fetch_result = await get_botvar('msg_id_lobotomyking')
			vote_msg = None
			if fetch_result is not None:
				vote_msg = await vote_stats_channel.fetch_message(fetch_result)
			if vote_msg is not None:
				await vote_msg.edit(content=leaderboard)
			else:
				vote_msg = await vote_stats_channel.send(leaderboard)
				await set_botvar('msg_id_lobotomyking', int(vote_msg.id))
			await db.db_conn.commit()
		await ctx.send('Your vote for <@%d> has been submitted' % candidate.id, ephemeral=True)

def setup(bot):
	VoteExt(bot)