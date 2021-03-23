from tinydb import TinyDB, Query
import hashlib
import time


class StorageController:
    __instance = None
    db_clients = None
    db_channels = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            cls.db_clients = TinyDB('storage/clients.json')
            cls.db_channels = TinyDB('storage/channels.json')
            return cls.__instance
        return cls.__instance

    @property
    def __get_instance__(self):
        if self.__instance is None:
            self.__instance = object.__new__(self)
            self.db_clients = TinyDB('clients.json')
            self.db_channels = TinyDB('channels.json')
            return self.__instance
        return self.__instance

    def insert(self, data: dict, db):
        """
        Insert new data in the database
        :param db: The database to make the operation
        :param data: The new data to be inserted in the database
        :return: All the documents created
        """
        data['_id'] = self.__generate_hash__()
        db.insert(data)
        return data

    def get_all_documents(self, db):
        """
        Return all the documents stored in the database
        :param db: Specific database to make the operation
        :return: List with the all documents of the database
        """
        return db.all()

    def search(self, id, db):
        """
        Search inside the database based in the document id
        :param id: id of the document to be search
        :param db: Specific database to make the operation
        :return: First match of the search
        """
        query = Query()
        return db.search(query._id == id)[0]

    def update(self, id, data: dict, db):
        """
        Update a specific document in the databse
        :param id: Id of the document to edit
        :param data: Data of the document to be updated
        :param db: Specific database to make the operation
        :return: Id of the document edited
        """
        query = Query()
        db.update(data, query._id == id)
        return id

    def delete(self, id, db):
        """
        Delete a specific document of the database
        :param id: Id of the document to be deleted
        :param db: Specific database to make the operation
        :return: Id of the document deleted
        """
        query = Query()
        db.remove(query._id == id)
        return id

    def __generate_hash__(self):
        """
        Generate a new hash generated with the algorithm sha1 based in the current time of the system
        :return: The firsts 32 characters of the previously generated hash
        """
        hash = hashlib.sha1()
        hash.update(str(time.time()).encode())
        return hash.hexdigest()[:32]