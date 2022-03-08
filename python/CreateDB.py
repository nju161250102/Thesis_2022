import sqlite3

if __name__ == "__main__":
    conn = sqlite3.connect('my.db')
    c = conn.cursor()

    c.execute("DROP TABLE IF EXISTS worker;")
    c.execute('''
    CREATE TABLE worker (
      id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
      name TEXT DEFAULT NULL,
      email TEXT DEFAULT NULL,
      password TEXT DEFAULT NULL);
    ''')

    c.execute("DROP TABLE IF EXISTS project;")
    c.execute('''
    CREATE TABLE project (
      id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
      name TEXT DEFAULT NULL,
      version TEXT DEFAULT NULL,
      state INTEGER NOT NULL,
      create_time TEXT DEFAULT NULL,
      description TEXT DEFAULT NULL);
    ''')

    c.execute("DROP TABLE IF EXISTS alarm;")
    c.execute('''
    CREATE TABLE alarm (
      id TEXT NOT NULL PRIMARY KEY,
      project_id INTEGER NOT NULL,
      category TEXT DEFAULT NULL,
      type TEXT DEFAULT NULL,
      rank INTEGER NOT NULL,
      path TEXT DEFAULT NULL,
      classname TEXT DEFAULT NULL,
      method TEXT DEFAULT NULL,
      signature TEXT DEFAULT NULL,
      location INTEGER DEFAULT -1,
      create_time TEXT DEFAULT NULL);
    ''')

    c.execute("DROP TABLE IF EXISTS label;")
    c.execute('''
    CREATE TABLE label (
      id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
      alarm_id TEXT NOT NULL,
      worker_id INTEGER NOT NULL,
      value INTEGER NOT NULL ,
      label_time TEXT DEFAULT NULL,
      create_time TEXT DEFAULT NULL);
    ''')

