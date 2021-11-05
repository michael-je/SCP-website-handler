"""
Handles the SCP database

scp.number -> id_number and scp.exists -> exists_online in this file because number
& exists are keywords in sqlite3
"""

import sqlite3
from datetime import datetime
from os import path

from scp import SCP


class SCPDatabase():
    """
    ORM that handles all interactions with the SCP database
    """

    def __init__(self, db_name):
        self.db_path = path.dirname(path.realpath(__file__)) + '/' + db_name
        self.set_up_database()

    def set_up_database(self):
        """
        Create a new database if it doesn't already exist.
        """
        if path.exists(self.db_path):
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # booleans are stored as ints
        # rating is stored as text because it can be N/A
        cursor.execute(
            """
            CREATE TABLE scps (
                id_number text,
                name text,
                object_class text,
                rating text,
                URL text,
                has_image integer,
                have_read integer,
                dont_want_to_read integer,
                exists_online integer,
                is_favorite integer,
                unusual_format integer,
                last_updated text,
                read_later integer
            )
            """
        )

        conn.commit()
        conn.close()

    def update_scp(self, scp):
        """
        Update an SCP in the database
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now()
        last_updated = f"{now.day}-{now.month}-{now.year}"

        cursor.execute(
            """
            UPDATE scps SET
                id_number = :id_number,
                name = :name,
                object_class = :object_class,
                rating = :rating,
                URL = :URL,
                has_image = :has_image,
                have_read = :have_read,
                dont_want_to_read = :dont_want_to_read,
                exists_online = :exists_online,
                is_favorite = :is_favorite,
                unusual_format = :unusual_format,
                last_updated = :last_updated,
                read_later = :read_later

                WHERE id_number=:id_number
            """,
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
                "last_updated": last_updated,
                "read_later": scp.read_later
            }
        )

        conn.commit()
        conn.close()
        return 1

    def get_scp(self, scp_id_number):
        """
        Returns data for a given scp number
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM scps WHERE id_number={}".format(scp_id_number))
            # fetchall returns a list containing a dict of all field for scp if it 
            # exists, otherwise nothing
            data = cursor.fetchall()[0]
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
        read_later = data[12]

        output_scp = SCP(
            id_number,
            name,
            object_class,
            rating,
            URL,
            has_image,
            have_read,
            dont_want_to_read,
            exists_online,
            is_favorite,
            unusual_format,
            last_updated,
            read_later
        )

        return output_scp

    def add_scp(self, scp):
        """
        Add an SCP to the database
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now()
        last_updated = f"{now.day}-{now.month}-{now.year}"

        if self.get_scp(scp.number) == -1:
            cursor.execute(
                """
                INSERT INTO scps VALUES (
                    :id_number,
                    :name,
                    :object_class,
                    :rating,
                    :URL,
                    :has_image,
                    :have_read,
                    :dont_want_to_read,
                    :exists_online,
                    :is_favorite,
                    :unusual_format,
                    :last_updated,
                    :read_later
                )
                """,
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
                    "last_updated": last_updated,
                    "read_later": scp.read_later
                }
            )
        else:
            conn.commit()
            conn.close()
            # -1 indicates that the scp was already in the database
            return -1

        conn.commit()
        conn.close()
        return 1

    def get_available_scp_numbers(self, additional_data=[]):
        """
        Searches the database and returns the ids of all SCPs in it.

        optionally include a list of additional data points to return, e.g:
            additional_data=["have_read", "dont_want_to_read"]

        This function returns the data for each scp as a dict.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        additional_data_string = ", ".join(additional_data)
        if additional_data_string:
            additional_data_string = ", " + additional_data_string

        cursor.execute("SELECT id_number{} FROM scps".format(additional_data_string))
        # returns a list of tuples
        db_data = cursor.fetchall()

        # now we need to dynamically create a dictionary for each scps key-value pairs 
        # and collect those together in a list as output
        output_data= []
        for scp in db_data:
            scp_dict = {"number": scp[0]}
            for i, data_point in enumerate(additional_data):
                scp_dict[data_point] = scp[i+1]
            output_data.append(scp_dict)

        return output_data
