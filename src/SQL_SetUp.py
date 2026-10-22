import sqlite3


def open_SQLite():
    # this function opens AND closes SQL again, keep in mind

    connection = sqlite3.connect("../data/database.db")

    try:  # makes things safer by ensuring 'connection.close()' will happen in case of error
        cursor = connection.cursor()

        # SQLite foreign-key checks must be enabled for each connection.
        cursor.execute("PRAGMA foreign_keys = ON")

        # BOOKS Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS BOOKS (
                book_id INTEGER PRIMARY KEY,
                fiction_id TEXT NOT NULL UNIQUE,
                book_title TEXT NOT NULL,
                book_author TEXT,
                book_cover BLOB,
                imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_update_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # CHAPTERS Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CHAPTERS (
                chapter_id INTEGER PRIMARY KEY,
                book_id INTEGER NOT NULL,
                chapter_index INTEGER NOT NULL,
                chapter_title TEXT,
                chapter_text TEXT,
                released_at TEXT,
                UNIQUE (book_id, chapter_index),
                UNIQUE (book_id, chapter_id),
                FOREIGN KEY (book_id) REFERENCES BOOKS(book_id)
            )
        """)

        # BOOKMAKRS Table
        # paragraph_index NOT INTEGRATED AS IT REQUIERES GUI STUFF
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS BOOKMARKS (
                book_id INTEGER PRIMARY KEY,
                current_chapter_id INTEGER,
                paragraph_index INTEGER,
                last_read_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (book_id) REFERENCES BOOKS(book_id),
                FOREIGN KEY (book_id, current_chapter_id)
                    REFERENCES CHAPTERS(book_id, chapter_id)
            )
        """)

        connection.commit()

    finally:
        connection.close()


def add_book(book_data, chapter_data):  # book_data is a dict, while chapter_data is a list with a dict per row
    connection = sqlite3.connect("../data/database.db")

    try:
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")

        cursor.execute(
            "SELECT 1 FROM BOOKS WHERE fiction_id = ?",
            (book_data["fiction_id"],)
        )

        if cursor.fetchone() is not None:
            print(f"Book already exists: {book_data["fiction_id"]}")
            return False

        cursor.execute(
            """INSERT INTO BOOKS
               (fiction_id, book_title, book_author, book_cover)
               VALUES
               (:fiction_id, :book_title, :book_author, :book_cover)""",
            book_data
        )

        book_id = cursor.lastrowid

        for x in chapter_data:
            x["book_id"] = book_id

        cursor.executemany(
            """INSERT INTO CHAPTERS
               (book_id, chapter_index, chapter_title, chapter_text, released_at)
               VALUES
               (:book_id, :chapter_index, :chapter_title, :chapter_text, :released_at)""",
            chapter_data
        )

        # this here gets the chapter_id from the first chapter
        cursor.execute("SELECT chapter_id from CHAPTERS WHERE book_id = ? AND chapter_index = ?", (book_id, 1))
        row = cursor.fetchone()

        if row is None:  # prevents unclean transaction
            raise RuntimeError("Chapter 1 was not inserted; cannot create its bookmark.")

        chapter_id = row[0]
        cursor.execute(
            """INSERT INTO BOOKMARKS
               (book_id, current_chapter_id, paragraph_index)
               VALUES (?, ?, ?)""",
            (book_id, chapter_id, 0)
        )

        # dont even know if paragraph_index will ever be used but we inlude it anyways
        # also we omit last_read_at, so it generates a timestamp

        connection.commit()

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()
        print("book added")
