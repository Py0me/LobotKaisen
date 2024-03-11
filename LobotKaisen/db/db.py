import aiosqlite
import json
import asyncio

db_conn = None
json_data = None
json_cur = None

async def init(db_uri: str):
	global db_conn
	if db_conn is None:
		db_conn = await aiosqlite.connect(db_uri)
		async with db_conn.cursor() as cur:
			with open('db/voting.sql', 'r', encoding='utf-8') as script_file:
				await cur.executescript(script_file.read())

async def get_cursor() -> aiosqlite.Cursor:
	global db_conn
	if db_conn is None:
		await init('lobotomy-db.sqlite')
	return await db_conn.cursor()

def init_json(json_uri: str):
	global json_data
	global json_cur
	if json_data is None:
		with open(json_uri, 'r', encoding='utf-8') as json_db:
			json_data = json.load(json_db)

def next_json() -> dict:
	global json_data
	global json_cur
	if json_data is None:
		init_json('db/servers.json')
	if json_cur is None and len(json_data) > 0:
		json_cur = 0
	elif json_cur + 1 < len(json_data):
		json_cur += 1
	else:
		json_cur = None
	return json_data[json_cur] if json_cur is not None else None
