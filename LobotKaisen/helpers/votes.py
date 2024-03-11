from ..db import db

async def update_votes(candidate_id):
	async with db.db_conn.cursor() as db_cur:
		await db_cur.execute(
			'INSERT INTO votes('
				'candidate_id,'
				'vote_count'
			') VALUES('
				'?,'
				'1'
			') ON CONFLICT(candidate_id) DO UPDATE SET vote_count = vote_count + 1',
			(candidate_id)
		)
		await db.db_conn.commit()