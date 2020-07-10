import requests
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
parser = HTMLParser()
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'My User Agent 1.0',
}
# cleantext = BeautifulSoup(raw_html, "html.parser").text
a = requests.get("https://www.newindianexpress.com/Entertainment/English/rssfeed/?id=194&getXmlFeed=true", headers=headers)
print(a.content)
tree = ET.ElementTree(ET.fromstring(a.content))
economic_times = list()
root = tree.getroot()
# for item in root.findall('./channel/album/item'):
for item in root.findall('./channel/item'):
    final_dict = {"source": "Indian Express",
                  "images": [],
                  "description": ""}
    for child in item:
        if child.tag == 'pubDate':
            final_dict["datetime"] = child.text
        elif child.tag == 'image':
            final_dict["images"].append(child.text)
        elif child.tag == 'title':
            final_dict["title"] = parser.unescape(child.text)
        elif child.tag == 'story':
            final_dict["description"] = BeautifulSoup(child.text, "html.parser").text



        else:
            final_dict[child.tag] =  parser.unescape(child.text)