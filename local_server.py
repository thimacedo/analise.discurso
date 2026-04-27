import http.server
import socketserver
import sys

PORT = 8090
Handler = http.server.SimpleHTTPRequestHandler

try:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"📡 SERVIDOR ATIVO NA PORTA {PORT}")
        httpd.serve_forever()
except Exception as e:
    with open("server_fatal_error.txt", "w") as f:
        f.write(str(e))
    sys.exit(1)
