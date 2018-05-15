import telegram
from celery import Celery
from settings import settings, Logger
from hacker_news import HackerNews


app = Celery('tasks', broker=settings.redis)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(180.0, send_new_posts.s(), name='new posts every 180')
    send_new_posts.delay()


@app.task
def send_new_posts():
    try:
        hacker_news = HackerNews()
        hacker_news.insert_new_posts()
        users = list(hacker_news.db.users.find({'subscribed': True}))
        posts = list(hacker_news.db.posts.find({'sent': False}))

        for post in posts:
            for user in users:
                notify_user.delay(user['_id'], post)

            hacker_news.set_post_sent(post['_id'])

    except Exception as exc:
        print(exc)


@app.task
def notify_user(chat_id, post):
    try:
        bot = telegram.Bot(settings.api_token)
        text = '*{}*\n[{}]({})\n[comments]({})'.format(post['title'], post['url'], post['url'], post['link'])
        bot.send_message(chat_id=chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)

    except Exception as exc:
        Logger().logger().error(exc)


@app.task
def hello():
    print('helloworld')
