CREATE TABLE IF NOT EXISTS votes(
	candidate_id INTEGER,
	server_id INTEGER,
	vote_count INTEGER
);

CREATE UNIQUE INDEX IF NOT EXISTS votes_idx ON votes(
	candidate_id,
	server_id
);

CREATE TABLE IF NOT EXISTS submitted_votes(
	voter_id INTEGER,
	server_id INTEGER,
	vote_timestamp INTEGER
);

CREATE UNIQUE INDEX IF NOT EXISTS submitted_votes_idx ON submitted_votes(
	voter_id,
	server_id
);

CREATE TABLE IF NOT EXISTS bot_vars(
	var TEXT,
	server_id INTEGER,
	val
);

CREATE UNIQUE INDEX IF NOT EXISTS bot_vars_idx ON bot_vars(
	var,
	server_id
);