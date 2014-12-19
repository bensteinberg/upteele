from flask import Flask, render_template, url_for, request
from flask_bootstrap import Bootstrap
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from pytz import timezone

def create_app():
    app = Flask(__name__)
    Bootstrap(app)
    return app

app = create_app()

routes = ['87', '88']

NOERROR = 0
NOARRIVALS = 1
BADRESPONSE = 2
NODATA = 4

errors = { 
    NOARRIVALS:  "no arrivals predicted",
    BADRESPONSE: "bad response from NextBus",
    NODATA:      "couldn't get NextBus data"
}

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
    error = NOERROR
    for rt in routes:
        try:
            r = requests.get(url + rt)
            if r.status_code == requests.codes.ok:
                for p in get_predictions(r.text):
                    buses.append((int(p), rt, "%.1f" % (int(p) / 60.0)))
            else:
                error = error | BADRESPONSE
        except:
            error = error | NODATA

    now = datetime.now(timezone('US/Eastern')).strftime("%Y-%m-%d %H:%M:%S")

    if len(buses) == 0 and error == NOERROR:
        error = NOARRIVALS

    error_msg = None
    for e, m in errors.iteritems():
        if e & error:
            if error_msg:
                error_msg = '; '.join([error_msg, m])
            else:
                error_msg = m[0].upper() + m[1:]

    return render_template("show.html", 
                           b = sorted(buses), 
                           s = title, 
                           h = heading, 
                           t = now,
                           e = error_msg
                       )

if __name__ == '__main__':
    app.run(host='0.0.0.0')
