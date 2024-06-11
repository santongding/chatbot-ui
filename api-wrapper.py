import http.server
import socketserver
import requests
import json
from urllib.parse import urlparse, parse_qs
# Define the port to listen on
PORT = 8888

# Define the Google Custom Search API parameters
API_URL = "https://www.googleapis.com/customsearch/v1"
CX = "02e8f0923da544bfd"
KEY = "AIzaSyDAG0i-V8vJU5cSyu3A58Lf1A2yKOXoHio"
import sys, io
def run_code_and_capture_output(code_str):
    code = [ x for x in code_str.split('\n') if len(x.strip())]
    if not "print(" in code[-1]:
        code[-1] = "print(" + code[-1] + ")"
    # Redirect stdout to capture print statements
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout

    dic = dict()
    try:
        # Execute the code string
        exec("\n".join(code), None, dic)
    except Exception as e:
        # Capture any exceptions and print them
        return f"Error: {e}"
    finally:
        # Reset stdout
        sys.stdout = old_stdout

    # Get the captured output
    output = new_stdout.getvalue()
    new_stdout.close()
    return output
class CustomSearchHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        # print("POST", self.path)
        pass

    def send_result(self, obj):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(obj, ensure_ascii=False).encode('utf-8'))
    def do_GET(self):
        print("GET", self.path)
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        if self.path.startswith('/search'):
            q = query_params.get('q', [''])[0]
            # print("q", q)
            # Make the request to the Google Custom Search API
            response = requests.get(API_URL, params={
                'cx': CX,
                'key': KEY,
                'q': query_params.get('q', [''])[0]
            })
            # print("code", response.status_code)
            # Check if the request was successful
            if response.status_code == 200:
                data = response.json()
                # Format the result
                formatted_result = self.format_result(data)
                print("r", formatted_result)
                self.send_result(formatted_result)
                # Send the formatted result back to the client

            else:
                self.send_response(response.status_code)
                self.end_headers()
        elif self.path.startswith('/python'):
            c = query_params.get('c', [''])[0]
            r = run_code_and_capture_output(c)
            print("r", r)
            self.send_result(r)

        else:
            self.send_response(404)
            self.end_headers()

    def format_result(self, data):
        # Extract and format the necessary information from the response
        formatted_result = {
            'items': []
        }
        for item in data.get('items', []):
            formatted_result['items'].append({
                'title': item.get('title'),
                'link': item.get('link'),
                'snippet': item.get('snippet')
            })
        return formatted_result

# Set up the HTTP server
with socketserver.TCPServer(("0.0.0.0", PORT), CustomSearchHandler) as httpd:
    httpd.allow_reuse_address = True
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
