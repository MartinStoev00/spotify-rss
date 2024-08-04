from flask import Flask, Response, request, redirect
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.cElementTree as ET


app = Flask(__name__)


def get_info(id):
    url = f'https://api.spotify.com/v1/shows/{id}/episodes'  # Example endpoint
    client_id = 'client_id'
    client_secret = 'client_secret'

    token_url = 'https://accounts.spotify.com/api/token'

    response = requests.post(token_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })

    token_info = response.json()
    access_token = token_info['access_token']

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get('https://api.spotify.com/v1/shows/2b025hq3gJ17tQdxS3aV43/episodes?offset=0&limit=50',
                            headers=headers)
    episodes = response.json()

    response = requests.get(url, headers=headers)
    episodes = response.json()
    print(episodes)
    episodes = episodes['items']

    r = requests.get(f'https://open.spotify.com/show/{id}', headers=headers)
    if r.status_code != 200:
        return None
    b = r.text
    root = ET.Element("rss")
    root.set("version", "2.0")
    root.set("xmlns:atom", "http://www.w3.org/2005/Atom")
    channel = ET.SubElement(root, "channel")
    channel_title = BeautifulSoup(b, 'html.parser').title.text.replace("| Podcast on Spotify", "")
    ET.SubElement(channel, "title").text = channel_title
    ET.SubElement(channel, "link").text = f"https://open.spotify.com/show/{id}"
    ET.SubElement(channel, "description").text = "Some"
    for elem in episodes:
        try:
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = elem["name"]
            ET.SubElement(item, "link").text = elem["external_urls"]["spotify"]
            ET.SubElement(item, "description").text = elem["description"]
            ET.SubElement(item, "pubDate").text = elem["release_date"]
        except AttributeError:
            break
    return ET.tostring(root, encoding='unicode')


@app.route('/', methods=['GET'])
def search():  # put application's code here
    return '<form action="results"><input type="text" name="id"/></form>'


@app.route('/results/', methods=['GET'])
def page():  # put application's code here
    id = request.args.get('id')
    xml = get_info(id)
    if xml is None:
        return redirect("/")
    return Response(xml, mimetype='text/xml')
