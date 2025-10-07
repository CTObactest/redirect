# /api/redirect.py

from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Your bot's username
BOT_USERNAME = "PremiumtelenovelasBot" # Replace with your bot's username

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the incoming URL to get the query parameters
        query_components = parse_qs(urlparse(self.path).query)
        payload = query_components.get('payload', [None])[0]

        if not payload:
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Error: Payload parameter is missing.")
            return

        # Construct the clean Telegram deep link
        telegram_url = f"https://t.me/{BOT_USERNAME}?start={payload}"

        # Send a 302 redirect response
        self.send_response(302)
        self.send_header('Location', telegram_url)
        self.end_headers()
        return
