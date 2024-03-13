import requests
import json
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

import database

telegram_token = ""
yandex_cloud_catalog = ""
yandex_gpt_api_key = ""
yandex_gpt_model = "yandexgpt-lite"

database = database.Database("database.db")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Я могу исправлять ошибки в тексте! Пришли мне что-нибудь.",
    )


async def counter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    counter = database.get_counter(update.effective_chat.id)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Количество присланных символов: {counter}",
    )


async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_len = len(update.message.text)
    database.add_counter(update.effective_chat.id, text_len)

    system_prompt = (
        "Исправь ошибки в тексте. В ответе напиши только исправленный текст."
    )
    answer = send_gpt_request(system_prompt, update.message.text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)


def send_gpt_request(system_prompt: str, user_prompt: str):
    body = {
        "modelUri": f"gpt://{yandex_cloud_catalog}/{yandex_gpt_model}",
        "completionOptions": {"stream": False, "temperature": 0.6, "maxTokens": "2000"},
        "messages": [
            {"role": "system", "text": system_prompt},
            {"role": "user", "text": user_prompt},
        ],
    }
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {yandex_gpt_api_key}",
        "x-folder-id": yandex_cloud_catalog,
    }
    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        return "ERROR"

    response_json = json.loads(response.text)
    answer = response_json["result"]["alternatives"][0]["message"]["text"]
    if len(answer) == 0:
        return "ERROR"
    return answer


if __name__ == "__main__":
    start_handler = CommandHandler("start", start)
    counter_handler = CommandHandler("counter", counter)
    text_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), text)

    application = ApplicationBuilder().token(telegram_token).build()
    application.add_handler(start_handler)
    application.add_handler(counter_handler)
    application.add_handler(text_handler)
    application.run_polling()
