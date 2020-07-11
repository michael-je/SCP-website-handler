# handles the SCP database
# assume that we need to handle objects of the SCP class for now
# scp.number -> id_number and scp.exists -> exists_online in this file because number & exists are keywords in sqlite3
import sqlite3

from classes import SCP


# conn = sqlite3.connect("scps.db")
# c = conn.cursor()


# create a function that creates the scp table in the database, only run this once
def set_up_database():
    conn = sqlite3.connect("scps.db")
    c = conn.cursor()

    # take note that booleans should be stored as integer values 1 or 0
    # rating is stored as text since we need a way to know if it is N/A
    # id_number can remain as integer since we can always know its value
    c.execute("""
        CREATE TABLE scps (
        id_number integer,
        name text,
        object_class text,
        rating text,
        URL text,
        has_image integer,
        have_read integer,
        dont_want_to_read integer,
        exists_online integer,
        is_favorite integer,
        unusal_format integer,
        last_updated text)
        """)

    conn.commit()
    conn.close()


# create a function that updates an scp in the database
def update_scp(scp):
    conn = sqlite3.connect("scps.db")
    c = conn.cursor()

    c.execute(""""UPDATE scps SET
        "id_number" = :id_number,
        "name" = :name,
        "object_class" = :object_class,
        "rating" = :rating,
        "URL" = :URL,
        "has_image" = :has_image,
        "have_read" = :have_read,
        "dont_want_to_read" = :dont_want_to_read,
        "exists" = :exists,
        "is_favorite" = :is_favorite,
        "unusual_format" = :unusal_format,
        "last_updated" = :last_updated
        
        WHERE id_number=:id_number""",
        {
        "id_number": scp.number,
        "name": scp.name,
        "object_class": scp.object_class,
        "rating": scp.rating,
        "URL": scp.URL,
        "has_image": scp.has_image,
        "have_read": scp.have_read,
        "dont_want_to_read": scp.dont_want_to_read,
        "exists_online": scp.exists,
        "is_favorite": scp.is_favorite,
        "unusual_format": scp.unusal_format,
        "last_updated": scp.last_updated
        }
    )

    conn.commit()
    conn.close()
    # 1 indicates that the scp was updated successfully
    return 1


# create a function which returns the data for a given scp number
def get_scp(scp_id_number):
    conn = sqlite3.connect("scps.db")
    c = conn.cursor()

    try:
        c.execute("SELECT * FROM scps WHERE id_number={}".format(scp_id_number))
        # fetchall returns a list containing a dict of all field for scp if it exists, otherwise nothing
        data = c.fetchall()[0]
    except IndexError:
        # -1 indicates that the scp does not exist in the database
        return -1

    # parse the data
    id_number = data[0]
    name = data[1]
    object_class = data[2]
    rating = data[3]
    URL = data[4]
    has_image = data[5]
    have_read = data[6]
    dont_want_to_read = data[7]
    exists_online = data[8]
    is_favorite = data[9]
    unusual_format = data[10]
    last_updated = data[11]

    output_scp = SCP(id_number, name, object_class, rating, URL, has_image, have_read, dont_want_to_read,
                     exists_online, is_favorite, unusual_format, last_updated)

    return output_scp


# create function to add an scp to the database
def add_scp(scp):
    conn = sqlite3.connect("scps.db")
    c = conn.cursor()

    # first check if the scp already exists in the database
    check_db = get_scp(scp.number)
    if check_db == -1:
        c.execute("INSERT INTO scps VALUES (:id_number, :name, :object_class, :rating, :URL, :has_image, :have_read,\
            :dont_want_to_read, :exists_online, :is_favorite, :unusual_format, :last_updated)",
            {
            "id_number": scp.number,
            "name": scp.name,
            "object_class": scp.object_class,
            "rating": scp.rating,
            "URL": scp.URL,
            "has_image": scp.has_image,
            "have_read": scp.have_read,
            "dont_want_to_read": scp.dont_want_to_read,
            "exists_online": scp.exists,
            "is_favorite": scp.is_favorite,
            "unusual_format": scp.unusal_format,
            "last_updated": scp.last_updated
            }
        )
    else:
        conn.commit()
        conn.close()
        # -1 indicates that the scp was already in the database
        return -1

    conn.commit()
    conn.close()
    # 1 indicates that the scp was successfully inserted
    return 1


# conn.commit()
# conn.close()
