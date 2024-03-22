import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl

class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        self.directory = directory
        super().__init__(*args, directory=directory, **kwargs)

def serve_https(directory, port=10023, keyfile="./ssl/key.pem", certfile="./ssl/cert.pem"):
    httpd = HTTPServer(('0.0.0.0', port), lambda *args, **kwargs: CustomHandler(*args, directory=directory, **kwargs))
    httpd.socket = ssl.wrap_socket(httpd.socket, keyfile=keyfile, certfile=certfile, server_side=True)
    print(f"Serving {directory} on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <directory_to_serve> [port]") # python ssl/serve.py dist 10023
        sys.exit(1)

    directory = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) >= 3 else 10023
    serve_https(directory, port)
