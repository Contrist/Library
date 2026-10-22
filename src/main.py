import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
from SQL_SetUp import open_SQLite, add_book


website = "removed"


def fetch_content(url):
    #removed
    pass



def get_book_info(html, website):
    # removed

    # left intact, so you see what content gets added to the db
    data = {  # this here is the data, we INSERT into the BOOKS Table
        "fiction_id": "removed",
        "book_title": "removed",
        "book_author": "removed",
        "book_cover": "removed"
    }
    print(f"adding book with fiction_id: {data["fiction_id"]}")
    # print("https://www.royalroad.com" + lower_url)
    return data, "removed"


def get_chapters(url, amount_chapters):
    print("reading chapters")
    data = []  # we initialize an empty list, which we're gonna fill with the chapter rows
    current_url = url  # we do this because were gonna change it to the next chapter every loop
    for i in range(1, amount_chapters + 1):  # we need i for the index, so we start counting at 1
        # removed
        row = {  # this here is the data, we INSERT into the BOOKS Table
            # "chapter_id": None,  # we leave this None so it generates a unique rowid
            "book_id": None,  # we leave this at None for now, but later when we INSERT it into the table, we replace it with cursor.lastrowid
            "chapter_index": i,
            "chapter_title": "removed",
            # "chapter_text": "\n\n".join(paragraph.text for paragraph in chapter_content.find_all("removed")),
            # this is advanced datetime shenanigans -> finds correct place in html -> converts into datetime -> formats datetime and adds +1 hour UTC (because website)
            # "released_at": datetime.fromisoformat(soup.find("time", attrs={"datetime": True})["datetime"].replace("Z", "+00:00")).strftime("%d/%m/%Y, %I:%M %p")
        }
        data.append(row)
        if i < amount_chapters:
            # removed
            break
        print(row["chapter_index"], row["chapter_title"], row["released_at"])
        time.sleep(0.25) # so we dont overload royalroad website
    return data


def main(website):
    open_SQLite()  # this create all neccessary tables if they dont already exist yet.

    # fetch_content gets actual html content, while website arg is there to get fiction_id
    book_data, first_chapter_url, amount_chapters = get_book_info(fetch_content(website), website)
    chapter_data = get_chapters(first_chapter_url, amount_chapters)
    add_book(book_data, chapter_data)


main(website)
