#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    app.py
    ~~~~~~

    :copyright: (c) 2015 by Mek.
    :license: see LICENSE for more details.
"""

from flask import Flask
from flask.ext.routing import router
from flask.ext.cors import CORS
from views import endpoints
from configs import options, cors, SECRET_KEY


urls = ('', endpoints)
app = router(Flask(__name__), urls)
app.secret_key = SECRET_KEY
cors = CORS(app) if cors else None

if __name__ == "__main__":
    app.run(**options)
