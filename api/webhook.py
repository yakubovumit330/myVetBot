# api/webhook.py
import os
import json
import requests
from http.server import BaseHTTPRequestHandler

TOKEN = os.environ.get("8467556633:AAFwl2sXSzq-3SCSHfp0TCSr4vbduIHOOlU")  # set this in Vercel later

class handler(BaseHTTPRequestHandler):
    def _send(self, code, body=b"OK"):
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        # simple health-check so visiting the URL in a browser returns something
        self._send(200, b"Bot running")

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            update = json.loads(raw.decode("utf-8"))
        except Exception as e:
            print("Failed to parse request body:", e)
            self._send(400, b"Bad Request")
            return

        print("Incoming update:", update)  # this should appear in Vercel function logs

        # Example: echo reply for messages
        if "message" in update:
            chat_id = update["message"]["chat"]["id"]
            text = "Hello — your bot received the update."
            try:
                requests.post(
                    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                    json={"chat_id": chat_id, "text": text},
                    timeout=5,
                )
            except Exception as e:
                print("Failed to call Telegram sendMessage:", e)

        self._send(200, b"OK")
