from urllib.parse import urljoin
import feedparser
import requests
from apify import Actor
from bs4 import BeautifulSoup
import cv2
import uuid
import asyncio

async def main():
    async with Actor:
        # Read the Actor input
        actor_input = await Actor.get_input() or {}
        start_urls = actor_input.get('startUrls', [])
        
        if not start_urls:
            Actor.log.info('No start URLs specified in actor input, exiting...')
            await Actor.exit()

        start_url = start_urls[0].get('url')  # Get the first URL from the list

        rss = feedparser.parse(start_url + '.rss')
        last_entry_description = rss.entries[0].description

        # Infinite loop to keep monitoring the RSS feed
        while True:
            try:
                rss = feedparser.parse(start_url + '.rss')
                current_entry_description = rss.entries[0].description

                # Check if a new entry has been added to the feed
                if current_entry_description != last_entry_description:
                    
                    last_entry_description = current_entry_description
                    last_entry_title = rss.entries[0].title
                    image_url = rss.entries[0].link

                    response = requests.get(image_url)
                    image_data = response.content

                    soup = BeautifulSoup(image_data, 'html.parser')
                    img_element = soup.find('img')
                    image_url = img_element['src']

                    response = requests.get(image_url)
                    image_data = response.content

                    image_filename = str(uuid.uuid4()) + '.jpg'

                    with open(image_filename, 'wb') as f:
                        f.write(image_data)

                    image = cv2.imread(image_filename)
                    image = cv2.resize(image, (1920, 1080))

                    _, image_data = cv2.imencode('.jpg', image)

                    Actor.log.info('Image downloaded')

                    await Actor.push_data(image_data)

            except Exception as e:
                Actor.log.exception(f'Cannot extract data from {start_url}.')

            await asyncio.sleep(5)  # Sleep for 5 seconds before checking the feed again

if __name__ == "__main__":
    asyncio.run(main())
