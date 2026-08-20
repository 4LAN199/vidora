from flask import Flask, request, render_template_string, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Video Downloader</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f2f4f7;
            display: flex;
            justify-content: center;
            padding-top: 60px;
        }

        .container {
            background: white;
            width: 450px;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,.1);
        }

        h1 {
            text-align: center;
        }

        input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            box-sizing: border-box;
            border: 1px solid #ccc;
            border-radius: 8px;
        }

        button {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 8px;
            background: #222;
            color: white;
            cursor: pointer;
            font-size: 16px;
        }

        button:hover {
            background: #444;
        }

        .message {
            margin-top: 20px;
            text-align: center;
        }
    </style>
</head>

<body>

<div class="container">

    <h1>🎬 Video Downloader</h1>

    <form method="POST">

        <input
            type="text"
            name="url"
            placeholder="Masukkan URL video..."
            required
        >

        <button type="submit">
            Download Video
        </button>

    </form>

    {% if message %}
        <div class="message">
            {{ message }}
        </div>
    {% endif %}

    {% if filename %}
        <div class="message">
            <a href="/download/{{ filename }}">
                ⬇️ Download File
            </a>
        </div>
    {% endif %}

</div>

</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():

    message = ""
    filename = None

    if request.method == "POST":

        url = request.form.get("url")

        if not url:
            message = "URL belum dimasukkan."

        else:

            file_id = str(uuid.uuid4())

            output = os.path.join(
                DOWNLOAD_DIR,
                file_id + ".%(ext)s"
            )

            options = {
                "format": "best[ext=mp4]/best",
                "outtmpl": output,
                "noplaylist": True
            }

            try:

                with yt_dlp.YoutubeDL(options) as ydl:
                    ydl.download([url])

                files = os.listdir(DOWNLOAD_DIR)

                matching = [
                    f for f in files
                    if f.startswith(file_id)
                ]

                if matching:
                    filename = matching[0]
                    message = "Video berhasil diproses."

                else:
                    message = "File tidak ditemukan."

            except Exception as e:

                message = f"Terjadi kesalahan: {e}"

    return render_template_string(
        HTML,
        message=message,
        filename=filename
    )


@app.route("/download/<filename>")
def download(filename):

    path = os.path.join(
        DOWNLOAD_DIR,
        filename
    )

    if not os.path.exists(path):
        return "File tidak ditemukan.", 404

    return send_file(
        path,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
