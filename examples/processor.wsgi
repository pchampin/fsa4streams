#!/usr/bin/env python

from os.path import dirname
from sys import path
path.append(dirname(dirname(__file__)))

from cgi import FieldStorage
import json

from fsa4streams import FSA

def application(environ, start_response):

    try:
        form = FieldStorage(fp=environ['wsgi.input'], environ=environ)
        structure = form.getvalue("structure")
        events = form.getvalue("events")

        if structure is None or events is None:
            raise ValueError("'structure' and 'events' are required")

        fsa = FSA.from_str(structure)
        if events[0] in '"{[':
            events = json.loads(events)
        else:
            events = events.split(" ")

        matches = fsa.feed_all(events)

        start_response("200 Ok", [
                       ("content-type", "application/json"),
        ])
        return [json.dumps(matches, indent=4)]

    except Exception as ex:
        start_response("400 Error", [
                       ("content-type", "text/html"),
        ])
        return ["<!DOCTYPE html>"
        "<html><head><title>400 Error</title></head>"
        "<body><h1>400 Error: {}</h1><pre>{}</pre>"
        "</html>".format(ex.__class__.__name__, ex.message)]

if __name__ == "__main__":
    import os
    if os.environ.get("AS_WSGI"):
        from wsgiref.simple_server import make_server
        HOST = "localhost"
        PORT = 12345
        HTTPD = make_server(HOST, PORT, application)
        print "Listening on http://%s:%s/" % (HOST, PORT)
        HTTPD.serve_forever()
    else:
        from wsgiref.handlers import CGIHandler
        CGIHandler().run(application)
