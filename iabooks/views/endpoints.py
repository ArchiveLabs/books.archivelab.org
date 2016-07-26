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


class Collections(MethodView):
    @rest
    def get(self):
        return {'collections': [c.dict() for c in api.Collection.all()]}


class Collection(MethodView):
    @rest
    def get(self, cid):
        return api.Collection.get(cid).dict(books=True, collections=True)


class Search(MethodView):

    @rest
    def get(self):
        query = request.args.get('q')
        page = request.args.get('page', 0)
        limit = int(request.args.get('limit', 0))
        if not query:
            return []        

        books = api.Book.search(query, field="name", limit=50, page=page)
        authors = api.Author.search(query, field="name", limit=5, page=page)
        collections = api.Collection.search(query, field="name", limit=20, page=page)
        sequences = api.Sequence.search(query, field="name", limit=20, page=page)
        author_names = api.AuthorName.search(query, field="name", limit=5, page=page)
        if author_names:
            for author_name in author_names:
                _author = author_name.author
                authors.append(_author)
                print(_author.books)
                books.extend(_author.books)
                print(books)

        return {
            'sequences': [s.dict() for s in sequences],
            'collections': [c.dict() for c in collections],
            'books': [b.dict() for b in list(set(books))],
            'authors': [a.dict() for a in list(set(authors))]
        }


# The following endpoints should be in their own service -- FE, not API

class Home(MethodView):
    def get(self):
        return render_template('index.html')


class Map(MethodView):
    def get(self):
        return render_template('map.html')


class MapJson(MethodView):
    @rest
    def get(self):
        data = {'children': [], "name": "Collections"}
        collections = [c for c in api.Collection.all() if not c.parents]

        def collect(data, cs, level):
            if cs:
                for co in cs:
                    level.append({
                        'id': str(co.id),
                        'name': co.name,
                    })
                    if co.subcollections:
                        level[-1]['children'] = []
                        _level = level[-1]['children']
                        collect(data, co.subcollections, level=_level)
                    else:
                        level[-1]['value'] = 100
            return data
        return collect(data, collections, data['children'])


class Admin(MethodView):
    def get(self):
        authors = [a.dict(names=True, books=True) for a in api.Author.all()]
        books = sorted([b.dict() for b in api.Book.all()],
                       key=lambda b: b['id'], reverse=True)
        seqs = [s.dict() for s in api.Sequence.all()]
        return render_template(
            'admin.html', authors=authors, books=books, seqs=seqs)


class SequencesPage(MethodView):

    def get(self, sid=None):
        if sid:
            return render_template('sequence.html', sequence=api.Sequence.get(sid))
        sequences = [s.dict() for s in api.Sequence.all()]
        return render_template('sequences.html', sequences=sequences, len=len)


    def post(self):
        pass


class AuthorPage(MethodView):

    def get(self, aid=None):
        if aid:
            return render_template('author.html', author=api.Author.get(aid))
        authors = [author.dict(books=True) for author in api.Author.all()]
        return render_template('authors.html', authors=authors, len=len)

    @rest
    def post(self):
        i = request.form
        olid = i.get('olid')
        name = i.get('name')

        try:
            a = api.Author.get(name=name)
        except:
            a = api.Author(name=name, olid=olid)
            a.create()

        aka = i.get('aka')
        if aka:
            for alias in aka.split(','):
                an = api.AuthorName(name=alias.strip(), author_id=a.id)
                an.create()
                a.names.append(an)
            a.save()                

        book_ids = i.get('bids')
        if book_ids:
            book_ids = [int(b) for b in i.get('bids', None).replace(' ', '').split(',')]
            for bid in book_ids:
                a.books.append(api.Book.get(bid))
            a.save()
        return a.dict()


class BookPage(MethodView):
    def get(self, archive_id):
        # get all sequences containing this book
        ## get all books following this book in a sequence
        # get all collections containing this book

        book = api.Book.get(archive_id=archive_id)
        author_ids = ', '.join(str(int(a.id)) for a in book.authors)
        return render_template(
            'book.html', book=book, aids=author_ids)

    @rest
    def post(self):
        i = request.form
        archive_id = i.get('archive_id')
        name = i.get('name')
        desc = i.get('description')

        try:
            b = api.Book.get(archive_id=archive_id)
        except:
            b = api.Book(archive_id=archive_id)
            b.create()

        author_ids = i.get('aids')
        if author_ids:
            author_ids = [a.strip() for a in author_ids.split(',')]
            for aid in author_ids:
                b.authors.append(api.Author.get(aid))
        if name:
            b.name = name
        if desc:
            from sqlalchemy.orm.attributes import flag_modified
            b.data[u'description'] = desc
            flag_modified(b, 'data')
        b.save()
        return b.dict()
                


class Endpoints(MethodView):
    def get(self):
        return ''


class Favicon(MethodView):
    def get(self):
        return ''


urls = (
    '/v1', Endpoints,
    '/favicon.ico', Favicon,
    '/collections/<cid>', Collection,
    '/collections', Collections,
    '/search', Search,
    '/map.json', MapJson,
    '/map', Map,
    '/admin', Admin,
    '/b/<archive_id>', BookPage,
    '/a/<aid>', AuthorPage,
    '/a', AuthorPage,
    '/s', SequencesPage,
    '/b', BookPage,
    '/', Home
)
