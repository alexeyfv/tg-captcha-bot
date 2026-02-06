# TG Captcha Bot

A Telegram bot that protects chat groups by requiring new members to solve a simple math captcha and verify subscription to a channel before approving join requests.

## Features

- Handles chat join requests with math-based captcha
- Verifies channel subscription before approval
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
INSTRUCTION_TEXT=To join, please subscribe to <channel_name> and solve the equation below:
SUCCESS_TEXT=Approved. Welcome!
BUTTON_TEXT=I subscribed. Answer:
ANSWER_INCORRECT=Incorrect answer. Join request declined.
NOT_SUBSCRIBED=Not subscribed to the channel. Join request declined.
```

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
2. The bot generates a simple math captcha with multiple choice options and sends a private message to the user with the question and answer buttons.
3. The user clicks one of the answer buttons.
4. If the answer is incorrect or the user is not subscribed, the bot declines the join request and shows an error message.
5. If the answer is correct and the user is subscribed, the bot approves the join request and sends a welcome message.
