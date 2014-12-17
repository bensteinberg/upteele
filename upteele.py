from flask import Flask, render_template
import xml.etree.ElementTree as ET
import requests

app = Flask(__name__)

routes = ['87', '88']

@app.route('/')
def hello_world():
    return render_template("index.html")

@app.route('/davis')
def davis():
    return show_times('2630', "Davis", "Outbound to Teele from Holland St @ Wallace St")

@app.route('/teele')
def teele():
    return show_times('2577', "Teele", "Inbound to Davis from Broadway @ Holland St - Teele Sq")

def get_predictions(xml):
    output = []
    root = ET.fromstring(xml)
    for p in root.iter("prediction"):
        output.append(p.attrib['seconds'])
    return output

def show_times(stop, title, heading):
    url = 'http://webservices.nextbus.com/service/publicXMLFeed?command=predictions&a=mbta&stopId=%s&routeTag=' % stop
    buses = []
    for rt in routes:
        r = requests.get(url + rt)
        if r.status_code == requests.codes.ok:
            ps = get_predictions(r.text)
            for p in ps:
                buses.append((int(p), rt, "%.1f" % (int(p) / 60.0)))
        else:
            print("Couldn't get data")

    return render_template("show.html", b = sorted(buses), s = title, h = heading)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
