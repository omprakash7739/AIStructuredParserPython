import asyncio
import os
from dotenv import load_dotenv
from llama_parse import LlamaParse
from llama_index.core import Document
from llama_index.readers.web import SimpleWebPageReader

from src.utils.dataextractor import extract_urls, download_file_from_url

load_dotenv()


parser = LlamaParse(
    api_key=os.environ['LLAMA_CLOUD_API_KEY'],
    result_type='markdown',
    gpt4o_mode=True,
    gpt4o_api_key=os.environ['OPENAI_API_KEY']
)



def is_not_empty(n):
   return len(n) > 0


async def parse_downloaded_file(file_path):
    print('parsing file stored at path: ', file_path)
    docs= await parser.aload_data(file_path)
    print('parsing complete...for file: ', file_path)
    os.remove(file_path)
    print('local file deleted...', file_path)
    return docs


async def parse_document_from_web_url(web_url: str):
    """
    This method parse web content available at the web url.
     along with that it also parse any images or pdf attached in web source script
    :param web_url: any valid web url
    :return: LlamaParse object
    """

    print(f'started crawling data from url {web_url}')

    text_documents = SimpleWebPageReader(html_to_text=True).load_data(urls=[web_url])
    html_documents = SimpleWebPageReader().load_data([web_url])

    print('web scraping completed...')
    urls = list(filter(is_not_empty, extract_urls(html_documents[0].text)))
    print('fetching data from image or file content received as part of the web url....', urls)

    final_documents = []
    # final_documents.extend(text_documents)
    parsing_tasks = []
    text_doc = "\n\n".join([d.get_content() for d in text_documents])
    final_documents.append(Document(text=text_doc))

    for url in urls:
        file_path = download_file_from_url(url)
        print(f'downloaded data from url {url}')
        parsing_tasks.append(parse_downloaded_file(file_path))

    parsing_results = await asyncio.gather(*parsing_tasks)
    print('finished crawling data from url: ', web_url)

    for doc in parsing_results:
        text_doc = "\n\n".join([d.get_content() for d in doc])
        final_documents.append(Document(text=text_doc))

    return final_documents

