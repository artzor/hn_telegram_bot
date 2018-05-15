from hacker_news import HackerNews
from settings import Logger


def user_subscribe(bot, chat_id):
    try:
        text = "From now on you'll be receiving notifications with links to new posts!"
        bot.send_message(chat_id=chat_id, text=text)

        hacker_news = HackerNews()
        hacker_news.db.users.update_one({'_id': chat_id},
                                        {'$set': {'subscribed': True}},
                                        upsert=True)

        Logger().logger().info(f'user {chat_id} subscribed')

    except Exception as exc:
        Logger().logger().error(exc)
        raise exc


def user_unsubscribe(bot, chat_id):
    try:
        text = "I won't be sending notifications anymore."
        bot.send_message(chat_id, text)

        hacker_news = HackerNews()
        hacker_news.db.users.update_one({'_id': chat_id},
                                        {'$set': {'subscribed': False}},
                                        upsert=True)

        Logger().logger().info(f'user {chat_id} unsubscribed')
    except Exception as exc:
        Logger().logger().error(exc)
        raise exc
