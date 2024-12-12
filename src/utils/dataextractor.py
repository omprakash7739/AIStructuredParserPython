import os
import re
import urllib.request
from urllib.parse import urlparse


def download_file_from_url(url: str):
    parsed_url = urlparse(url)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": f"{parsed_url.scheme}://{parsed_url.netloc}"  # Optional: set a referer if needed
    }

    url_string_tokens = url.split('/')
    file_name = url_string_tokens[len(url_string_tokens) - 1]
    local_file_storage_path = os.getcwd() + '/' + file_name

    # Create a request object with the specified headers
    request = urllib.request.Request(url, headers=headers)
    # Use urlopen to open the URL with the request object
    with urllib.request.urlopen(request) as response:
        # Read the response and write it to a file
        with open(local_file_storage_path, "wb") as out_file:  # Change the filename as needed
            out_file.write(response.read())

        print('File downloaded.')

    return local_file_storage_path




def extract_urls(text):
    # Regular expression pattern for markdown links and direct URLs for images and PDFs
    pattern = r'$$.*?$$]$(https?://[^\s]+?\.(?:jpg|jpeg|png|gif|pdf))$|https?://[^\s]+?\.(?:jpg|jpeg|png|gif|pdf)'

    # Find all markdown and direct URLs
    matches = re.findall(pattern, text)

    # Extract URLs from the matches
    urls = [match for match in matches]

    # Additional regex to find direct URLs in plain text
    plain_text_pattern = r'https?://[^\s]+?\.(?:jpg|jpeg|png|gif|pdf)'
    plain_text_matches = re.findall(plain_text_pattern, text)

    # Combine and remove duplicates
    urls.extend(plain_text_matches)
    return list(set(urls))
