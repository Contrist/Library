from flask import Flask, render_template, Response, request
import sqlite3


DATABASE = "../data/database.db"

app = Flask(__name__,
            template_folder="../templates",
            static_folder="../static")


# Links to the /home page
@app.route('/home')
def home():
    connection = sqlite3.connect(DATABASE)
    try:
        books = connection.execute(
            "SELECT book_id, book_title FROM BOOKS ORDER BY imported_at DESC"
        ).fetchall()
    finally:
        connection.close()
    return render_template('home.html', books=books)


# links to the book_covers source url
@app.route("/book-cover/<int:book_id>")
def book_cover(book_id):
    connection = sqlite3.connect(DATABASE)
    try:
        cover = connection.execute(
            "SELECT book_cover FROM BOOKS WHERE book_id = ?",
            (book_id, )
        ).fetchone()
    finally:
        connection.close()
    return Response(cover[0], mimetype="image/jpeg")


# links to the /read page
@app.route("/read/<string:book_title>")
def open_book(book_title):
    book_id = request.args.get("book_id", type=int)
    requested_chapter_id = request.args.get("chapter_id", type=int)

    connection = sqlite3.connect(DATABASE)

    try:
        # If no chapter_id was provided, start at the bookmark.
        if requested_chapter_id is None:
            bookmark = connection.execute(
                """
                SELECT current_chapter_id
                FROM BOOKMARKS
                WHERE book_id = ?
                """,
                (book_id,)
            ).fetchone()

            chapter_id = bookmark[0]
        else:
            chapter_id = requested_chapter_id

        # Load the selected chapter.
        row = connection.execute(
            """
            SELECT chapter_id, chapter_index, chapter_text, chapter_title
            FROM CHAPTERS
            WHERE book_id = ? AND chapter_id = ?
            """,
            (book_id, chapter_id)
        ).fetchone()

        chapter_id, chapter_index, chapter_text, chapter_title = row

        # Find the closest chapter before and after this one.
        previous = connection.execute(
            """
            SELECT chapter_id
            FROM CHAPTERS
            WHERE book_id = ? AND chapter_index < ?
            ORDER BY chapter_index DESC
            LIMIT 1
            """,
            (book_id, chapter_index)
        ).fetchone()

        next_chapter = connection.execute(
            """
            SELECT chapter_id
            FROM CHAPTERS
            WHERE book_id = ? AND chapter_index > ?
            ORDER BY chapter_index ASC
            LIMIT 1
            """,
            (book_id, chapter_index)
        ).fetchone()

    finally:
        connection.close()

    paragraphs = chapter_text.split("\n\n") if chapter_text else []

    return render_template(
        "read.html",
        book_title=book_title,
        book_id=book_id,
        chapter_title=chapter_title,
        paragraphs=paragraphs,
        previous_chapter_id=previous[0] if previous else None,
        next_chapter_id=next_chapter[0] if next_chapter else None
    )


# links to the /details page
@app.route("/details/<string:book_title>?<book_id>")
def open_details(book_title, book_id):
    return render_template("details.html", book_title=book_title, book_id=book_id)


if __name__ == '__main__':
    app.run(debug=True)
