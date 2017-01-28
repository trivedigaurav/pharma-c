from mongokit import Connection, Document

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

#Begin database schema
class Patient(Document):
    # __collection__ = 'patients'
    # __database__ = 'pharmac'
    structure = {
        'uid': unicode,
        'q1': unicode,
        'q2': unicode,
        'q3': unicode
    }
    indexes = [{ 'fields': ['uid'], 'unique': True }]

class Response(Document):
    # __collection__ = 'responses'
    # __database__ = 'pharmac'
    structure = {
        'time': float,
        'answer': unicode,
        'question': unicode,
        'pid': unicode
    }

connection = Connection(MONGODB_HOST, MONGODB_PORT)
connection.register([Patient, Response])
database = connection['pharmac']
