class Article:
    def __init__(self, title, author_list, abstract, date, sections, type):
        self.title = title
        self.author_list = author_list
        self.abstract = abstract
        self.date = date
        self.sections = sections
        self.type = type

    def __str__(self):
        return f"Title: {self.title}\nAuthor List: {self.author_list}\nAbstract: {self.abstract}\nDate: {self.date}\nSections: {self.sections}\nType: {self.type}"

    def __repr__(self):
        return f"Title: {self.title}\nAuthor List: {self.author_list}\nAbstract: {self.abstract}\nDate: {self.date}\nSections: {self.sections}\nType: {self.type}"

    def get_title(self):
        return self.title

    def get_author_list(self):
        return self.author_list

    def get_abstract(self):
        return self.abstract

    def get_date(self):
        return self.date

    def get_sections(self):
        return self.sections

    def get_type(self):
        return self.type

    def get_body(self):
        body_str = ""
        for key, value in self.sections.items():
            body_str += key + "\n"
            body_str += value + "\n\n"

        return body_str
