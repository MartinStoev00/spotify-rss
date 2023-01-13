from flask import Flask, Response
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.cElementTree as ET


app = Flask(__name__)
root = ET.Element("rss")
root.set("version", "2.0")
root.set("xmlns:atom", "http://www.w3.org/2005/Atom")
channel = ET.SubElement(root, "channel")
ET.SubElement(channel, "title").text = "Title"
ET.SubElement(channel, "link").text = "https://www.google.com"
ET.SubElement(channel, "description").text = "Some"
headers = {'Accept-Encoding': 'identity'}


def get_info(id):
    year = datetime.now().year
    r = requests.get(f'https://open.spotify.com/show/{id}', headers=headers)
    b = r.text
    soup = BeautifulSoup(b, 'html.parser').findAll("div", {"data-testid": "infinite-scroll-list"})
    for elem in soup[0]:
        try:
            title = elem.div.select("div:nth-child(2)")[0].div.contents[0].contents[0].contents[-1]
            date = str(elem.div.select("div:nth-child(4)")[0].p.contents[0])
            datetime_object = None
            if date.endswith(str(year - 1)) or date.endswith(str(year)):
                datetime_object = datetime.strptime(date, '%b %Y')
            else:
                datetime_object = datetime.strptime(date, '%b %d').replace(year=year)
            # datetime_object.hour = 0
            # datetime_object.minute = 0
            # datetime_object.second = 0
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = title
            ET.SubElement(item, "pubDate").text = datetime_object.strftime('%a, %d %b %Y 00:00:00')
        except AttributeError:
            break
    return ET.tostring(root, encoding='unicode')


@app.route('/<id>', methods=['GET'])
def hello_world(id):  # put application's code here
    xml = get_info(id)
    return Response(xml, mimetype='text/xml')


if __name__ == '__main__':
    app.run()
