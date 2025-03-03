def find_figure_references(xml_article):
    """Find all figure references in the article text and their locations."""
    figure_refs = {}

    # Find all sections
    sections = xml_article.findall("./body/sec")

    for sec in sections:
        title_elem = sec.find("./title")
        if title_elem is None:
            continue

        section_title = "".join(title_elem.itertext()).lower()

        # Find all figure references (xref elements with ref-type="fig")
        for xref in sec.findall(".//xref[@ref-type='fig']"):
            fig_id = xref.get("rid")
            ref_text = "".join(xref.itertext())

            if fig_id not in figure_refs:
                figure_refs[fig_id] = []

            figure_refs[fig_id].append({"section": section_title, "ref_text": ref_text})

    return figure_refs


from xml.etree import ElementTree as ET

import requests
from ratelimit import limits

from epmc_xml.article import Article


@limits(calls=10, period=1)
def fetch_xml(pmcid):
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
    res = requests.get(url)

    if res.status_code == 500:
        return fetch_xml(pmcid)

    # print(res.content)
    return ET.fromstring(res.content)


def get_abstract(xml_article):
    abstract = xml_article.find("./front/article-meta/abstract")
    if abstract is None:
        return ""
    else:
        paras = abstract.findall("./p")
        section_text = ""
        if len(paras) == 0:
            section_text += " ".join(abstract.itertext())
        for p in paras:
            section_text += " ".join(p.itertext())

        return section_text


def get_title(xml_article):
    title = xml_article.find("./front/article-meta/title-group/article-title")
    if title is None:
        return ""
    else:
        return "".join(title.itertext())


def extract_figures(xml_article):
    """Extract figures from the floats-group in the XML document."""
    figures = []

    # Find the floats-group element
    floats_group = xml_article.find("./floats-group")

    if floats_group is not None:
        # Get all figure elements
        for fig in floats_group.findall("./fig"):
            fig_data = {}

            # Get figure ID
            fig_id = fig.get("id", "unknown")
            fig_data["id"] = fig_id

            # Get figure label
            label_elem = fig.find("./label")
            fig_data["label"] = (
                "".join(label_elem.itertext()) if label_elem is not None else ""
            )

            # Get figure caption
            caption_elem = fig.find("./caption")
            caption_text = ""
            if caption_elem is not None:
                # Get paragraphs within caption
                caption_paras = caption_elem.findall("./p")
                if caption_paras:
                    for p in caption_paras:
                        caption_text += "".join(p.itertext()) + "\n"
                else:
                    # If no paragraphs, get all text
                    caption_text = "".join(caption_elem.itertext())

            fig_data["caption"] = caption_text.strip()

            # Get graphic elements (if present)
            graphic_elems = fig.findall(".//graphic")
            graphics = []
            for graphic in graphic_elems:
                graphics.append(graphic.get("{http://www.w3.org/1999/xlink}href", ""))

            fig_data["graphics"] = graphics

            # Add to the figures list
            figures.append(fig_data)

    return figures


def get_body(xml_article):
    sections = xml_article.findall("./body/sec")
    section_dict = {}

    for sec in sections:
        title_elem = sec.find("./title")
        if title_elem is None:
            continue

        title = "".join(title_elem.itertext())
        section_title = title.lower()

        paras = sec.findall("./p")
        section_text = f"{title}\n"

        if len(paras) == 0:
            section_text += "".join(sec.itertext())
        else:
            for p in paras:
                section_text += "".join(p.itertext())
                section_text += "\n"

        ## find all subsections
        for subsec in sec.findall("./sec"):
            subsection_heading = subsec.find("./title")
            subsection_paras = subsec.findall("./p")

            if subsection_heading is not None:
                subsection_title = "".join(subsection_heading.itertext())
                section_text += subsection_title
                section_text += "\n"

            section_text += "\n".join(
                ["".join(para.itertext()) for para in subsection_paras]
            )
            section_text += "\n"

        section_dict[section_title] = section_text

    # Extract figures from the floats-group
    figures = extract_figures(xml_article)

    # Find figure references in the text
    figure_refs = find_figure_references(xml_article)

    # Add reference information to each figure
    for figure in figures:
        fig_id = figure["id"]
        if fig_id in figure_refs:
            figure["references"] = figure_refs[fig_id]
        else:
            figure["references"] = []

    return section_dict, figures


def get_author_list(xml_article):
    author_list = xml_article.findall("./front/article-meta/contrib-group/contrib/name")
    author_list = [", ".join(author.itertext()) for author in author_list]
    return "; ".join(author_list)


def get_date(xml_article):
    date = xml_article.find("./front/article-meta/pub-date/year")
    if date is None:
        return ""
    else:
        return "".join(date.itertext())


def get_type(xml_article):
    type_elem = xml_article.find(
        "./front/article-meta/article-categories/subj-group/subject"
    )
    if type_elem is None:
        return ""
    return type_elem.text


def article(pmcid):
    xml_article = fetch_xml(pmcid)
    abstract = get_abstract(xml_article)
    title = get_title(xml_article)
    body, figures = get_body(xml_article)
    author_list = get_author_list(xml_article)
    article_type = get_type(xml_article)
    article_date = get_date(xml_article)

    return Article(
        title, author_list, abstract, article_date, body, article_type, figures
    )
