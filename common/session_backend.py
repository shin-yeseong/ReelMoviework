from django.contrib.sessions.backends.base import SessionBase, CreateError
from django.contrib.sessions.exceptions import InvalidSessionKey
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

client = MongoClient('mongodb+srv://jklas187:PI9IWptT59WMOYZF@likemovie.toohv.mongodb.net/?retryWrites=true&w=majority')
db = client['mongodatabase']
session_collection = db['django_sessions']

class SessionStore(SessionBase):
    """
    A MongoDB-backed session store for Django.
    """
    def load(self):
        # 세션 데이터 로드
        try:
            session = session_collection.find_one({'_id': self.session_key})
            if session and 'session_data' in session:
                return self.decode(session['session_data'])
        except Exception as e:
            print(f"Error loading session: {e}")
        return {}

    def create(self):
        # 세션 생성
        while True:
            self.session_key = self._get_new_session_key()
            try:
                session_collection.insert_one({
                    '_id': self.session_key,
                    'session_data': self.encode({}),
                    'expire_date': self.get_expiry_date()
                })
                self.modified = True
                return
            except Exception as e:
                print(f"Error creating session: {e}")
                continue

    def save(self, must_create=False):
        # 세션 저장
        if must_create:
            return self.create()
        session_collection.update_one(
            {'_id': self.session_key},
            {
                '$set': {
                    'session_data': self.encode(self._get_session(no_load=must_create)),
                    'expire_date': self.get_expiry_date()
                }
            },
            upsert=True
        )

    def delete(self, session_key=None):
        # 세션 삭제
        if session_key is None:
            session_key = self.session_key
        session_collection.delete_one({'_id': session_key})
class MongoDBSession(SessionBase):
    def load(self):
        try:
            session = session_collection.find_one({'_id': self._get_session_key()})
            if session and 'session_data' in session:
                return self.decode(session['session_data'])
        except InvalidSessionKey:
            pass
        return {}

    def create(self):
        while True:
            self._session_key = self._get_new_session_key()
            try:
                session_collection.insert_one({
                    '_id': self._session_key,
                    'session_data': self.encode({}),
                    'expire_date': self.get_expiry_date()
                })
                self.modified = True
                return
            except Exception:  # Duplicate key error
                continue

    def save(self, must_create=False):
        if must_create:
            return self.create()
        session_collection.update_one(
            {'_id': self._get_session_key()},
            {
                '$set': {
                    'session_data': self.encode(self._get_session(no_load=must_create)),
                    'expire_date': self.get_expiry_date()
                }
            },
            upsert=True
        )

    def delete(self, session_key=None):
        if session_key is None:
            session_key = self._get_session_key()
        session_collection.delete_one({'_id': session_key})
