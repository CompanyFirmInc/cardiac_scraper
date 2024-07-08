import praw
import uuid
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


authorisation_code = None


# HELPER CLASS
class AuthHandler (BaseHTTPRequestHandler):
    def do_GET (self):
        global authorisation_code
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        query = parse_qs(urlparse(self.path).query)
        
        if 'code' in query:
            authorisation_code = query["code"][0]
            self.wfile.write(b"Authorization successful! You can close this window.")
        else:
            self.wfile.write(b"No code found in the request.")
            exit(1)


# UTILITY SERVER
def start_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, AuthHandler)
    httpd.handle_request()


# AUTH CODE
def auth() -> None:
    state = uuid.uuid4().hex
    scopes = ["identity","read"]
    
    # make a connection to reddit from the vars
    connection = praw.Reddit("scraper", ratelimit_seconds=300)    
    auth_uri = connection.auth.url(scopes, state, "permanent")

    # create the listening server
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    # opens the OS-set default web_browser
    webbrowser.open_new(auth_uri)
    print("Your web browser should open. If it didn't, go to:\n")
    print(auth_uri)
    print("\nSign in to your Reddit account. Copy the code from the URL below.\n")
    
    # wait for the webbrowser to request to web server
    server_thread.join()
    
    if authorisation_code:
        refresh_token = connection.auth.authorize(authorisation_code)
        reddit = praw.Reddit(
            "scraper",
            refresh_token=refresh_token)
        print(reddit.user.me())
        print(reddit.auth.scopes())
        return connection
    else:
        exit("No code acquired. Exiting.")
