# Telegram Bot with Perplexity AI Integration
<!--
SPDX-FileCopyrightText: 2024-2025 Damian Fajfer <damian@fajfer.org>

SPDX-License-Identifier: EUPL-1.2
-->
This Telegram bot integrates with Perplexity AI to provide AI-powered responses when mentioned in (group) chats.

## Why Perplexity?

There's plenty of opportunities (eg. mobile operator promotions) to get a one year Perplexity.ai Pro subscription.  Once applied, it gives you 5$ to spend on [the API](https://sonar.perplexity.ai/). This is my way of using these API credits.

## Bot settings

### Behaviour

The bot responds to:
- **@mentions**: `@your_bot_username your question`
- **Reply with @mention**: When you reply to a message and mention the bot, it will include the original message content as context

The bot ignores:
- All other messages and commands (e.g., `/start`, `/help`, `/ct` etc.)
- Messages outside of `ALLOWED_GROUPS`

### Privacy Settings

Bot only works with Privacy Mode set to **OFF**, for some reason I don't get any mentions, only commands used via `/`

### Configuration

Configure your bot by copying `.env.example` to `.env` and updating values:
- **Allowed Groups**: Configure which groups the bot can respond in
- **Bot Username**: Your bot's @username
- **API Tokens**: Telegram bot token and Perplexity API token

### Required variables

Please, refer to [.env](.env)

## How to run

1. **Just do it:**
   venv, install requirements, run `main.py`

2. **Docker:**
   ```bash
    docker run -d --rm \
    --name perplexity-telegram-bot \
    --env-file .env \
    ghcr.io/fajfer/perplexity-telegram-bot:latest
   ```
