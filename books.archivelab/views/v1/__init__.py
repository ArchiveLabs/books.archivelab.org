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
from views import rest, paginate
from datetime import datetime
from api import books as api


class Endpoints(MethodView):
    @rest
    def get(self, uri=None):      
        urlbase = request.base_url
        return dict([(urls[i+1].__name__.split(".")[-1].lower(),
                      urlbase + urls[i])
            for i in range(len(urls))[::2]])


class Collections(MethodView):
    @rest
    def get(self, cid=None):
        if cid:
            return api.Collection.get(cid).dict(books=True)
        return {
            'collections': [c.dict() for c in api.Collection.all()]
        }


class Collection(MethodView):
    @rest
    def get(self, cid):
        collection = api.Collection.get(cid)
        return collection.dict(books=True, collections=True)


class Authors(MethodView):
    @rest
    def get(self, aid=None):
        if aid:
            return api.Author.get(aid).dict(books=True)
        return {
            'authors': [author.dict(books=True) for author in
                        api.Author.all()]
        }


class Sequences(MethodView):
    @rest
    def get(self):
        return {
            'sequences': [s.dict() for s in api.Sequence.all()]
        }


class Books(MethodView):
    @rest
    def get(self, archive_id=None):
        if archive_id:
            return api.Book.get(archive_id=archive_id).dict()
        return {
            'book': [book.dict() for book in 
                     api.Book.all()]
        }


urls = (
    '/collections/<cid>', Collection,
    '/collections', Collections,
    '/authors/<aid>', Authors,
    '/authors', Authors,
    '/sequences', Sequences,
    '/books/<archive_id>', Books,
    '/books', Books,
    '', Endpoints
)
