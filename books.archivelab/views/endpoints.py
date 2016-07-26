#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    endpoints.py
    ~~~~~~~~~~~~

    :copyright: (c) 2015 by Mek.
    :license: see LICENSE for more details.
"""

from flask import render_template, request
from flask.views import MethodView
from datetime import datetime


class Home(MethodView):
    def get(self):
        return render_template('index.html')


urls = (
    '/', Home
)
