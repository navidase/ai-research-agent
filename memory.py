import sqlite3

DB_NAME = "memory.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)

    return conn


def save_memory(role, content):
    conn = get_connection()

    conn.execute(
        "INSERT INTO memories (role, content) VALUES (?, ?)",
        (role, content)
    )

    conn.commit()
    conn.close()


def search_memory(keyword, limit=10):
    conn = get_connection()

    memories = conn.execute(
        """
        SELECT role, content
        FROM memories
        WHERE content LIKE ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (f"%{keyword}%", limit)
    ).fetchall()

    conn.close()

    return memories


def get_memories():
    conn = get_connection()

    memories = conn.execute(
        """
        SELECT role, content
        FROM memories
        ORDER BY id
        """
    ).fetchall()

    conn.close()

    return memories