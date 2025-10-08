# /api/redirect.py

from http.server import BaseHTTPRequestHandler
# Change 1: Added 'quote' to the import list
from urllib.parse import urlparse, parse_qs, unquote, quote
import os

# Your bot's username - MUST match your actual bot
BOT_USERNAME = "PremiumtelenovelasBot"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Get the query string from the Vercel environment variable
            query_string = os.environ.get('QUERY_STRING')

            # If not running on Vercel, fall back to parsing self.path
            if not query_string:
                parsed_url = urlparse(self.path)
                query_string = parsed_url.query

            query_components = parse_qs(query_string)

            # Flutterwave sends these parameters: status, tx_ref, transaction_id
            # We need the tx_ref to create our payload
            tx_ref = query_components.get('tx_ref', [None])[0]
            status = query_components.get('status', [None])[0]

            # Also check for our custom payload parameter (backup)
            custom_payload = query_components.get('payload', [None])[0]

            # Create payload from tx_ref or use custom payload
            if tx_ref:
                # Flutterwave redirect - use tx_ref
                payload = f"verify_{tx_ref}"
            elif custom_payload:
                # Direct access with payload
                payload = unquote(custom_payload)
            else:
                # No valid parameters
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                error_html = f"""
                    <html>
                        <body>
                            <h1>Error</h1>
                            <p>Payment verification data is missing.</p>
                            <p>Received parameters: {', '.join(query_components.keys())}</p>
                        </body>
                    </html>
                """
                self.wfile.write(error_html.encode())
                return

            # Change 2: Encoded the payload to make it URL-safe
            telegram_url = f"https://t.me/{BOT_USERNAME}?start={quote(payload)}"

            # Send a 302 redirect response with HTML fallback
            self.send_response(302)
            self.send_header('Location', telegram_url)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # Fallback HTML with auto-redirect and manual link
            html_content = f"""
                <html>
                    <head>
                        <meta http-equiv="refresh" content="0; url={telegram_url}">
                    </head>
                    <body>
                        <h2>Redirecting to Telegram...</h2>
                        <p>If you are not redirected automatically, <a href="{telegram_url}">click here</a>.</p>
                    </body>
                </html>
            """
            self.wfile.write(html_content.encode())

        except Exception as e:
            # Handle any errors
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error_html = f"""
                <html>
                    <body>
                        <h1>Server Error</h1>
                        <p>An error occurred: {str(e)}</p>
                    </body>
                </html>
            """
            self.wfile.write(error_html.encode())
