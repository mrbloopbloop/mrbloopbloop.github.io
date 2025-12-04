#! /usr/bin/env python3

from bs4 import BeautifulSoup
from markdown import markdown
from pathlib import Path

articles = dict()

def getHtml(path: Path) -> BeautifulSoup:
    html = None
    with path.open() as f:
        html = BeautifulSoup(f.read(),"html.parser")
    return html


def getMarkdownString(path: Path) -> str:
    with path.open() as f:
        return f.read()

def insertMarkdown(parser: BeautifulSoup, md: str, selector: str = "article") -> str:
    mdHtml = BeautifulSoup(markdown(md), "html.parser")
    title = mdHtml.find("h1").get_text()
    parser.find(selector).insert(1, mdHtml)
    parser.find("title").string = title
    return parser

def writeHtml(path:Path, html:str) -> None:
    with path.open('w') as f:
        f.write(str(html))

def processArticle(htmlPath: Path, mdPath: Path, templatePath: Path) -> None:
    templateHtml = getHtml(templatePath)
    mdString = getMarkdownString(mdPath)
    htmlString = insertMarkdown(templateHtml, mdString)
    articles[htmlPath] = htmlString.find('article').h1.get_text()
    writeHtml(htmlPath, htmlString)

def generateArticleIndex(htmlPath: Path, templatePath: Path) -> None:
    html = getHtml(templatePath)
    article = html.find("article")
    tmp = BeautifulSoup("<h1>Articles</h1>", "lxml")
    article.insert(1, tmp.html.body.h1)
    tmp = BeautifulSoup("<ul></ul>", "lxml")
    ul = tmp.html.body.ul
    for path, title in articles.items():
        htmlString = f'<li><a href={str(path.relative_to(htmlPath))}>{title}</a></li>'
        item = BeautifulSoup(htmlString, "lxml")
        item = item.html.body.li
        ul.insert(1, item)
    article.insert(2, ul)
    writeHtml(htmlPath / Path("index.html"), str(html))

        


def main():
    templatePath = Path('./templates/article.html')
    mdPath = Path('./md/articles')
    htmlPath = Path('./html/articles')

    if not mdPath.exists():
        print(f'{mdPath} does not exist!')
        exit()
    
    for path in mdPath.iterdir():
        if path.is_dir():
            continue
        if path.suffix == '.md':
            newPath = htmlPath / path.relative_to(mdPath).with_suffix('.html')
            articles[newPath] = None
            print(f'Processing article [{path}]...  ', end='')
            processArticle(
                    newPath,
                    path,
                    templatePath)
            print('[OK!]')

    generateArticleIndex(htmlPath, templatePath)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
