import os
import openai


openai.api_key = os.getenv("OPENAI_API_KEY")


async def summarize(text):
    if (os.environ.get('SPYGLASSES_ENVIRONMENT', None) == 'TEST'):
        return "This is a test summary"

    completion = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Summarize the following article in less than 100 words: {text}"},
        ]
    )
    return completion.choices[0].message["content"]
