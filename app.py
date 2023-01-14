from flask import Flask, Response, request, redirect
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.cElementTree as ET


app = Flask(__name__)


def get_info(id):
    year = datetime.now().year
    headers = {'Accept-Encoding': 'identity'}
    root = ET.Element("rss")
    root.set("version", "2.0")
    root.set("xmlns:atom", "http://www.w3.org/2005/Atom")
    channel = ET.SubElement(root, "channel")
    ET.SubElement(channel, "title").text = "Title"
    ET.SubElement(channel, "link").text = "https://www.google.com"
    ET.SubElement(channel, "description").text = "Some"
    r = requests.get(f'https://open.spotify.com/show/{id}', headers=headers)
    if r.status_code != 200:
        return None
    b = r.text
    soup = BeautifulSoup(b, 'html.parser').findAll("div", {"data-testid": "infinite-scroll-list"})
    for elem in soup[0]:
        try:
            title = elem.div.select("div:nth-child(2)")[0].div.contents[0].contents[0].contents[-1]
            link = elem.div.select("div:nth-child(2)")[0].div.contents[0]['href']
            link = 'https://open.spotify.com' + link
            command = 'getp ' + link
            date = str(elem.div.select("div:nth-child(4)")[0].p.contents[0])
            datetime_object = None
            if date.endswith(str(year - 1)) or date.endswith(str(year)):
                datetime_object = datetime.strptime(date, '%b %Y')
            else:
                datetime_object = datetime.strptime(date, '%b %d').replace(year=year)
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = title
            ET.SubElement(item, "link").text = link
            ET.SubElement(item, "description").text = command
            ET.SubElement(item, "pubDate").text = datetime_object.strftime('%a, %d %b %Y 00:00:00')
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


if __name__ == '__main__':
    app.run(debug=True)
