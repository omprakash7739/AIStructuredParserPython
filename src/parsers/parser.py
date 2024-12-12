import os
import re

from dotenv import load_dotenv
from enum import Enum
import asyncio

from llama_parse import LlamaParse
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex

from src.parsers.webparser import parse_document_from_web_url
from src.prompts.prompt_library import build_parsing_prompt
from src.utils.dataextractor import download_file_from_url
from src.utils.objectmapper import find_and_merge_json_objects_info_one

load_dotenv()

parser = LlamaParse(
    api_key=os.environ['LLAMA_CLOUD_API_KEY'],
    result_type='markdown',
    gpt4o_mode=True,
    gpt4o_api_key=os.environ['OPENAI_API_KEY']
)


class UrlType(Enum):
    FILE_PATH = 'file path'
    WEB_URL = 'web url'
    PDF_URL = 'pdf url'
    IMAGE_URL = 'image url'
    UNKNOWN = 'unknown'


def check_url_type(url):
    """
    This method checks if the url type is valid. and categorise it into image url pdf url or any valid web url
    :param url: any valid url
    :return: URL type enum
    """
    # Regular expressions for different types of URLs
    image_regex = re.compile(r'\.(jpg|jpeg|png|gif|bmp|tiff|svg|webp|ico)$', re.IGNORECASE)
    pdf_regex = re.compile(r'\.pdf$', re.IGNORECASE)
    webpage_regex = re.compile(r'^(https?:\/\/)?([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,}.*$', re.IGNORECASE)

    # Check for local file path (Windows and Unix-like)
    if os.path.isfile(url) or re.match(r'^[a-zA-Z]:\\.*$', url) or re.match(r'^\/.*$', url):
        return UrlType.FILE_PATH

    if image_regex.search(url):
        return UrlType.IMAGE_URL
    elif pdf_regex.search(url):
        return UrlType.PDF_URL
    elif webpage_regex.match(url):
        return UrlType.WEB_URL
    else:
        return UrlType.UNKNOWN



async def parse_document_from_file(file_path: str):
    """
    This method use LLamaIndex to parse the document from file path.
    :param file_path: any valid local file path
    :return: LlamaIndex document
    """

    print('parsing data from file input.....')
    return await parser.aload_data(file_path)


async def parse_document_from_remote_resource_location(url: str):
    """
    This method use LLamaIndex to parse the document from remote resource location.
    :param url: any valid remote resource url
    :return: LlamaIndex document
    """

    print('Starting file download...')
    local_file_storage_path = download_file_from_url(url)
    print(f'downloading successful from remote resource url {url}')
    documents = await parser.aload_data(local_file_storage_path)

    os.remove(local_file_storage_path)
    print('downloaded file removed from storage...')
    return documents


async def parse_documents_from_url(url: str):
    """
    This method use LLamaIndex to parse the documents from url.
    :param url: any valid remote url or local file path
    :return: LlamaIndex document
    """

    url_type = check_url_type(url)

    print('confirmed url type is {}'.format(url_type.value))

    if url_type == UrlType.UNKNOWN:
        raise Exception("This url type is not supported as of now")
    elif url_type == UrlType.FILE_PATH:
        return await parse_document_from_file(url)
    elif url_type == UrlType.PDF_URL or url_type == UrlType.IMAGE_URL:
        return await parse_document_from_remote_resource_location(url)
    elif url_type == UrlType.WEB_URL:
        return await parse_document_from_web_url(url)


def parse_and_fetch_structured_output_from_file_or_url(file_or_url_path: str,
                                                       output_structure_json_path: str,
                                                       example_valid_putput_json_path: str):
    """
    This method use LLamaIndex to parse the structured output from file or images/web/pdf located at remote ulr
    :param example_valid_putput_json_path: provide example valid structured outpout json file
    :param output_structure_json_path: provide output structure json file. This will be the format of example structured output
    :param file_or_url_path: file or url path for which the structured output should be fetched
    :return: LlamaIndex query engine response
    """

    if file_or_url_path is None:
        raise Exception('valid file_path must be provided')


    documents = asyncio.run(parse_documents_from_url(file_or_url_path))


    print('Data collection successful. Now parsing and extracting required structured data...')

    node_parser = MarkdownElementNodeParser(llm=OpenAI(model='gpt-4o', temperature=0), num_workers=4)
    nodes = node_parser.get_nodes_from_documents(documents=documents)
    base_nodes, objects = node_parser.get_nodes_and_objects(nodes)

    print('Node & objects created successfully...proceeding with index creation...')

    recursive_index = VectorStoreIndex(nodes=base_nodes, objects=objects)

    generated_prompt = build_parsing_prompt(output_structure_json_path, example_valid_putput_json_path)

    print('Index creation successful...now processing actual query...')

    """
    This step is require to find restaurant name correctly
    """
    compact_response = recursive_index.as_query_engine(
        llms=OpenAI(model='gpt-4o', temperature=0.2),
        similarity_top_k=10000,
        response_mode="compact_accumulate"
    ).query(generated_prompt)

    print('compact restaurant menu items parsed..converting into single json structure...')

    compact_json_response = find_and_merge_json_objects_info_one(compact_response.response)


    """
    This step is require to find all the menu items name and nutrition information correctly
    """

    print('Parsing detailed menu & nutrition information ...')
    detailed_menus_response = recursive_index.as_query_engine(
        llms=OpenAI(model='gpt-4o', temperature=0.2),
        similarity_top_k=1000000,
        response_mode="accumulate"
    ).query(generated_prompt)

    print('Detailed menus parsed... converting it into single json structure...')

    detailed_menu_json_response = find_and_merge_json_objects_info_one(detailed_menus_response.response)

    compact_json_response['items'] = detailed_menu_json_response['items']

    return compact_json_response
