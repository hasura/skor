#!/usr/bin/env python3

import socketserver
import threading
import http.server
import json
import queue
from http import HTTPStatus

from sqlalchemy import create_engine
from sqlalchemy.schema import MetaData

respQ = queue.Queue(maxsize=1)

class WebhookHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.end_headers()
    def do_POST(self):
        contentLen = self.headers.get('Content-Length')
        reqBody = self.rfile.read(int(contentLen))
        reqJson = json.loads(reqBody)
        self.log_message(json.dumps(reqJson))
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()
        respQ.put(reqJson)

def startWebserver():
    server_address = ('', 5000)
    httpd = http.server.HTTPServer(server_address, WebhookHandler)
    webServer = threading.Thread(target=httpd.serve_forever)
    webServer.start()
    return httpd, webServer

def assertEvent(q, resp, timeout=5):
    evResp = q.get(timeout=timeout)
    return resp == evResp

def t1Insert(meta):
    t = meta.tables['skor_test_t1']
    return {
        "name": "t1: insert",
        "statement": t.insert().values(c1=1, c2='hello'),
        "resp": {
            'table': 'skor_test_t1',
            'schema': 'public',
            'op': 'INSERT',
            'data': {'c1': 1, 'c2': 'hello'}
        }
    }

def t1Update(meta):
    t = meta.tables['skor_test_t1']
    return {
        "name": "t1: update",
        "statement": t.update().values(c2='world').where(t.c.c1 == 1),
        "resp": {
            'table': 'skor_test_t1',
            'schema': 'public',
            'op': "UPDATE",
            'data': {'c1': 1, 'c2': 'world'}
        }
    }

def t1Delete(meta):
    t = meta.tables['skor_test_t1']
    return {
        "name": "t1: delete",
        "statement": t.delete().where(t.c.c1 == 1),
        "resp": {
            'table': 'skor_test_t1',
            'schema': 'public',
            'op': 'DELETE',
            'data': {'c1': 1, 'c2': 'world'}
        }
    }

def t3Insert(meta):
    t = meta.tables['skor_test_t3']
    return {
        "name": "t3: insert",
        "statement": t.insert().values(c1=1, c2='hello'),
        "resp": {
            'table': 'skor_test_t3',
            'schema': 'public',
            'op': 'INSERT',
            'data': {'c1': 1}
        }
    }

def t3Update(meta):
    t = meta.tables['skor_test_t3']
    return {
        "name": "t3: update",
        "statement": t.update().values(c2='world').where(t.c.c1 == 1),
        "resp": {
            'table': 'skor_test_t3',
            'schema': 'public',
            'op': "UPDATE",
            'data': {'c1': 1}
        }
    }

def t3Delete(meta):
    t = meta.tables['skor_test_t3']
    return {
        "name": "t3: delete",
        "statement": t.delete().where(t.c.c1 == 1),
        "resp": {
            'table': 'skor_test_t3',
            'schema': 'public',
            'op': 'DELETE',
            'data': {'c1': 1}
        }
    }

def t4Insert(meta):
    t = meta.tables['skor_test_t4']
    return {
        "name": "t4: insert",
        "statement": t.insert().values(c1=1, c2='hello', c3='world'),
        "resp": {
            'table': 'skor_test_t4',
            'schema': 'public',
            'op': 'INSERT',
            'data': {'c1': 1, 'c2': 'hello', 'c3': 'world'}
        }
    }

def t4Update(meta):
    t = meta.tables['skor_test_t4']
    return {
        "name": "t4: update",
        "statement": t.update().values(c2='ahoy').where(t.c.c1 == 1),
        "resp": {
            'table': 'skor_test_t4',
            'schema': 'public',
            'op': "UPDATE",
            'data': {'c1': 1, 'c2': 'ahoy'}
        }
    }

def t4Delete(meta):
    t = meta.tables['skor_test_t4']
    return {
        "name": "t4: delete",
        "statement": t.delete().where(t.c.c1 == 1),
        "resp": {
            'table': 'skor_test_t4',
            'schema': 'public',
            'op': 'DELETE',
            'data': {'c1': 1}
        }
    }

tests = [ t1Insert, t1Update, t1Delete
        , t3Insert, t3Update, t3Delete
        , t4Insert, t4Update, t4Delete
        ]

httpd, webServer = startWebserver()

engine = create_engine('postgresql://admin@localhost:5432/skor_test')
meta = MetaData()
meta.reflect(bind=engine)

conn = engine.connect()

for t in tests:
    testParams = t(meta)
    print("-" * 20)
    print("Running Test: {}".format(testParams['name']))
    stmt = testParams['statement']
    conn.execute(stmt)
    print(stmt)
    resp = testParams['resp']
    success = assertEvent(respQ, resp)
    res = "Succeeded" if success else "Failed"
    print("Test result: {}".format(res))

httpd.shutdown()
webServer.join()
