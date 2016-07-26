#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    api/books.py
    ~~~~~~~~~~~~~
    Pragma API

    :copyright: (c) 2015 by mek.
    :license: see LICENSE for more details.
"""

from random import randint
from datetime import datetime
import requests
import internetarchive as ia
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import Column, Unicode, BigInteger, Integer, \
    Unicode, DateTime, ForeignKey, Table, exists, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm.exc import ObjectDeletedError
from sqlalchemy.orm import relationship
from api import db, engine, core


collections_collections = Table(
    'collections_collections', core.Base.metadata,
    Column('id', BigInteger, primary_key=True),
    Column('parent_id', BigInteger, ForeignKey('collections.id'), nullable=False),
    Column('child_id', BigInteger, ForeignKey('collections.id'), nullable=False),
    Column('created', DateTime(timezone=False), default=datetime.utcnow,
           nullable=False)
)


book_collections = Table(
    'book_collections', core.Base.metadata,
    Column('id', BigInteger, primary_key=True),       
    Column('collection_id', BigInteger, ForeignKey('collections.id'), nullable=False),
    Column('book_id', BigInteger, ForeignKey('books.id'), nullable=False),
    Column('created', DateTime(timezone=False), default=datetime.utcnow,
           nullable=False)
)

book_authors = Table(
    'book_authors', core.Base.metadata,
    Column('id', BigInteger, primary_key=True),       
    Column('author_id', BigInteger, ForeignKey('authors.id'), nullable=False),
    Column('book_id', BigInteger, ForeignKey('books.id'), nullable=False),
    Column('role', Unicode),  # author? translator?
    Column('created', DateTime(timezone=False), default=datetime.utcnow,
           nullable=False)
)

book_sequences = Table(
    'book_sequences', core.Base.metadata,
    Column('id', BigInteger, primary_key=True),       
    Column('sequence_id', BigInteger, ForeignKey('sequences.id'), nullable=False),
    Column('book_id', BigInteger, ForeignKey('books.id'), nullable=False),
    Column('created', DateTime(timezone=False), default=datetime.utcnow,
           nullable=False)
)


class Collection(core.Base):

    __tablename__ = "collections"

    id = Column(BigInteger, primary_key=True)
    name = Column(Unicode, nullable=False, unique=True)
    data = Column(JSON)
    history = Column(JSON) 
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)

    books = relationship('Book', secondary=book_collections, backref="collections")
    subcollections = relationship('Collection', secondary=collections_collections,
                                  primaryjoin=id==collections_collections.c.parent_id,
                                  secondaryjoin=id==collections_collections.c.child_id,
                                  backref="parents")


    def add_book(self, archive_id):
        try:
            b = Book.get(archive_id=archive_id)
        except:
            b = Book(archive_id=archive_id)
            b.create()
        self.books.append(b)
        self.save()


    def dict(self, books=False, collections=False):
        co = super(Collection, self).dict()
        if books:
            co['books'] = [b.dict() for b in self.books]
        if collections:
            co['subcollections'] = [sc.dict() for sc in self.subcollections]
        return co


class Author(core.Base):

    __tablename__ = "authors"

    id = Column(BigInteger, primary_key=True)
    olid = Column(Unicode, nullable=False, unique=True)  # openlibrary
    #grid = Column(Unicode, nullable=True, unique=True)  # goodreads
    name = Column(Unicode, nullable=False)
    data = Column(JSON)
    history = Column(JSON) 
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)

    books = relationship('Book', secondary=book_authors, backref="authors")

    def dict(self, names=False, books=False):
        author = super(Author, self).dict()
        author['name'] = self.name
        if books:
            author['books'] = [book.id for book in self.books]
        if names:
            author['names'] = [an.name for an in self.names]
        return author


class AuthorName(core.Base):

    __tablename__ = "author_names"

    id = Column(BigInteger, primary_key=True)
    author_id = Column(BigInteger, ForeignKey('authors.id'), nullable=False)
    name = Column(Unicode)

    author = relationship('Author', foreign_keys=[author_id], backref="names",
                          primaryjoin="AuthorName.author_id==Author.id")


class Book(core.Base):

    __tablename__ = "books"

    id = Column(BigInteger, primary_key=True)
    archive_id = Column(Unicode, nullable=False, unique=True)
    #olid = Column(Unicode, unique=True)  # openlibrary
    #grid = Column(Unicode, unique=True)  # goodreads
    #asin = Column(Unicode, unique=True)  # amazon
    name = Column(Unicode)
    cover_url = Column(Unicode)
    data = Column(JSON)
    history = Column(JSON) 
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)

    def create_pre_hook(self):
        print("prehook")
        self.data = ia.get_item(self.archive_id).metadata
        self.name = self.data.get('title')
        self.cover_url = 'https://archive.org/services/img/' + self.archive_id

    def dict(self):
        book = super(Book, self).dict()
        book['authors'] = [a.dict() for a in self.authors]
        book['collections'] = [c.name for c in self.collections]
        book['sequences'] = [s.name for s in self.sequences]
        return book


class Sequence(core.Base):

    """TODO: Create custom IIIF manifests based on the information inside `data` json"""

    __tablename__ = "sequences"

    id = Column(BigInteger, primary_key=True)
    name = Column(Unicode, unique=True)
    order = Column(JSON)  # Order of books in sequence
    data = Column(JSON)
    history = Column(JSON) 
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)

    books = relationship('Book', secondary=book_sequences,
                         backref="sequences")

    def dict(self):
        seq = super(Sequence, self).dict()
        seq['books'] = [book.dict() for book in self.books]
        return seq


class Users(core.Base):

    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    email = Column(Unicode)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)


# Contest (downvote) a sequence or collection, fork

collections = {"Language Learning": [], "Survival": [], "Greek Classics": [], "Children's Books": [],
               "Principles of Design": [], "Magazines & Periodicals": [], "Revolutionary Research": [],
               "Modern Non-fiction": [
                   "gonetomorrow00bant", "scarecrow00mich",
                   "roughjustice00jack", "runninghot00jayn"
               ], "Textbooks": {
                   "Security": ["crackingdessecre00elec"],
                   "Mathematics": ["firstyearalgebra00well",
                                   "fishsarithmeticn02fish"
                               ],
                   "Psychology": [],
                   "Science": {
                       "Physics": [],
                       "Biology": []
                   }
               }, "Historical": [],
               "Military Treatise & Tactics": ["artofwaroldestmi00suntuoft"],
               "Self Improvement": [], "Poetry": [],
               "American Classics": ["worksofcharlesdd04dick"],
               "Literary Compilations": ["masterpiecesofwo00gild"],
               "Poetry": ["worksofedgaralle01poee"],
               "Reference Books": ["ourwonderworldli07chic"],
               "Craftwork": ["ourwonderworldli07chic"],
               "Religious Texts": [],
               "Plays": []
           }


def create_tables():
    Book.metadata.create_all(engine)


def add_content(cs=None, parent=None):
    cs = cs or collections    
    for key in cs:
        c = Collection(name=key)
        c.create()

        if parent:
            parent.subcollections.append(c)
            parent.save()

        if type(cs[key]) is dict:
            add_content(cs[key], parent=c)
        else:
            for book_id in cs[key]:
                try:
                    b = Book.get(archive_id=book_id)
                except:
                    b = Book(archive_id=book_id)
                    b.create()
                c.books.append(b)
                c.save()


def build():
    create_tables()
    add_content()
