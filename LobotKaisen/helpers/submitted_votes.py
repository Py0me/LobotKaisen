from ..db import db

async def update_submitted_votes(user_id, ):
	async with db.db_conn.cursor() as db_cur:
		await db_cur.execute(
			'INSERT INTO submitted_votes('
				'voter_id,'
				'vote_timestamp'
			') VALUES('
				'?,'
				'?'
			') ON CONFLICT(voter_id) DO UPDATE SET vote_timestamp = ?',
			(user_id, int(time), int(time))
		)
		await db.db_conn.commit()