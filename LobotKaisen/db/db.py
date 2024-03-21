import aiosqlite
import json
import os
import abc

from argparse import Namespace
from typing import Optional

# TODO: implement thread-safe reference counter and garbage
#       collection for DBConnection classes
db_enum = {}

class DBConnection(abc.ABC):
	def __init__(self, db_uri: str):
		self._db_uri = os.path.realpath(db_uri)
		self._db_cur = None
		self._db_next = None
		self._db_next_list = self._db_init_next()
		self._db_conn = db_enum.get(self._db_uri)
		if self._db_conn is None:
			self._db_conn = self._db_open()
			db_enum[self._db_uri] = self._db_conn

	def __iter__(self):
		self._db_cur = 0
		self._db_next_list = self._db_init_next()
		if self._db_next_list is None:
			raise NotImplementedError

	def __next__(self):
		if self._db_cur < len(self._db_next):
			self._db_next = self._db_next_list[self._db_cur]
			return self._db_next
		raise StopIteration

	@abc.abstractmethod
	def _db_open(self) -> "Connection":
		'''
		Method to open the database
		'''
		pass

	@abc.abstractmethod
	def _db_init_next(self) -> list:
		'''
		Method to initialize the known `next`-values (return None if not implemented)
		'''
		return None

	@abc.abstractmethod
	def _db_validate_next(self, next_entry) -> Optional[int]:
		'''
		Method to validate `_db_next`-jumps
		'''
		return None

	def db_jump(self, next_entry):
		self._db_next = self._db_validate_next(next_entry)
		return self._db_next

class SQLConnection(DBConnection):
	def _db_open(self) -> aiosqlite.Connection:
		return aiosqlite.connect(self._db_uri)

	def _db_init_next(self):
		return None

	def _db_validate_next(self, next_entry: int) -> Optional[int]:
		if issubclass(next_entry, int):
			return next_entry

	async def db_init(self, init_script: str):
		async with self._db_conn.cursor() as db_cur:
			with open(init_script, 'r', encoding='utf-8') as script_file:
				await db_cur.executescript(script_file.read())

	async def _sql_votes_get_timestamp(self, voter_id: int, server_id: int=...) -> int:
		if server_id is ...:
			server_id = self._db_next

		async with self._db_conn.cursor() as db_cur:
			exec_result = await db_cur.execute(
				'SELECT vote_timestamp FROM submitted_votes WHERE voter_id = :voter_id AND server_id = :server_id',
				{'voter_id': voter_id, 'server_id': server_id}
			)
			fetch_result = await exec_result.fetchone()

			return None if fetch_result is None else fetch_result[0]

	async def _sql_votes_get_election_result(self, server_id: int=...) -> list[int]:
		election_board = []

		if server_id is ...:
			server_id = self._db_next

		async with self._db_conn.cursor() as db_cur:
			exec_result = await db_cur.execute(
				'SELECT candidate_id FROM votes WHERE vote_count = ('
					'SELECT max(vote_count) FROM votes WHERE server_id = :server_id'
				') AND server_id = :server_id',
				{'server_id': server_id}
			)

			async for row in exec_result:
				election_board.append(row[0])

			return election_board

	async def _sql_votes_get_leaderboard(self, leaderboard_rows: int=..., server_id: int=...) -> list[int]:
		leaderboard = []

		if leaderboard_rows is ...:
			leaderboard_rows = 15

		if server_id is ...:
			server_id = self._db_next

		async with self._db_conn.cursor() as db_cur:
			exec_result = await db_cur.execute(
				'SELECT candidate_id FROM votes WHERE server_id = :server_id ORDER BY vote_count DESC LIMIT :leaderboard_rows',
				{'leaderboard_rows': leaderboard_rows, 'server_id': server_id}
			)

			async for row in exec_result:
				leaderboard.append(row[0])

			return leaderboard

	async def _sql_bot_vars_get_variable(self, var_name: str, server_id: int=...):
		if server_id is ...:
			server_id = self._db_next

		async with self._db_conn.cursor() as db_cur:
			exec_result = await db_cur.execute(
				'SELECT val FROM bot_vars WHERE var = :var_name AND server_id IS :server_id',
				{'var_name': var_name, 'server_id': server_id}
			)
			fetch_result = await exec_result.fetchone()

			return None if fetch_result is None else fetch_result[0]

	async def _sql_bot_vars_set_variable(self, var_name: str, any_val, server_id: int=...):
		if server_id is ...:
			server_id = self._db_next

		async with self._db_conn.cursor() as db_cur:
			await db_cur.execute(
				'INSERT INTO bot_vars('
					'var,'
					'server_id,'
					'val'
				') VALUES('
					':var_name,'
					':server_id,'
					':any_val'
				') ON CONFLICT DO UPDATE SET val = :any_val',
				{'var_name': var_name, 'any_val': any_val, 'server_id': server_id}
			)
			await self.commit()

	def __getitem__(self, key):
		return {
			'votes': Namespace(
				get_timestamp=self._sql_votes_get_timestamp,
				get_election_result=self._sql_votes_get_election_result,
				get_leaderboard=self._sql_votes_get_leaderboard
			),
			'bot_vars': Namespace(
				get_variable=self._sql_bot_vars_get_variable,
				set_variable=self._sql_bot_vars_set_variable
			),
		}.get(key)

	async def cursor(self) -> aiosqlite.Cursor:
		return await self._db_conn.cursor()

	async def commit(self):
		await self._db_conn.commit()

class JSONConnection(DBConnection):
	def _db_open(self) -> list[dict]:
		with open(self._db_uri, 'r', encoding='utf-8') as json_db:
			json_data = json.load(json_db)

	def _db_init_next(self):
		return self._db_conn

	def _db_validate_next(self, next_entry) -> Optional[int]:
		if not issubclass(next_entry, (str, int)):
			return None
		for entry in self._db_conn:
			if entry.get('id') == next_entry or entry.get('name') == next_entry:
				return entry

	def get_json(self, obj_id=...):
		if obj_id is ...:
			return self._db_next
		else:
			return self._db_validate_next(obj_id)
