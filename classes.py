class SCP:
    def __init__(self, number, name, object_class, rating, URL, has_image, have_read=False, dont_want_to_read=False, exists=True,
                 is_favorite=False, unusual_format=False):
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

    def display(self, debug=False):
        print('Number:', self.number)
        print('Name:', self.name)
        print('Object Class:', self.object_class)
        print('Rating:', self.rating)
        print('Link:', self.URL)
        if debug:
            print('Have read:', self.have_read)
            print("Don't want to read:", self.dont_want_to_read)
            print('Exists:', self.exists)
            print('Is favorite:', self.is_favorite)
            print('Has unusual format:', self.unusal_format)
            print('Has image:', self.has_image)