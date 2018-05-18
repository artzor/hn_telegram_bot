from settings import Logger, settings
from hacker_news import HackerNews


def test_settings():
    assert settings.db_host != '' and isinstance(settings.db_host, str)
    assert settings.db_name != '' and isinstance(settings.db_name, str)
    db = settings.db_host.split(':')
    print(db)
    assert int(db[1]) != 0
    assert db[0] != ''

    assert settings.redis != '' and isinstance(settings.redis, str)


def test_logger(capsys):
    logger = Logger().logger()
    logger.debug('this is log test')
    captured = capsys.readouterr()
    assert 'this is log test' in captured.err


def test_hn():
    hacker_news = HackerNews()
    hacker_news.insert_new_posts()

    posts = hacker_news.db['posts'].find({})
    post_id = posts[0]['_id']
    assert post_id
    assert hacker_news.set_post_sent(post_id)


def test_bot():
    raise Exception('test not implemented')
