import requests
from fake_useragent import UserAgent
from typing import List
from newspaper import Article

class ArticleMethods:

    def get_article(url, min_length=300, max_length=None, language="en", check_spun=False):
        try:
            article = Article(url)
            article.download()-
            article.parse()

            res = len(article.text.split())
            print(res)
            if res > min_length:
                detected_language = detect_language(article.text[:25])
                if detected_language == language:
                    final_article = WaybackArticle(
                        title=article.title,
                        text=article.text,
                        original_url=url,
                        author=article.authors,
                        html=article.html,
                        keywords=article.keywords,
                        topimage=article.top_image,
                        videos=article.movies,
                        wordcount=res,
                    )
                    return final_article
            else:
                return False
        except Exception as e:
            print(e)
            return False