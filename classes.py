class SCP:
    def __init__(self, number, name, object_class, rating, URL, has_image, have_read=0, dont_want_to_read=0, exists=1,
                 is_favorite=0, unusual_format=0, last_updated="Never"):
        self.number = number
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

    def display(self, debug=False):
        print('Number:', self.number)
        print('Name:', self.name)
        print('Object Class:', self.object_class)
        print('Rating:', self.rating)
        print('Link:', self.URL)
        if debug:
            print('Have read:', bool(self.have_read))
            print("Don't want to read:", bool(self.dont_want_to_read))
            print('Exists:', bool(self.exists))
            print('Is favorite:', bool(self.is_favorite))
            print('Has unusual format:', bool(self.unusal_format))
            print('Has image:', bool(self.has_image))
            print('Last updated:', self.last_updated)

    def debug_info(self):
        return [
            f"number - {self.number}",
            f"name - {self.name}",
            f"class - {self.object_class}",
            f"rating - {self.rating}",
            f"URL - {self.URL}",
            f"has_image - {self.has_image}",
            f"have_read - {self.have_read}",
            f"dont_want - {self.dont_want_to_read}",
            f"exists - {self.exists}",
            f"is_favorite - {self.is_favorite}",
            f"unusual - {self.unusal_format}",
            f"last_updated - {self.last_updated}"
        ]

    def __repr__(self):
        return "{} - {}\n{}\n".format(self.number, self.name, self.URL)
