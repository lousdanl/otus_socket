import argparse
import re
import socket
import ssl
from collections import defaultdict
from html.parser import HTMLParser

# Params
parser = argparse.ArgumentParser()
parser.add_argument("--method", action="store", default="GET")
parser.add_argument("--url", action="store", default="/")
parser.add_argument("--host", action="store", default="www.google.com")
parser.add_argument("--headers", action="store", default="")
args = parser.parse_args()

# SSL
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
context.verify_mode = ssl.CERT_REQUIRED
context.check_hostname = True
context.load_default_certs()

# Request
request = f"""
{args.method} {args.url} HTTP/1.1
Host: {args.host}
{args.headers}
"""

# Client Socket
port = 443
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock = context.wrap_socket(sock, server_hostname=args.host)
sock.connect((args.host, port))
sock.send(request.encode(encoding="utf-8"))
response = sock.recv(4096).decode(encoding="utf8")
sock.close()

# Response
result, body = response.split("\r\n\r\n", 1)
result = result.split("\r\n")
starting_line = result[0]
result.remove(starting_line)
headers = result
code = re.search(r"(\d{3})", starting_line).group(1)
print("Response code: ", code)
print("Response headers: ", headers)
print("Response Body: ", body)


class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = defaultdict(int)
        self.data = []
        self.links = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        self.tags[tag] += 1

        if tag == "a":
            self.links.append(attrs[0][1])

        if tag == "img":
            self.images.append(attrs[0][1])

    def handle_data(self, data):
        self.data.append(data)

    def most_common_tag(self):
        return max(self.tags.keys(), key=self.tags.get)


parser = MyHTMLParser()
parser.feed(body)
print("Tags: ", dict(parser.tags))
print("Most common tag: ", parser.most_common_tag())
print("Text: ", parser.data)
print("Links: ", parser.links)
print("Images: ", parser.images)
