# TG Captcha Bot

A Telegram bot that protects chat groups by requiring new members to solve a simple math captcha, verify subscription to a channel, or both before approving join requests.

## Features

- Configurable join requirements: math captcha, channel subscription, or both
- Uses inline keyboards for user interaction
- Configurable via environment variables
- Docker support for easy deployment

## Setup

1. Clone the repository
2. Install dependencies using uv:

   ``` bash
   uv sync
   ```

## Environment variables

Create a `.env` file in the root directory with the following variables:

``` env
BOT_TOKEN=
CHANNEL_ID=
CHAT_ID=
MODE=subscription
INSTRUCTION_TEXT=To join, please subscribe to <channel_name> and click the button below.
SUCCESS_TEXT=Approved. Welcome!
BUTTON_TEXT=I subscribed!:
ANSWER_INCORRECT=Incorrect answer. Join request declined.
NOT_SUBSCRIBED=Not subscribed to the channel. Join request declined.
```

`MODE` can be `subscription` (check channel subscription only), `equation` (math captcha only), or `both` (both checks).

Example values for `INSTRUCTION_TEXT` and `BUTTON_TEXT` based on `MODE`:

| Mode         | INSTRUCTION_TEXT                                                            | BUTTON_TEXT             |
| ------------ | --------------------------------------------------------------------------- | ----------------------- |
| subscription | `To join, please subscribe to <channel_name> and click the button below:`   | `I subscribed!`         |
| equation     | `To join, please solve the equation below:`                                 | `Answer:`               |
| both         | `To join, please subscribe to <channel_name> and solve the equation below:` | `I subscribed. Answer:` |

## Running locally

Run the bot locally:

``` bash
uv run main.py
```

## Running with Docker

Use pre-built Docker image `ghcr.io/alexeyfv/tg-captcha-bot:latest` or build it yourself:

``` bash
docker build -t tg-captcha-bot .
```

## Join request processing flow

1. A user sends a join request to the chat.
2. Depending on `MODE`, the bot sends a private message with captcha (math or subscription verification) and buttons.
3. The user interacts with the buttons.
4. The bot validates the response based on `MODE` (answer and/or subscription).
5. If requirements are met, the join request is approved; otherwise, declined.
