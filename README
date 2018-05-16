## Telegram bot for Hacker News
This [telegram](https://telegram.org) bot sends notifications from [Hacker News](https://news.ycombinator.com) to the users.
 Bot uses [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) library with [webhooks](https://core.telegram.org/bots/webhooks) through flask+gunicorn.


## Installation and Configuration

1. Create new bot using [BotFather](https://core.telegram.org/bots#6-botfather)
1. `git clone` repository
1. Make changes to **settings.env**: set **API_TOKEN**, **BOT_HOST**, and **CERT_FILE** with **CERT_KEY** if you're using self generated certificate (you may want to mount volume)
1. Setup nginx with ssl and forwarding to `localhost:5000` 
1. Run `docker-compose up`

1. Navigate in browser to `your_host/wh` and if everything is correct you will see a message `Webhook was set to your_host/your_api_token`
1. Create chat in telegram with your bot and and say `/start `
