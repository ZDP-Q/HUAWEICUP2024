from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from myStatic import MyClass
class TokenServer:
    def __init__(self, port):
        self.token = None
        self.port = port
        self.httpd = HTTPServer(('0.0.0.0', self.port), self.RequestHandler)
        self.RequestHandler.set_server(self)

    class RequestHandler(BaseHTTPRequestHandler):
        @classmethod
        def set_server(cls, server_instance):
            cls.server_instance = server_instance

        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                print(data)
                if 'token' in data:
                    self.server_instance.token = data['token']
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'Token received')
                    MyClass.set_class_var(self.server_instance.token)
                    print("server_instance.token",self.server_instance.token)
                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b'Invalid request: No token found')
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Invalid request: Not a valid JSON')

    def start_server(self):
        print(f"Starting server on port {self.port}")
        self.httpd.serve_forever()

    def get_token(self):
        self.token = self.server_instance.token
        return self.token

# Example usage
if __name__ == "__main__":
    port = 8880
    server = TokenServer(port)
    server.start_server()