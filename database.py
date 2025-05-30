import mysql.connector
from mysql.connector import Error

def get_db_connection(db_name='sakila'):
    try:
        conn = mysql.connector.connect(
            host="your host",
            user="your user",
            password="your password",
            database=db_name,
            auth_plugin='mysql_native_password',
            port=your port,
            connection_timeout=10
        )
        return conn
    except Error as e:
        print(f"MySQL connection error: {e}")
        raise

def advanced_search(keyword="", genres=None, year_from=None, year_to=None, sort_by="title_asc"):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT DISTINCT f.title, f.description, f.release_year, f.length,
               GROUP_CONCAT(c.name SEPARATOR ', ') AS genres
        FROM film f
        LEFT JOIN film_category fc ON f.film_id = fc.film_id
        LEFT JOIN category c ON fc.category_id = c.category_id
        WHERE 1 = 1
        """
        params = []

        if keyword:
            query += " AND (f.title LIKE %s OR f.description LIKE %s)"
            keyword_param = f"%{keyword}%"
            params.extend([keyword_param, keyword_param])

        if genres:
            query += " AND c.name IN (" + ",".join(["%s"] * len(genres)) + ")"
            params.extend(genres)

        if year_from:
            query += " AND f.release_year >= %s"
            params.append(year_from)

        if year_to:
            query += " AND f.release_year <= %s"
            params.append(year_to)

        query += " GROUP BY f.film_id"

        if sort_by == "title_asc":
            query += " ORDER BY f.title ASC"
        elif sort_by == "title_desc":
            query += " ORDER BY f.title DESC"
        elif sort_by == "year_asc":
            query += " ORDER BY f.release_year ASC"
        elif sort_by == "year_desc":
            query += " ORDER BY f.release_year DESC"
        elif sort_by == "length_desc":
            query += " ORDER BY f.length DESC"

        cursor.execute(query, params)
        results = cursor.fetchall()
        return results
    except Error as e:
        print(f"Search error: {e}")
        return []
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

# В database.py

def log_search(query, search_type):
    try:
        # Добавляем проверку существования фильма
        if not check_movie_exists(query):
            return
            
        conn = get_db_connection('log_db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO search_logs (query, search_type) VALUES (%s, %s)",
            (query, search_type)
        )
        conn.commit()
    except Error as e:
        print(f"[ERROR] Logging failed: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def get_popular_queries():
    try:
        conn = get_db_connection('log_db')
        cursor = conn.cursor(dictionary=True)

        sql = """
            SELECT s.query, COUNT(*) as count 
            FROM search_logs s
            INNER JOIN sakila.film f ON s.query = f.title  # Добавляем JOIN
            WHERE s.query != '' 
              AND NOT REGEXP_LIKE(s.query, '^[0-9]+$')
            GROUP BY s.query 
            ORDER BY count DESC 
            LIMIT 10;
        """
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    except Error as e:
        print(f"Error getting popular queries: {e}")
        return []
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

# Новая функция для проверки существования фильма
def check_movie_exists(title):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM film WHERE title = %s LIMIT 1", (title,))
        return cursor.fetchone() is not None
    except Error as e:
        print(f"Error checking movie: {e}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
            
def get_all_genres():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM category")
        genres = [row[0] for row in cursor.fetchall()]
        return genres
    except Error as e:
        print(f"Error getting genres: {e}")
        return []
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

import re

def get_top_violent_films(limit=10):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT title, release_year, length, rating
            FROM film
            WHERE rating IN ('G', 'PG', 'PG-13', 'R', 'NC-17')
            ORDER BY CASE rating
                WHEN 'NC-17' THEN 1
                WHEN 'R' THEN 2
                WHEN 'PG-13' THEN 3
                WHEN 'PG' THEN 4
                WHEN 'G' THEN 5
                ELSE 6
            END ASC,
            release_year DESC
            LIMIT %s
        """, (limit,))

        results = cursor.fetchall()
        return results

    except Error as e:
        print(f"Error getting top violent films: {e}")
        return []
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

