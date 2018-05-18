import pymongo
import pymongo.errors
import requests
import concurrent.futures
from settings import settings, Logger
import datetime
import urllib.parse


HN_TOP_STORIES = 'https://hacker-news.firebaseio.com/v0/topstories.json'

HN_POST_DETAILS = 'https://hacker-news.firebaseio.com/v0/item/{}.json'
HN_POST_LINK = 'https://news.ycombinator.com/item?id={}'
POSTS_LIMIT = 3


class HackerNews:
    def __init__(self):

        _db = settings.db_host.split(':')
        db_host = _db[0]
        db_port = int(_db[1])
        connection_user = ''

        if settings.db_user and settings.db_password:
            db_user = urllib.parse.quote_plus(settings.db_user)
            db_password = urllib.parse.quote_plus(settings.db_password)
            connection_user = f'{db_user}:{db_password}@'

        connection_string = f'mongodb://{connection_user}{db_host}:{db_port}'

        self.db_client = pymongo.MongoClient(connection_string, serverSelectionTimeoutMS=1000, connect=False)

        db_name = settings.db_name

        if not self.db_client:
            raise DBConnectionError('Failed to connect to the database server')

        if not db_name:
            raise DBConfigError('Database name not found in configuration')

        self.db = self.db_client[settings.db_name]
        self._logger = Logger().logger()



        #self._logger.info(f'connected to mongo: {self.client.server_info()}')

    def insert_new_posts(self):
        try:
            new_post_ids = self.get_new_post_ids()
            #find those which don't already exist:
            already_exist = self.db.posts.find({'_id': {'$in': new_post_ids}})
            already_exist = [row['_id'] for row in already_exist]

            new_post_ids = [post_id for post_id in new_post_ids if post_id not in already_exist]

            posts = self.get_posts_details(new_post_ids)
            inserted = []

            for post in posts:
                try:
                    self.db.posts.insert_one(post)
                    inserted.append(post['_id'])
                except pymongo.errors.DuplicateKeyError as exc:
                    pass  # can ignore duplicate key

            self._logger.info(f'new posts inserted: {inserted}')
            return inserted

        except Exception as exc:
            self._logger.error(exc)
            raise exc

    def set_post_sent(self, post_id):
        try:
            self.db.posts.update({'_id': post_id}, {'$set': {'sent': True}})
            return True
        except Exception as exc:
            self._logger.error(exc)
            return False

    def delete_old_posts(self, older_than):
        #todo: delete posts older than specific datetime
        pass

    def get_new_post_ids(self):
        try:
            top_stories_response = requests.get(HN_TOP_STORIES)

            if top_stories_response.status_code != 200:
                raise HNRetriveCurrentPostsError

            new_post_ids = sorted(top_stories_response.json(), reverse=True)[:POSTS_LIMIT]
            self._logger.info(f'new posts received: {new_post_ids}')
            return new_post_ids

        except HNRetriveCurrentPostsError:
            self._logger.error('Could not retrieve new posts')
            return None

    def _get_multiple_posts_data(self, urls):
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                future_to_json = {executor.submit(requests.get, post): post for post in urls}

                ret = []
                for future in concurrent.futures.as_completed(future_to_json):
                    data = future.result().json()
                    if data:
                        ret.append(data)

                return ret

        except ConnectionError as exc:
            self._logger.error(exc)
        except Exception as exc:
            self._logger.error('_get_multiple_posts_data failed.')
            self._logger.error(exc)

            ret = []

        return ret

    def get_posts_details(self, post_ids):
        urls = [HN_POST_DETAILS.format(post_id) for post_id in post_ids]
        post_details = self._get_multiple_posts_data(urls)

        post_details_stripped = [{'_id': post['id'],
                                  'title': post['title'],
                                  'url': post.get('url', ''),
                                  'link': HN_POST_LINK.format(post['id']),
                                  'received': datetime.datetime.now(),
                                  'sent': False} for post in post_details]

        return post_details_stripped


class HNRetriveCurrentPostsError(Exception):
    pass


class DBConnectionError(Exception):
    pass


class DBConfigError(Exception):
    pass
