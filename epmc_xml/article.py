class Article:
    def __init__(
        self, title, author_list, abstract, date, sections, type, figures=None
    ):
        self.title = title
        self.author_list = author_list
        self.abstract = abstract
        self.date = date
        self.sections = sections
        self.type = type
        self.figures = figures or {}  # Dictionary to store figure captions by section

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

    def get_body(self, include_figures=False):
        body_str = ""
        for key, value in self.sections.items():
            body_str += key + "\n"

            # If we need to include figures and they exist for this section
            if include_figures and key in self.figures and self.figures[key]:
                # Split the section text by paragraphs to interleave figures
                paragraphs = value.split("\n")
                final_text = ""

                for para in paragraphs:
                    if para.strip():  # If not an empty paragraph
                        final_text += para + "\n"

                # Add figures at the end of the section
                for fig_id, fig_content in self.figures[key].items():
                    final_text += "\n--- FIGURE ---\n"
                    final_text += f"Figure ID: {fig_id}\n"
                    final_text += fig_content
                    final_text += "\n--- END FIGURE ---\n\n"

                body_str += final_text + "\n"
            else:
                body_str += value + "\n\n"

        return body_str
