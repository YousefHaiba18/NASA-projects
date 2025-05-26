import socket
import requests
import os


API_KEY = os.getenv('NASA_API_KEY')
if not API_KEY:
    raise RuntimeError("NASA_API_KEY environment variable not set. Please set it before running.")


def get_apod():
    url = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}"
    response = requests.get(url)
    return response.json()


def apod_html(data):
    if data['media_type'] == 'image':
        image_tag = f'<img src="{data["url"]}" style="max-width: 60%;">'
    else:
        image_tag = f'<iframe src="{data["url"]}" width="560" height="315"></iframe>'
    title = data.get('title', 'Astronomy Picture of the Day')
    explanation = data.get('explanation', '')
    copyright = data.get('copyright', '')
    return f"""
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{
                background: #111;
                color: #eee;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 800px;
                margin: 40px auto;
                padding: 24px;
                background: #222;
                border-radius: 16px;
                box-shadow: 0 4px 20px #0005;
            }}
            h1 {{
                text-align: center;
                font-size: 2em;
                margin-top: 0;
            }}
            img, iframe {{
                display: block;
                margin: 0 auto 24px auto;
                max-width: 100%;
                border-radius: 10px;
                box-shadow: 0 2px 10px #0007;
            }}
            p {{
                font-size: 1.15em;
                line-height: 1.5;
                text-align: justify;
            }}
            .copyright {{
                font-size: 0.9em;
                color: #bbb;
                text-align: right;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{title}</h1>
            {image_tag}
            <p>{explanation}</p>
            <div class="copyright">{copyright}</div>
        </div>
    </body>
    </html>
    """

mainSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

mainSocket.bind(('127.0.0.1', 8080))  # Bind to localhost on port 8080

mainSocket.listen(1)

conn, addr = mainSocket.accept()
print(f"Connection from {addr} has been established!")

request = conn.recv(1024).decode('utf-8')
print(request)

request_line = request.splitlines()[0]
method, path, http_version = request_line.split()

if path == "/apod":
    data = get_apod()
    html = apod_html(data)
    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html\r\n\r\n"
        f"{html}"
    )
else:
    response = (
        "HTTP/1.1 404 Not Found\r\n"
        "Content-Type: text/html\r\n\r\n"
        "<h1>404 - Not Found</h1><p>Try <a href='/apod'>/apod</a></p>"
    )
conn.sendall(response.encode('utf-8'))
conn.close()