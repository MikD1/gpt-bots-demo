import sqlite3


class Database:
    def __init__(self, filename: str):
        self.connection = sqlite3.connect(filename)
        self.__create_table()

    def __del__(self):
        self.connection.close()

    def add_counter(self, userId: str, counter: int):
        cursor = self.connection.cursor()
        try:
            with self.connection:
                cursor.execute("SELECT counter FROM Counters WHERE userId = ?", (userId,))
                results = cursor.fetchall()
                if len(results) > 0:
                    current_counter = results[0][0]
                    cursor.execute(
                        "UPDATE Counters SET counter = ? WHERE userId = ?",
                        (current_counter + counter, userId),
                    )
                else:
                    cursor.execute(
                        "INSERT INTO Counters (userId, counter) VALUES (?, ?)",
                        (userId, counter),
                    )
        except:
            pass

    def get_counter(self, userId: str):
        cursor = self.connection.cursor()
        cursor.execute("SELECT counter FROM Counters WHERE userId = ?", (userId,))
        results = cursor.fetchall()
        if len(results) > 0:
            return results[0][0]
        else:
            return 0

    def __create_table(self):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Counters (
            id INTEGER PRIMARY KEY,
            userId TEXT NOT NULL,
            counter INTEGER
            )
            """
        )
        self.connection.commit()

    connection = sqlite3.Connection
