
import sqlite3, logging
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, channel):
        self.db_name = f"AIDungeon_{channel.replace('#', '').lower()}.db"
        sql = """
        CREATE TABLE IF NOT EXISTS WhisperIgnore (
            username TEXT COLLATE NOCASE,
            PRIMARY KEY (username)
        );
        """
        logger.debug("Creating WhisperIgnore Database...")
        self.execute(sql)
        logger.debug("Finished creating WhisperIgnore Database.")
    
    def execute(self, sql, values=None, fetch=False):
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            if values is None:
                cur.execute(sql)
            else:
                cur.execute(sql, values)
            conn.commit()
            if fetch:
                return cur.fetchall()

    def add_whisper_ignore(self, username):
        self.execute("INSERT OR IGNORE INTO WhisperIgnore(username) SELECT ?", (username,))
    
    def check_whisper_ignore(self, username):
        return self.execute("SELECT username FROM WhisperIgnore WHERE username = ?;", (username,), fetch=True)

    def remove_whisper_ignore(self, username):
        self.execute("DELETE FROM WhisperIgnore WHERE username = ?", (username,))
