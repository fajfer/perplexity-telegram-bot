# SPDX-FileCopyrightText: 2025 Damian Fajfer <damian@fajfer.org>

# SPDX-License-Identifier: EUPL-1.2
from loguru import logger
import asyncio
import json
import re
import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from environment variables with fallbacks
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_OWNER_USERNAME = os.getenv("TELEGRAM_OWNER_USERNAME")

PERPLEXITY_API_TOKEN = os.getenv("PERPLEXITY_API_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")
PERPLEXITY_API_URL = os.getenv("PERPLEXITY_API_URL", "https://api.perplexity.ai/chat/completions")
MODEL = os.getenv("MODEL", "sonar")
PROMPT = os.getenv("PROMPT", "")

allowed_groups_str = os.getenv("ALLOWED_GROUPS")
chat_ids = [int(group_id.strip()) for group_id in allowed_groups_str.split(",")]

def make_perplexity_request(user_prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": PROMPT + user_prompt
            }
        ]
    }
    
    try:
        logger.info(f"Making request to Perplexity API for text: {user_prompt[:50]}...")
        response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"Received response from Perplexity API")
        
        if "choices" in data and len(data["choices"]) > 0:
            message_content = data["choices"][0].get("message", {}).get("content", "")
            if message_content:
                return message_content
            else:
                return "Sorry, I received an empty response from the AI service."
        else:
            logger.warning("No choices found in API response")
            return "Sorry, I couldn't get a response from the AI service."
            
    except requests.exceptions.Timeout:
        logger.error("Request to Perplexity API timed out")
        return "Sorry, the request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making request to Perplexity API: {e}")
        return "Sorry, there was an error connecting to the AI service."
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON response: {e}")
        return "Sorry, there was an error parsing the AI response."
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return "Sorry, an unexpected error occurred."

def strip_think_blocks(text: str) -> str:
    """
    Remove everything between <think> blocks from the text
    Thinking blocks appear as response in some models and annoy me
    """
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message

    if not message or not message.text:
        return
    
    bot_username_clean = BOT_USERNAME.lower().replace("@", "")
    user_text = message.text.replace(f"@{bot_username_clean}", "").strip()

    if message.text.startswith(f"@{bot_username_clean}"):
        if message.chat.id not in chat_ids:
            logger.error(f"Received unauthorized message in chat {message.chat.id} from user {message.from_user.id}: {message.text}")
            await message.reply_text(f"Unauthorized. Contact {TELEGRAM_OWNER_USERNAME} for access.")
            return
        logger.info(f"Processing user text: {user_text}")
        if user_text is None or user_text == "":
            return
        # Send "typing" action to show the bot is working
        await context.bot.send_chat_action(chat_id=message.chat_id, action="typing")
        # Make request to Perplexity AI
        ai_response = make_perplexity_request(user_text)
        if "<think>" in ai_response:
            stripped_response = strip_think_blocks(ai_response)
        else:
            stripped_response = ai_response
        # Send the AI response back to the chat
        # Split long messages if necessary (Telegram has a 4096 character limit)
        max_length = 4096
        if len(stripped_response) <= max_length:
            await message.reply_text(stripped_response)
        else:
            # Split the message into chunks
            for i in range(0, len(stripped_response), max_length):
                chunk = stripped_response[i:i + max_length]
                await message.reply_text(chunk)
                await asyncio.sleep(0.5)  # Small delay between chunks
    return

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle errors
    """
    logger.error(f"Exception while handling an update: {context.error}")


def main() -> None:
    """
    Start the bot
    """
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        return
    
    if not PERPLEXITY_API_TOKEN:
        logger.error("PERPLEXITY_API_TOKEN not found in environment variables")
        return
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT, handle_all_messages))
    application.add_error_handler(error_handler)
    
    logger.info(f"Starting Telegram bot {BOT_USERNAME}...")
    logger.info(f"Allowed chat ids: {chat_ids}")
    
    application.run_polling()


if __name__ == '__main__':
    main()
