from openai import OpenAI, BadRequestError
from trafilatura import fetch_url, extract, feeds
import json
import os


class ArticleTranslator:
    def __init__(self) -> None:
        self.client = OpenAI()
        self.initial_message = """
                You are a translation program. 
                When given a series of paragraphs from an article in english, delimited by triple backticks, translate the paragraphs to chinese. The paragraphs will be in Markdown format, output your results in Markdown without changing images. When filler paragraphs such as: ```- Published```, ```Sign up for our morning newsletter```, ```Your device is not supported``` appear, output nothing.
                When given the summarize() command, summarize the article you've seen so far in at most 100 english words. 
                """
        self.paragraphs = []
        self.messages = [{"role": "system", "content": self.initial_message}]

    def _summarize(self):
        print("summarizing...")

        to_summarise = self.messages
        to_summarise.append({"role": "user", "content": "summarize()"},)
        chat = self.client.chat.completions.create(
            model="gpt-3.5-turbo", messages=to_summarise
        )
        summary = chat.choices[0].message.content
        system_message = self.initial_message
        +  f"\nThe current context of the article is as below: ```{summary}```. "
        + f"\nThe previous paragraph is: ```{self.paragraphs[-1]}```. "
        self.messages = [{"role": "system", "content": system_message}]

    def translate(self, paragraph):
        self.messages.append(
            {"role": "user", "content": f"```{paragraph}```"},
        )

        try:
            chat = self.client.chat.completions.create(
                model="gpt-3.5-turbo", messages=self.messages
            )
            reply = chat.choices[0].message.content
            self.messages.append({"role": "assistant", "content": reply})
            self.paragraphs.append(paragraph)
            return reply
        except BadRequestError:
            self._summarize()
            self.translate(paragraph)


def fetch_article(url):
    downloaded = fetch_url(url)
    result = extract(downloaded, output_format="json", include_images=True)
    return json.loads(result)


def translate_article(article):
    print(f"Translating: {article['title']}")

    translator = ArticleTranslator()
    article['title'] = translator.translate(article['title'])
    paragraphs = article['text'].split("\n")
    translated_paragraphs = []

    for i, paragraph in enumerate(paragraphs):
        print(f"\t{i + 1}/{len(paragraphs)}")
        paragraph = translator.translate(paragraph)
        translated_paragraphs.append(paragraph)

    article['text'] = "\n".join(translated_paragraphs)
    return article


def discover_articles_for_country(country, articles_per_source=10):
    for source in news_feeds[country]:
        articles_list = feeds.find_feed_urls(source["feed"])
        excludes = set(source["excludes"])
        articles_list = [
            article_url for article_url in articles_list if article_url not in excludes]
        for article_url in articles_list[:articles_per_source]:
            article = fetch_article(article_url)
            article = translate_article(article)

            filename = f"articles/{country}/{article['date']}/{article['hostname']}/{article['fingerprint']}.md"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            f = open(filename, "w+")
            f.write(f"## {article['title']} \n\n")
            f.write(article["text"])
            f.close()

# Get newsfeeds from https://rss.feedspot.com/rss_directory/u/
news_feeds = json.load(open("feeds.json"))
discover_articles_for_country("UK", articles_per_source=1)
