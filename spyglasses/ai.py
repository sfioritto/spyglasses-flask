import os
import openai
import tiktoken
from newspaper import Article

openai.api_key = os.getenv("OPENAI_API_KEY")


class TooLongTextError(Exception):
    pass


def split_text(text, n):
    """Splits the text into n equal parts"""
    length = len(text)
    return [text[i*length // n: (i+1)*length // n] for i in range(n)]


async def recursive_summarize(text, max_tokens=4096):
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")

    # Calculate the number of tokens
    tokens = enc.encode(text)
    num_tokens = len(tokens)

    # If the number of tokens is within the limit, summarize directly
    if num_tokens <= max_tokens:
        completion = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"Summarize the following article in less than 100 words: {text}"},
            ]
        )
        return completion.choices[0].message["content"]

    # If the number of tokens exceeds the limit, split the text into two parts and summarize each part separately
    else:
        summaries = []
        parts = split_text(text, 2)
        for part in parts:
            summary = await recursive_summarize(part, max_tokens)
            summaries.append(summary)
        return await recursive_summarize(' '.join(summaries), max_tokens)


async def summarize(text):
    if (os.environ.get('SPYGLASSES_ENVIRONMENT', None) == 'TEST'):
        return "This is a test summary"
    else:
        return await recursive_summarize(text)


def get_article(document):
    """Checks if the text is an article"""
    article = Article(url='')
    article.set_html(document)
    try:
        article.parse()
    except:
        return None

    # If the article has a title and some text, it might be an article
    if article.title and article.text:
        return article
    else:
        return None
