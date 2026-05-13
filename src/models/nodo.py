
class Nodo:
    def __init__(self, pagename, id, categories):
        self.id = id
        self.categories = categories
        self.pagename = pagename
        self.links = []

    def get_links(self):
        return self.links

    def get_categories(self):
        return self.categories
