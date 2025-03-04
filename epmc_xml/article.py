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
        self.figures = (
            figures or []
        )  # List to store all figure information from floats-group

        # Create a section index for faster lookup
        self.section_index = {}
        for i, section_name in enumerate(self.sections.keys()):
            self.section_index[section_name] = i

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

    def get_section(self, section_name, include_figures=False, figures_placement="end"):
        """
        Generate text for a specific section with optional figure captions.

        Args:
            section_name (str): The name of the section to retrieve
            include_figures (bool): Whether to include figure captions in the output
            figures_placement (str): Where to place figures - 'end' (at section end),
                                    'inline' (at references), or 'separate' (as a separate text)

        Returns:
            str or tuple: The formatted section text, or a tuple of (section_text, figures_text)
                          if figures_placement is 'separate'
        """
        # Check if the section exists
        section_key = section_name.lower()
        if section_key not in self.sections:
            return f"Section '{section_name}' not found."

        section_str = ""
        figures_str = ""

        # Add section title and content
        section_str += section_name + "\n"
        section_str += self.sections[section_key] + "\n"

        # Find figures referenced in this section
        section_figures = []
        if include_figures:
            for figure in self.figures:
                for ref in figure.get("references", []):
                    if ref["section"] == section_key:
                        if figure not in section_figures:
                            section_figures.append(figure)

        # Add inline figures if requested
        if include_figures and figures_placement == "inline" and section_figures:
            for figure in section_figures:
                section_str += "\n--- FIGURE ---\n"
                section_str += f"Figure {figure['label']}: {figure['caption']}\n"
                section_str += "--- END FIGURE ---\n\n"

        # Build separate figures section if needed
        if (
            include_figures
            and (figures_placement == "end" or figures_placement == "separate")
            and section_figures
        ):
            figures_str += "--- FIGURES ---\n\n"
            for figure in section_figures:
                figures_str += "--- FIGURE ---\n"
                figures_str += f"Figure {figure['label']}: {figure['caption']}\n"

                # Include where the figure is referenced in this section
                section_refs = [
                    ref["ref_text"]
                    for ref in figure["references"]
                    if ref["section"] == section_key
                ]
                if section_refs:
                    figures_str += f"Referenced as: {', '.join(section_refs)}\n"

                figures_str += "--- END FIGURE ---\n\n"

        # If separate mode, return both texts
        if include_figures and figures_placement == "separate":
            return section_str, figures_str

        # Otherwise, combine section and figures if needed
        if include_figures and figures_placement == "end":
            section_str += "\n" + figures_str

        return section_str

    def get_body(self, include_figures=False, figures_placement="end"):
        """
        Generate body text with optional figure captions.

        Args:
            include_figures (bool): Whether to include figure captions in the output
            figures_placement (str): Where to place figures - 'end' (all at end),
                                    'inline' (at references), or 'separate' (as a separate section)

        Returns:
            str: The formatted body text, or a tuple of (body_text, figures_text) if figures_placement is 'separate'
        """
        body_str = ""
        figures_str = ""

        # Create a mapping from section name to figures referenced in that section
        if include_figures and figures_placement == "inline":
            section_figures = {}
            for figure in self.figures:
                for ref in figure.get("references", []):
                    section_name = ref["section"]
                    if section_name not in section_figures:
                        section_figures[section_name] = []
                    # Add the figure to the list for this section if not already there
                    if figure not in section_figures[section_name]:
                        section_figures[section_name].append(figure)

        # Process main text
        for key, value in self.sections.items():
            body_str += key + "\n"
            body_str += value + "\n"

            # If inline figures, add them at the end of their referenced section
            if (
                include_figures
                and figures_placement == "inline"
                and key in section_figures
            ):
                for figure in section_figures[key]:
                    body_str += "\n--- FIGURE ---\n"
                    body_str += f"Figure {figure['label']}: {figure['caption']}\n"
                    body_str += "--- END FIGURE ---\n"

            body_str += "\n"

        # Build separate figures section if needed
        if (
            include_figures
            and (figures_placement == "end" or figures_placement == "separate")
            and self.figures
        ):
            figures_str += "--- FIGURES ---\n\n"
            for figure in self.figures:
                figures_str += "--- FIGURE ---\n"
                figures_str += f"Figure {figure['label']}: {figure['caption']}\n"

                # Include where the figure is referenced
                if figure.get("references"):
                    refs = [
                        f"{ref['ref_text']} (in {ref['section']})"
                        for ref in figure["references"]
                    ]
                    figures_str += f"Referenced as: {', '.join(refs)}\n"

                figures_str += "--- END FIGURE ---\n\n"

        # If separate mode, return both texts
        if include_figures and figures_placement == "separate":
            return body_str, figures_str

        # Otherwise, combine body and figures if needed
        if include_figures and figures_placement == "end":
            body_str += "\n\n" + figures_str

        return body_str

    def add_figures_section(self):
        """
        Add a new section to the sections dictionary that contains all figure captions.
        The section will be named 'figures'.

        Returns:
            bool: True if figures were added successfully, False if no figures were found
        """
        if not self.figures:
            return False

        figures_text = "Figures\n\n"

        for figure in self.figures:
            figures_text += "--- FIGURE ---\n"
            figures_text += f"Figure {figure['label']}: {figure['caption']}\n"

            # Include reference information if available
            if figure.get("references"):
                refs = []
                for ref in figure["references"]:
                    refs.append(f"{ref['ref_text']} (in {ref['section']})")
                figures_text += f"Referenced as: {', '.join(refs)}\n"

            figures_text += "--- END FIGURE ---\n\n"

        # Add the figures section to the sections dictionary
        self.sections["figures"] = figures_text

        # Update the section index
        self.section_index["figures"] = len(self.sections) - 1

        return True
