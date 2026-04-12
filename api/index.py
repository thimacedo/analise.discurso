#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        with open(os.path.join(os.path.dirname(__file__), '..', 'dashboard.html'), 'r', encoding='utf-8') as f:
            html = f.read()
        
        self.wfile.write(html.encode('utf-8'))

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f"Dashboard rodando na porta {PORT}")
    server.serve_forever()