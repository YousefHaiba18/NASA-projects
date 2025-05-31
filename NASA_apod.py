import socket
import requests
import os
from urllib.parse import urlparse, parse_qs

API_KEY = os.getenv('NASA_API_KEY')
if not API_KEY:
    raise RuntimeError("NASA_API_KEY environment variable not set. Please set it before running.")

def get_apod(date=None):
    url = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}"
    if date:
        url += f"&date={date}"
    response = requests.get(url)
    return response.json()

def apod_html(data=None, selected_date=None, error=None):
    date_picker_form = f"""
    <form method="get" action="/apod" style="text-align: center; margin-bottom: 20px;">
        <label for="date">Select Date:</label>
        <input type="date" id="date" name="date" value="{selected_date or ''}">
        <button type="submit">Go</button>
    </form>
    """
    if data:
        if data['media_type'] == 'image':
            image_tag = f'<img src="{data["url"]}" style="max-width: 60%;">'
        else:
            image_tag = f'<iframe src="{data["url"]}" width="560" height="315"></iframe>'
        title = data.get('title', 'Astronomy Picture of the Day')
        explanation = data.get('explanation', '')
        copyright = data.get('copyright', '')
        content = f"""
            <h1>{title}</h1>
            {image_tag}
            <p>{explanation}</p>
            <div class="copyright">{copyright}</div>
        """
    elif error:
        content = f"<h1>Error</h1><p>{error}</p>"
    else:
        content = "<p>Please select a date to view the Astronomy Picture of the Day.</p>"

    return f"""
    <html>
    <head>
        <title>Astronomy Picture of the Day</title>
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
            form {{
                margin-bottom: 20px;
            }}
            label {{
                font-size: 1em;
                margin-right: 10px;
            }}
            input[type="date"] {{
                padding: 5px;
                font-size: 1em;
                border-radius: 5px;
                border: none;
            }}
            button {{
                padding: 6px 12px;
                font-size: 1em;
                border-radius: 5px;
                background-color: #444;
                color: #eee;
                border: none;
                cursor: pointer;
            }}
            button:hover {{
                background-color: #555;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            {date_picker_form}
            {content}
        </div>
    </body>
    </html>
    """

def start_server():
    mainSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mainSocket.bind(('127.0.0.1', 8080))
    mainSocket.listen(1)
    print("Server is running at http://localhost:8080")

    while True:
        conn, addr = mainSocket.accept()
        print(f"Connection from {addr} has been established!")

        request = conn.recv(1024).decode('utf-8')
        print(request)

        if not request:
            conn.close()
            continue

        request_line = request.splitlines()[0]
        try:
            method, path, http_version = request_line.split()
        except ValueError:
            conn.close()
            continue

        parsed_url = urlparse(path)
        path_only = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        if path_only == "/apod":
            date_param = query_params.get('date', [None])[0]
            try:
                if date_param:
                    data = get_apod(date_param)
                    if 'code' in data and data['code'] == 400:
                        raise ValueError(data.get('msg', 'Invalid date'))
                    html = apod_html(data, selected_date=date_param)
                else:
                    html = apod_html()
                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/html\r\n\r\n"
                    f"{html}"
                )
            except Exception as e:
                html = apod_html(error=str(e))
                response = (
                    "HTTP/1.1 400 Bad Request\r\n"
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

if __name__ == "__main__":
    start_server()
