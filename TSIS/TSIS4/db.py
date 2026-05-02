import psycopg2
from config import DB_CONFIG

def connect():
    return psycopg2.connect(**DB_CONFIG)


def get_player_id(username):
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT id FROM players WHERE username=%s", (username,))
    result = cur.fetchone()

    if result:
        player_id = result[0]
    else:
        cur.execute(
            "INSERT INTO players(username) VALUES(%s) RETURNING id",
            (username,)
        )
        player_id = cur.fetchone()[0]
        conn.commit()

    cur.close()
    conn.close()
    return player_id


def save_game(username, score, level):
    conn = connect()
    cur = conn.cursor()

    player_id = get_player_id(username)

    cur.execute("""
        INSERT INTO game_sessions(player_id, score, level_reached)
        VALUES(%s, %s, %s)
    """, (player_id, score, level))

    conn.commit()
    cur.close()
    conn.close()


def get_leaderboard():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT username, score, level_reached, played_at
        FROM game_sessions
        JOIN players ON players.id = game_sessions.player_id
        ORDER BY score DESC
        LIMIT 10
    """)

    data = cur.fetchall()

    cur.close()
    conn.close()
    return data


def get_best_score(username):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT MAX(score)
        FROM game_sessions
        JOIN players ON players.id = game_sessions.player_id
        WHERE username=%s
    """, (username,))

    result = cur.fetchone()[0]

    cur.close()
    conn.close()
    return result or 0

# CREATE TABLE players (
#     id SERIAL PRIMARY KEY,
#     username VARCHAR(50) UNIQUE NOT NULL
# );

# CREATE TABLE game_sessions (
#     id SERIAL PRIMARY KEY,
#     player_id INTEGER REFERENCES players(id),
#     score INTEGER NOT NULL,
#     level_reached INTEGER NOT NULL,
#     played_at TIMESTAMP DEFAULT NOW()
# );