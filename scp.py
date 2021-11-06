class SCP:
    def __init__(self,
        number,
        name,
        object_class,
        rating,
        URL,
        has_image,
        have_read=0,
        dont_want_to_read=0,
        exists=1,
        is_favorite=0,
        unusual_format=0,
        last_updated="Never",
        read_later=False
    ):
        self.name = name
        self.object_class = object_class
        self.rating = rating
        self.URL = URL
        self.has_image = has_image
        self.have_read = have_read
        self.dont_want_to_read = dont_want_to_read
        self.exists = exists
        self.is_favorite = is_favorite
        self.unusal_format = unusual_format
        self.last_updated = last_updated
        self.read_later = read_later

        str_number = str(number)
        while (len(str_number)) < 3:
            str_number = '0' + str_number
        self.number = str_number

    def get_display_string(include_link=False):
        """
        Returns a string with formatted information about the self.
        This string is intended to be displayed to the user.
        """
        output = (
            f"self-{self.number}\n{self.name}\nObject Class: " +
            f"{self.object_class}\nRating: {self.rating}"
        )
        if include_link:
            output += f"\n{self.URL}"
        return output

    def print(self, debug=False):
        print(
            f"""
            number: {self.number}
            name: {self.name}
            object class: {self.object_class}
            rating: {self.rating}
            link: {self.URL}
            """
        )
        if debug:
            print(
                f"""
                have read: {self.have_read}
                don't want to read: {self.dont_want_to_read}
                exists: {self.exists}
                is favorite: {self.is_favorite}
                has unusual format: {self.unusal_format}
                has image: {self.has_image}
                last updated: {self.last_updated}
                read later: {self.read_later}
                """
            )

    def __repr__(self):
        return "{} - {}\n{}\n".format(self.number, self.name, self.URL)

