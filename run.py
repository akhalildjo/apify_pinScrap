import time
import requests
import tweepy
import cv2
import numpy as np
import os
import uuid
from bs4 import BeautifulSoup
from requests import get
from pyuploadcare import File, conf
from pyuploadcare import Uploadcare
import feedparser
from dotenv import load_dotenv
import logging


# Charge variables from .env file
load_dotenv()

# logging configuration 
logging.basicConfig(
    filename="/pinterest_scrap/logs/scrap.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
)

# Enter your Uploadcare API key and secret
uploadcare = Uploadcare(public_key=os.environ.get('UC_PUB_KEY'), secret_key=os.environ.get('UC_SECRET_KEY'))

# Enter your Twitter API credentials
consumer_key = os.environ.get('consumer_key')
consumer_secret = os.environ.get('consumer_secret')
access_token = os.environ.get('access_token')
access_token_secret = os.environ.get('access_token_secret')

# Authenticate with the Twitter API
auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
api = tweepy.API(auth)

# Set the URL of the Pinterest boards you want to track
board_url = os.environ.get('moujinh0')
board_url2 = os.environ.get('univers')

# Parse the RSS feed for the Pinterest boards
rss = feedparser.parse(board_url + '.rss')
rss2 = feedparser.parse(board_url2 + '.rss')

# Get the published date and title of the last entry in the first RSS feed
last_entry_description = rss.entries[0].description
last_entry_title = rss.entries[0].title

last_entry_description2 = rss2.entries[0].description
last_entry_title2 = rss2.entries[0].title

# Set the name of the Twitter account you want to tweet from withouth @
twitterAcc = "dy_mjnho"

while True:
    
    logging.info('Checking for new images...')
    # Parse the RSS feed again
    rss = feedparser.parse(board_url + '.rss')
    rss2 = feedparser.parse(board_url2 + '.rss')

    # Check if a new entry has been added to the feed
    if rss.entries[0].description != last_entry_description or rss.entries[0].title != last_entry_title:
        logging.info('New image from Moujinh0 detected, parsing RSS feed...')
        # Update the published date and title of the last entry
        
        last_entry_description = rss.entries[0].description
        last_entry_title = rss.entries[0].title

        # Get the URL of the new image
        image_url = rss.entries[0].link
        
        # Download the image
        response = requests.get(image_url)
        image_data = response.content
        
        # Parse the HTML page
        soup = BeautifulSoup(image_data, 'html.parser')

        # Find the <img> element containing the image
        img_element = soup.find('img')

        # Get the 'src' attribute of the <img> element, which contains the URL of the image file
        image_url = img_element['src']

        # Download the image file
        response = requests.get(image_url)
        image_data = response.content
        
        # Generate a unique filename for the image
        image_filename = str(uuid.uuid4()) + '.jpg'
        print('Image name is ' + image_filename + '')

        
        # Save the image to a local file
        with open(image_filename, 'wb') as f:
            f.write(image_data)

        # Load the image into memory
        image = cv2.imread(image_filename)

        # Resize the image to 1080p
        image = cv2.resize(image, (1920, 1080))

        # Encode the image as a JPEG
        _, image_data = cv2.imencode('.jpg', image)
        
        logging.info('Image downloaded, uploading to Uploadcare...')
        # Open the image file
        with open(image_filename, 'rb') as f:
            # Upload the image file to Uploadcare
            ucare_file: File = uploadcare.upload(f)


        # Get the URL of the uploaded image
        uploaded_image_url = ucare_file.cdn_url
        logging.info('Image uploaded to Uploadcare, URL is ' + uploaded_image_url + '')
        
        logging.info('Uploading image to Twitter...')
        # Upload the image file to Twitter
        media = api.media_upload(image_filename)
        # delete the image from the local storage
        os.remove(image_filename)
        # Tweet the image
        api.update_status(status=last_entry_title, media_ids=[media.media_id])
        # if image has been tweeted, display a message of the tweet
        logging.info('Image uploaded to Twitter, tweet URL is https://twitter.com/' + twitterAcc + '/status/' + str(media.media_id) + '')

        
        

    if rss2.entries[0].description != last_entry_description2 or rss2.entries[0].title != last_entry_title2:
        logging.info('New image from Univers detected, parsing RSS feed...')
        # Update the published date and title of the last entry
        
        last_entry_description2 = rss2.entries[0].description
        last_entry_title2 = rss2.entries[0].title

        # Get the URL of the new image
        image_url = rss2.entries[0].link
        
        # Download the image
        response = requests.get(image_url)
        image_data = response.content
        
        # Parse the HTML page
        soup = BeautifulSoup(image_data, 'html.parser')

        # Find the <img> element containing the image
        img_element = soup.find('img')

        # Get the 'src' attribute of the <img> element, which contains the URL of the image file
        image_url = img_element['src']

        # Download the image file
        response = requests.get(image_url)
        image_data = response.content
        
        # Generate a unique filename for the image
        image_filename = str(uuid.uuid4()) + '.jpg'
        logging.info('Image name is ' + image_filename + '')

        
        # Save the image to a local file
        with open(image_filename, 'wb') as f:
            f.write(image_data)

        # Load the image into memory
        image = cv2.imread(image_filename)

        # Resize the image to 1080p
        image = cv2.resize(image, (1920, 1080))

        # Encode the image as a JPEG
        _, image_data = cv2.imencode('.jpg', image)
        
        logging.info('Image downloaded, uploading to Uploadcare...')
        # Open the image file
        with open(image_filename, 'rb') as f:
            # Upload the image file to Uploadcare
            ucare_file: File = uploadcare.upload(f)
        
    

        # Get the URL of the uploaded image
        uploaded_image_url = ucare_file.cdn_url
        logging.info('Image uploaded to Uploadcare, URL is ' + uploaded_image_url + '')
        
        logging.info('Uploading image to Twitter...')
        # Upload the image file to Twitter
        media = api.media_upload(image_filename)
        # delete the image from the local storage
        os.remove(image_filename)
        # Tweet the image
        api.update_status(status=last_entry_title2, media_ids=[media.media_id])
        # if image has been tweeted, display a message of the tweet
        logging.info('Image uploaded to Twitter, tweet URL is https://twitter.com/' + twitterAcc + '/status/' + str(media.media_id) + '')

    # to check for new images every 5 seconds
    time.sleep(5)



    