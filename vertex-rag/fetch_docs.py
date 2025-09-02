import re
import requests
from urllib.parse import urljoin, urldefrag
from collections import deque
from bs4 import BeautifulSoup
import pypandoc
from pathlib import Path
import zipfile
import io
import os
import tempfile
import glob
import shutil
import logging

def download_websites(sources,extract_to_dir):
    """
    Fetches content from a list of starting URLs, finds all internal links,
    and then recursively fetches and parses them.
    """
    # Initialize the queue with the list of base URLs
    to_fetch = deque(sources["urls"])
    fetched = set()
    internal_links = set()

    # Regex to find all href attributes
    link_pattern = re.compile(r'href="(.*?)"')

    path = Path(extract_to_dir)
    if "dir" in sources and bool(sources["dir"]):
        path = Path(path/sources["dir"])
    path.mkdir(parents=True, exist_ok=True)

    while to_fetch:
        current_url = to_fetch.popleft()

        # Check if the URL without the fragment has already been fetched
        current_url_base, _ = urldefrag(current_url)

        if current_url_base in fetched:
            continue
        exclude=False;
        if "exclude_pattern" in sources and bool(sources["exclude_pattern"]):
            exclude=re.search(sources["exclude_pattern"], current_url_base)
        if (not current_url_base in sources["urls"]) and  (exclude):
            logging.info(f"Skipping: {current_url_base}")
            continue

        logging.info(f"Fetching: {current_url_base}")

        try:
            response = requests.get(current_url_base, timeout=15)
            if not response.ok:
                logging.info(f"Error fetching {link}: {response.status_code}")
                continue
            # Add the URL without the fragment to the fetched set
            fetched.add(current_url_base)
            contents=response.text
            markdown_content=convert_to_markdown(contents, sources["extract"])            
            file_name=link_to_file(current_url_base, "https://")
            # Open the file in write mode ('w')
            if markdown_content:
                with open(path/file_name, 'w') as file:
                    # Write the text to the file
                    file.write(markdown_content)
                # Find all links in the content
                found_links = link_pattern.findall(contents)

            for link in found_links:
                # Resolve relative URLs
                absolute_link = urljoin(current_url_base, link)

                # Remove the bookmark/fragment part from the URL
                absolute_link_base, _ = urldefrag(absolute_link)

                # Check if the resolved link is an internal link. We check against
                # all base URLs to handle multiple starting points.
                is_internal = any(absolute_link_base.startswith(base_url) for base_url in sources["urls"])

                if is_internal:
                    # Add the link to the queue for fetching
                    to_fetch.append(absolute_link_base)
                    # Add the link to the final set of all collected links
                    internal_links.add(absolute_link_base)

        except requests.exceptions.RequestException as e:
            logging.info(f"Error fetching {current_url_base}: {e}")

    return list(internal_links)

def convert_to_markdown(html_content: str, element: str):
    """
    Parses HTML content, finds all <devsite-content> tags, and converts each
    to a separate Markdown file using pypandoc.
    """
    soup = BeautifulSoup(html_content, 'lxml')
    sections = soup.find_all(element)
    for section in sections:

        # Wrap the section's HTML in a complete document structure for pypandoc
        wrapped_html = f"<html><body>{section.prettify()}</body></html>"

        try:
            # Convert the wrapped HTML string to a Markdown string
            markdown_content = pypandoc.convert_text(wrapped_html, 'gfm', format='html')
            return markdown_content
        except RuntimeError as e:
            logging.info(f"Error converting {section_id}: {e}")

def link_to_file(link: str, prefix: str) -> str:
    """
    Removes a specified prefix from a link and replaces all slashes with underscores.

    Args:
        link: The full URL string.
        prefix: The prefix to remove from the link.

    Returns:
        The formatted string.
    """
    if link.startswith(prefix):
        modified_link = link[len(prefix):]
    else:
        modified_link = link

    file_name = modified_link.replace("/", "_")+ ".txt"
    return file_name

def download_git_repo(source:dict,extract_to_dir:str):
    """
    Downloads a git repository as a zip file, and extracts files matching a pattern.
    """
    for zip_url in source["urls"]:
        logging.info(f"Downloading from: {zip_url}")
        try:
            response = requests.get(zip_url, timeout=30)
            if not response.ok:
                logging.error(f"Error fetching {link}: {response.status_code}")
                continue
            temp_file_path = tempfile.mktemp(suffix=".zip")
            pattern = source["url_pattern"]
            with open(temp_file_path, 'wb') as f:
                f.write(response.content)
            logging.info(f"Downloaded repo saved as {temp_file_path}");
            # Create the extraction directory if it doesn't exist
            extract_to_dir = Path(extract_to_dir)
            logging.info(f"Target Dir: {extract_to_dir}");
            if "dir" in source and bool(source["dir"]):
                extract_to_dir = Path(os.path.join(extract_to_dir,source["dir"]))
            logging.info(f"Target Dir: {extract_to_dir}");
            extract_to_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
                for member in zip_ref.infolist():
                    # Check if the member is a file (not a directory) and matches the pattern
                    if not member.is_dir() and re.search(pattern, member.filename) and not re.search(source["exclude_pattern"], member.filename):
                        if member.filename.endswith('markdown'):
                            member.filename=member.filename.replace('markdown', 'md')
                        logging.info(f"Extracting: {member.filename} to {extract_to_dir}")
                        zip_ref.extract(member, extract_to_dir)
        except requests.exceptions.RequestException as e:
            logging.info(f"Error downloading {zip_url}: {e}")
        except zipfile.BadZipFile:
            logging.info(f"Error: Downloaded file is not a valid zip file from {zip_url}")
        except FileNotFoundError:
            logging.info(f"Error: ZIP file '{temp_file_path}' not found.")
        except Exception as e:
            logging.info(f"An unexpected error occurred: {e}")
