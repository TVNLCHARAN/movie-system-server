import sqlite3

create_shows_table = '''
CREATE TABLE IF NOT EXISTS shows (
    show_id INTEGER PRIMARY KEY,
    type TEXT,
    title TEXT,
    director TEXT,
    cast TEXT,
    country TEXT,
    date_added TEXT,
    release_year INTEGER,
    rating TEXT,
    duration FLOAT,
    listed_in TEXT,
    description TEXT
);
'''


create_users_table = '''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT UNIQUE,
    date_joined DATE DEFAULT CURRENT_DATE
);
'''

create_movies_watched_table = '''
CREATE TABLE IF NOT EXISTS movies_watched (
    watched_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    show_id INTEGER NOT NULL,
    watch_date DATETIME default CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (show_id) REFERENCES shows(show_id)
);
'''

create_movies_liked_table = '''
CREATE TABLE IF NOT EXISTS movies_liked (
    liked_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    show_id INTEGER NOT NULL,
    liked_date DATETIME default CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (show_id) REFERENCES shows(show_id)
);
'''

if __name__ == '__main__':
    conn = sqlite3.connect('../database.db')

    cursor = conn.cursor()

    cursor.execute(create_shows_table)
    cursor.execute(create_users_table)
    cursor.execute(create_movies_watched_table)
    cursor.execute(create_movies_liked_table)

    conn.close()