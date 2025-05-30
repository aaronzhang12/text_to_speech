import os
from http.server import SimpleHTTPRequestHandler, HTTPServer
import gzip
from io import BytesIO

class GzipHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.translate_path(self.path)
        if not os.path.exists(path) or os.path.isdir(path):
            self.send_error(404, "File not found")
            return None
        
        # Handle JSON files with Gzip compression
        if path.endswith('.json'):
            try:
                with open(path, 'rb') as f:
                    content = f.read()
                compressed = BytesIO()
                with gzip.GzipFile(fileobj=compressed, mode='wb') as gz:
                    gz.write(content)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Encoding', 'gzip')
                self.send_header('Content-Length', len(compressed.getvalue()))
                self.end_headers()
                return BytesIO(compressed.getvalue())
            except Exception as e:
                self.send_error(500, f"Error compressing file: {e}")
                return None
        
        # Handle other files (default behavior)
        return super().send_head()

def run(server_class=HTTPServer, handler_class=GzipHandler, port=8000):
    # Set the current directory as the server root
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Serving HTTP on http://localhost:{port} from {os.getcwd()}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()

if __name__ == '__main__':
    run()