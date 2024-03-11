from ..db import db

async def set_botvar(varname, val, server_id=None):
	async with db.db_conn.cursor() as db_cur:
		await db_cur.execute(
			'INSERT INTO bot_vars('
				'var,'
				'server_id,'
				'val'
			') VALUES('
				'?,'
				'?,'
				'?'
			') ON CONFLICT(var) DO UPDATE SET val = ?',
			(varname, server_id, val, val)
		)
		await db.db_conn.commit()

async def get_botvar(varname, server_id=None):
	async with db.db_conn.cursor() as db_cur:
		exec_result = await db_cur.execute(
			'SELECT val FROM bot_vars WHERE var = ? AND server_id = ?',
			(varname, server_id)
		)
		var = await exec_result.fetchone()
		return var[0] if var is not None else None