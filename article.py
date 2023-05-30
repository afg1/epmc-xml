class Article:
    def __init__(self, title, author_list, abstract, date, sections, type):
        self.title = ""
        self.author_list = ""
        self.abstract = ""
        self.date = ""
        self.sections = {}
        self.type = ""

    def __str__(self):
        return f"Title: {self.title}\nAuthor List: {self.author_list}\nAbstract: {self.abstract}\nDate: {self.date}\nSections: {self.sections}\nType: {self.type}"
