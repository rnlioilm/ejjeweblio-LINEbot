from flask import Flask, request,abort
import requests
from bs4 import BeautifulSoup
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os

app = Flask(__name__)

YOUR_CHANNEL_ACCESS_TOKEN = "YOUR_CHANNEL_ACCESS_TOKEN"
YOUR_CHANNEL_SECRET = "YOUR_CHANNEL_SECRET"

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body) #

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'




@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    word = event.message.text
    url = "https://ejje.weblio.jp/content/" + word
    r = requests.get(url)
    r.encoding = r.apparent_encoding
    html = r.text
    bs = BeautifulSoup(html, 'html.parser')
    explanation_list = bs.select("td.content-explanation")
    
    try:
        for idx, txt in enumerate(explanation_list):
            ejje = explanation_list[idx].text
    except AttributeError:
        ejje = "Not found"

    if event.reply_token == "00000000000000000000000000000000":
        return    

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=word + '\n' + ejje.lstrip()))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
