from mongokit import Connection, Document

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

#Begin database schema
class User(Document):
    # __collection__ = 'users'
    # __database__ = 'pharmac'
    structure = {
        'uid': unicode,
        'password': unicode,
        'role': unicode #student, teacher
    }
    indexes = [{ 'fields': ['uid'], 'unique': True }]

class Student(Document):
    # __collection__ = 'students'
    # __database__ = 'pharmac'
    structure = {
        'uid': unicode,
        'tid': unicode
    }
    indexes = [{ 'fields': ['uid'], 'unique': True }]

class Annotation(Document):
    # __collection__ = 'annotations'
    # __database__ = 'pharmac'
    structure = {
        'uid': unicode,
        'did': basestring,
        'annotation': unicode,
        'connection':  unicode
    }

class Document(Document): #This may cause a problme for future generation of coders :D
    # __collection__ = 'documents'
    # __database__ = 'pharmac'
    structure = {
        'uid': unicode,
        'title': unicode,
        'text':  unicode
    }



connection = Connection(MONGODB_HOST, MONGODB_PORT)
connection.register([User, Student, Document, Annotation])
database = connection['pharmac']
