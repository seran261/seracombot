import requests

class TelegramNotifier:
    def __init__(self, token):
        self.url = f"https://api.telegram.org/bot{token}"

    def send(self, chat_id, text):
        requests.post(
            f"{self.url}/sendMessage",
            json={"chat_id": chat_id, "text": text}
        )
