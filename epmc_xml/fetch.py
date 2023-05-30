from xml.etree import ElementTree as ET

import ratelimiter
import requests
from article import Article


@ratelimiter.RateLimiter(max_calls=10, period=1)
def fetch_xml(pmcid):
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
    res = requests.get(url)

    if res.status_code == 500:
        return fetch_xml(pmcid)

    return ET.fromstring(res.content)


def get_abstract(xml_article):
    abstract = xml_article.find("./front/article-meta/abstract/")
    if abstract is None:
        return ""
    else:
        return "".join(abstract.itertext())


def get_title(xml_article):
    title = xml_article.find("./front/article-meta/title-group/article-title")
    if title is None:
        return ""
    else:
        return "".join(title.itertext())


def get_body(xml_article):
    sections = xml_article.findall("./body/sec")
    section_dict = {}
    for sec in sections:
        if len(sec.findall("./p")) == 0:
            section_text = ""
        else:
            section_text = ["".join(para.itertext()) for para in sec.findall("p")][0]
        ## find all subsections
        for subsec in sec.findall("./sec"):
            subsection_heading = subsec.find("title")
            subsection_paras = subsec.findall("p")
            section_text += "".join(subsection_heading.itertext())
            section_text += "".join(
                ["".join(para.itertext()) for para in subsection_paras]
            )

        section_dict[sec.find("./title").text] = section_text

    return section_dict


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
    return xml_article.find(
        "./front/article-meta/article-categories/subj-group/subject"
    ).text


def article(pmcid):
    xml_article = fetch_xml(pmcid)
    abstract = get_abstract(xml_article)
    title = get_title(xml_article)
    body = get_body(xml_article)
    author_list = get_author_list(xml_article)
    article_type = get_type(xml_article)
    article_date = get_date(xml_article)

    return Article(title, author_list, abstract, article_date, body, article_type)
