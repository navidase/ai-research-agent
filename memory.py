import sqlite3

DB_NAME = "memory.db"

def search_memory(keyword):
    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, content
        FROM memories
        ORDER BY id DESC
        LIMIT 20
    """)

    memories = cursor.fetchall()

    conn.close()

    return memories

    
def save_memory(role, content):
    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT
        )
    """)

    cursor.execute(
        "INSERT INTO memories (role, content) VALUES (?, ?)",
        (role, content)
    )

    conn.commit()
    conn.close()


def get_memories():
    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT
        )
    """)

    cursor.execute(
        "SELECT role, content FROM memories ORDER BY id"
    )

    memories = cursor.fetchall()

    conn.close()

    return memories