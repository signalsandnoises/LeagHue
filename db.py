import sqlite3

class DB(object):
    def __init__(self):
        self.con = sqlite3.connect('drive.db')
        self.cur = self.con.cursor()
        self._setup_schema()

    def _setup_schema(self):
        """
        Example object:
        {
            "bridge_id": "ecb5fafffe1c49aa",
            "user": "o2fOTT6c3wb8fevjeEgmTtcsLyyJ65fe3eAYClJkc441",
            "key": "t9EfSmHRC267bCty5L3qFegM4Nh0FtwLBFn5EEwW"
        }
        """
        q = "CREATE TABLE IF NOT EXISTS BridgeKeys (bridge_id TEXT PRIMARY KEY, user TEXT, key TEXT)"
        try:
            self.cur.execute(q)
            self.con.commit()
        except Exception as e:
            print('ERROR: DB table creation failed.', e)
            return None

    def _close(self):
        self.con.commit()
        self.con.close()

    def insert_bridge_key(self, bridge_id: str, user: str, key: str) -> None:
        q = f"INSERT OR REPLACE INTO BridgeKeys VALUES ('{bridge_id}', '{user}','{key}')"
        try:
            self.cur.execute(q)
            self.con.commit()
        except Exception as e:
            print("ERROR: Can't insert bridge key.", e)

    def get_bridge_key(self, bridge_id: str) -> (str, str):
        q = f"SELECT user, key FROM BridgeKeys WHERE bridge_id == '{bridge_id}'"
        try:
            key = self.cur.execute(q)
            firstRow = key.fetchone()
            if firstRow is None:
                return (None, None)
            else:
                return firstRow
        except Exception as e:
            print(f"ERROR: Can't get bridge key for {bridge_id}.", e)
            return (None, None)

    def select_all(self) -> list:
        q = "SELECT * FROM BridgeKeys"
        try:
            data = self.cur.execute(q)
            return data.fetchall()
        except Exception as e:
            print("ERROR: Can't get all values.", e)
            return []