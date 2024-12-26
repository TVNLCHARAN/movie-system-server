import sqlite3
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join('./backend/app')))

from schemas.movie_schema import create_shows_table, create_movies_watched_table, create_users_table, create_movies_liked_table

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

csv_file = os.path.abspath('./backend/app/data/netflix_titles.csv')

df = pd.read_csv(csv_file)

df['show_id'] = df['show_id'].map(lambda x: x[1:]).astype('int64')

df['rating'] = df['rating'].fillna('Unknown').apply(lambda x: x if x in ['G', 'PG', 'PG-13', 'R', 'NC-17', 'TV-G', 'TV-PG', 'TV-Y', 'TV-Y7', 'TV-MA', 'TV-14', 'TV-Y7-FV', 'UR'] else 'Unknown')

df['duration'] = df['duration'].apply(lambda x: int(x.split()[0]) if isinstance(x, str) and 'min' in x else None)

df = df.fillna('Unknown')

cursor.execute('DROP TABLE IF EXISTS shows;')

cursor.execute(create_shows_table)

def insert_data_to_db(df):
    for _, row in df.iterrows():
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO shows (show_id,
                            title,
                            description,
                            cast,
                            director,
                            rating,
                           release_year,
                           duration,
                           listed_in,
                           country,
                           date_added
                           )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['show_id'],
                row['title'],
                row['description'],
                row['cast'],
                row['director'],
                row['rating'],
                row['release_year'] if pd.notna(row['release_year']) else None,  
                row['duration'],
                row['listed_in'],
                row['country'],
                row['date_added'] if pd.notna(row['date_added']) else None  
            ))
        except:
            print(row)
            continue
    conn.commit()

insert_data_to_db(df)

cursor.execute(create_users_table)
cursor.execute(create_movies_watched_table)
cursor.execute(create_movies_liked_table)

print("Tables created successfully!")

conn.close()
print("Database setup completed!")

print("Data inserted and database setup completed!")