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


def extract_figure_captions(section, section_title):
    """Extract figure captions from a section or subsection."""
    figures = {}

    # Find all figures in this section
    for fig in section.findall(".//fig"):
        fig_id = fig.get("id", "unknown")

        # Extract the label if it exists
        label_elem = fig.find("./label")
        label = "".join(label_elem.itertext()) if label_elem is not None else ""

        # Extract the caption
        caption_elem = fig.find("./caption")
        caption_text = ""
        if caption_elem is not None:
            # First try to get paragraph text
            caption_paras = caption_elem.findall("./p")
            if caption_paras:
                for p in caption_paras:
                    caption_text += "".join(p.itertext()) + "\n"
            else:
                # If no paragraphs, get all text
                caption_text = "".join(caption_elem.itertext())

        # Combine label and caption
        figure_content = f"{label}: {caption_text}" if label else caption_text

        if figure_content.strip():
            if section_title not in figures:
                figures[section_title] = {}
            figures[section_title][fig_id] = figure_content

    return figures


def get_body(xml_article):
    sections = xml_article.findall("./body/sec")
    section_dict = {}
    figures_dict = {}

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

        # Extract figures from this section
        section_figures = extract_figure_captions(sec, section_title)
        if section_figures:
            figures_dict.update(section_figures)

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

            # Extract figures from subsections too
            subsection_figures = extract_figure_captions(subsec, section_title)
            if subsection_figures:
                figures_dict.update(subsection_figures)

        section_dict[section_title] = section_text

    return section_dict, figures_dict


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
