import re


def clean_content(docs: list, stopwords: list):
    """
    :param docs: list of documents
    :param stopwords: list of stopwords
    :return: cleaned documents
    """

    for doc in docs:
        content = doc.page_content
        content = re.sub(r"(@\[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+://\S+)|^rt|http.+?", " ", content)
        content = " ".join([word for word in content.split() if word not in stopwords])
        doc.page_content = content

    return docs
