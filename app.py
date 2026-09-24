from flask import Flask, request, render_template_string
import subprocess
import os
import uuid

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ReelSave — Facebook Reels Downloader</title>
<meta name="description" content="ReelSave adalah downloader Facebook Reels sederhana dan cepat.">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{
font-family:Arial,Helvetica,sans-serif;
min-height:100vh;
background:linear-gradient(135deg,#07111f,#102b46,#07111f);
color:white;
display:flex;
justify-content:center;
align-items:center;
padding:20px
}
.container{width:100%;max-width:720px}
.logo{
text-align:center;
font-size:38px;
font-weight:800;
letter-spacing:-1px;
margin-bottom:8px
}
.logo span{color:#39a9ff}
.subtitle{
text-align:center;
color:#aebdcc;
margin-bottom:30px
}
.card{
background:rgba(255,255,255,.08);
border:1px solid rgba(255,255,255,.12);
border-radius:24px;
padding:30px;
backdrop-filter:blur(15px);
box-shadow:0 20px 60px rgba(0,0,0,.35)
}
h1{font-size:25px;text-align:center;margin-bottom:10px}
.desc{text-align:center;color:#b9c5d1;margin-bottom:25px}
input{
width:100%;
padding:17px;
border-radius:13px;
border:1px solid #31485d;
background:#091522;
color:white;
font-size:16px;
outline:none;
margin-bottom:13px
}
input:focus{border-color:#39a9ff}
button{
width:100%;
padding:17px;
border:0;
border-radius:13px;
background:linear-gradient(90deg,#1688e8,#45b8ff);
color:white;
font-size:17px;
font-weight:bold;
cursor:pointer
}
button:hover{opacity:.9}
.info{
display:grid;
grid-template-columns:repeat(3,1fr);
gap:10px;
margin-top:22px
}
.box{
background:rgba(255,255,255,.06);
padding:15px 8px;
border-radius:13px;
text-align:center;
font-size:13px;
color:#c8d3de
}
.footer{
text-align:center;
color:#7f91a2;
font-size:12px;
margin-top:20px;
line-height:1.6
}
.notice{
margin-top:20px;
font-size:12px;
color:#8fa3b5;
text-align:center
}
@media(max-width:500px){
.logo{font-size:31px}
.card{padding:22px}
.info{grid-template-columns:1fr}
}
</style>
</head>
<body>
<div class="container">
<div class="logo">Reel<span>Save</span></div>
<div class="subtitle">Facebook Reels Downloader</div>

<div class="card">
<h1>Download Facebook Reels</h1>
<p class="desc">Tempel URL Facebook Reel kamu di bawah.</p>

<form action="/download" method="post">
<input
type="url"
name="url"
placeholder="https://www.facebook.com/reel/..."
required>
<button type="submit">⬇ Download Reel</button>
</form>

<div class="info">
<div class="box">⚡ Cepat</div>
<div class="box">📱 Mobile Friendly</div>
<div class="box">🔒 Sederhana</div>
</div>

<div class="notice">
Gunakan hanya untuk konten yang kamu miliki atau berhak mengunduhnya.
</div>
</div>

<div class="footer">
© 2026 ReelSave · Facebook Reels Downloader<br>
ReelSave bukan bagian dari Facebook/Meta.
</div>
</div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML)

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url", "").strip()

    if not url:
        return "URL tidak boleh kosong.", 400

    filename = f"/tmp/{uuid.uuid4().hex}.mp4"

    try:
        subprocess.run([
            "yt-dlp",
            "--no-playlist",
            "-f", "best[ext=mp4]/best",
            "-o", filename,
            url
        ], check=True, timeout=120)

        if os.path.exists(filename):
            from flask import send_file
            return send_file(
                filename,
                as_attachment=True,
                download_name="reelsave-video.mp4"
            )

        return "Video tidak berhasil dibuat.", 500

    except Exception:
        return """
        <h2>Download gagal</h2>
        <p>Pastikan URL Facebook Reel valid dan dapat diakses secara publik.</p>
        <p><a href="/">Kembali</a></p>
        """, 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
