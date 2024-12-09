import os
from bs4 import BeautifulSoup
import json
import logging

def process_html_to_json(input_file):
    # Determine the output file path
    directory = os.path.dirname(input_file)
    base_name, ext = os.path.splitext(os.path.basename(input_file))
    output_file = os.path.join(directory, base_name + '.json')

    # Read the HTML content from the file
    with open(input_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract the topic name
    topic_title_div = soup.find('div', {'id': 'topic-title'})
    topic_title_a = topic_title_div.find('h1').find('a')
    topic_name = topic_title_a.get_text()

    # Initialize a list to hold the posts
    posts = []

    # Find all post divs with classes containing 'crawler-post'
    post_divs = soup.find_all('div', class_='crawler-post')

    for div in post_divs:
        post_data = {}
        
        # Extract username
        creator_span = div.find('span', {'class': 'creator'})
        if creator_span:
            username = creator_span.find('a').find('span', {'itemprop': 'name'}).get_text()
            post_data['username'] = username
        else:
            post_data['username'] = 'Unknown'
        
        # Extract date
        crawler_post_meta = div.find('div', {'class': 'crawler-post-meta'})
        if crawler_post_meta:
            post_infos_span = crawler_post_meta.find('span', {'class': 'crawler-post-infos'})
            if post_infos_span:
                time_tag = post_infos_span.find('time')
                if time_tag and 'datetime' in time_tag.attrs:
                    post_data['date'] = time_tag['datetime']
                else:
                    post_data['date'] = 'Unknown'
                
                position_span = post_infos_span.find('span', {'itemprop': 'position'})
                if position_span:
                    post_data['position'] = int(position_span.get_text())
                else:
                    post_data['position'] = 0
            else:
                post_data['date'] = 'Unknown'
                post_data['position'] = 0
        else:
            post_data['date'] = 'Unknown'
            post_data['position'] = 0
        
        # Extract likes
        likes_div = div.find('div', {'itemprop': 'interactionStatistic'})
        if likes_div:
            likes_span = likes_div.find('span', {'class': 'post-likes'})
            if likes_span:
                likes_text = likes_span.get_text()
                likes_spl = likes_text.split()

                if len(likes_spl) > 0:
                    likes = likes_spl[0]
                else:
                    likes = "0"
                if likes.isdigit():
                    post_data['likes'] = int(likes)
                else:
                    post_data['likes'] = 0
            else:
                post_data['likes'] = 0
        else:
            post_data['likes'] = 0
        
        # Extract content with newline separators
        content_div = div.find('div', {'class': 'post'})
        if content_div:
            # Extract mentions (citations)
            mentions = []
            asides = content_div.find_all('aside', {'class': 'quote'})
            for aside in asides:
                # Extract data-username and data-post
                username = aside.get('data-username', 'Unknown')
                data_post = aside.get('data-post', 'Unknown')
                # Extract the quoted text
                blockquote = aside.find('blockquote')
                if blockquote:
                    quote_text = blockquote.get_text(separator='\n', strip=True)
                else:
                    quote_text = ''
                mentions.append({
                    'username': username,
                    'post_number': data_post,
                    'text': quote_text
                })
                # Remove the aside from the main content
                aside.decompose()
            post_data['mentions'] = mentions
            
            # Extract main content excluding mentions
            main_content = content_div.get_text(separator='\n', strip=True)
            post_data['content'] = main_content
        else:
            post_data['content'] = ''
            post_data['mentions'] = []
        
        # Append the post data to the list
        posts.append(post_data)

    # Prepare the data to save
    data = {
        'topic': topic_name,
        'posts': posts
    }
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    
    print(f'Data has been saved to {output_file}')
    
def process_and_delete_files(directory):
    """
    Processes all files without extension in the given directory and its subdirectories,
    converts them to JSON, and deletes the original files.

    Parameters:
    directory (str): The path to the directory containing files.

    Note:
    - The function logs its actions and errors.
    - Only files without any extension are processed.
    - Original files are deleted only if their JSON counterparts are successfully created.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file has no extension
            if os.path.splitext(file)[1] == '':
                file_path = os.path.join(root, file)
                logging.info(f'Processing {file_path}')
                try:
                    process_html_to_json(file_path)
                    json_file = os.path.splitext(file_path)[0] + '.json'
                    if os.path.exists(json_file):
                        os.remove(file_path)
                        logging.info(f'Deleted {file_path}')
                    else:
                        logging.error(f'JSON file not found for {file_path}')
                except Exception as e:
                    logging.error(f'Error processing {file_path}: {e}')
