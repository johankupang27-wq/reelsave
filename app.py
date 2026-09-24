from flask import Flask, request, render_template_string, send_file
import subprocess
import os
import uuid
import re

app = Flask(__name__)

BASE_STYLE = """
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{
font-family:Arial,Helvetica,sans-serif;
min-height:100vh;
background:linear-gradient(135deg,#07111f,#102b46,#07111f);
color:white;
padding:20px;
}
.container{
width:100%;
max-width:850px;
margin:0 auto;
}
.logo{
text-align:center;
font-size:38px;
font-weight:800;
letter-spacing:-1px;
margin-top:30px;
margin-bottom:8px;
}
.logo span{color:#39a9ff}
.nav{
text-align:center;
margin:20px 0 30px;
}
.nav a{
color:#aebdcc;
text-decoration:none;
margin:0 8px;
font-size:14px;
}
.nav a:hover{color:#39a9ff}
.card{
background:rgba(255,255,255,.08);
border:1px solid rgba(255,255,255,.12);
border-radius:24px;
padding:30px;
backdrop-filter:blur(15px);
box-shadow:0 20px 60px rgba(0,0,0,.35);
}
h1{
font-size:28px;
text-align:center;
margin-bottom:12px;
}
h2{
font-size:21px;
margin:25px 0 10px;
}
p{
line-height:1.7;
color:#c4d0db;
margin-bottom:14px;
}
.desc{
text-align:center;
margin-bottom:25px;
}
input{
width:100%;
padding:17px;
border-radius:13px;
border:1px solid #31485d;
background:#091522;
color:white;
font-size:16px;
outline:none;
margin-bottom:13px;
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
cursor:pointer;
}
button:hover{opacity:.9}
.info{
display:grid;
grid-template-columns:repeat(3,1fr);
gap:10px;
margin-top:22px;
}
.box{
background:rgba(255,255,255,.06);
padding:15px 8px;
border-radius:13px;
text-align:center;
font-size:13px;
color:#c8d3de;
}
.notice{
margin-top:20px;
font-size:12px;
color:#8fa3b5;
text-align:center;
line-height:1.6;
}
.footer{
text-align:center;
color:#7f91a2;
font-size:12px;
margin-top:25px;
padding-bottom:30px;
line-height:1.7;
}
.footer a{
color:#8fa3b5;
text-decoration:none;
}
.error{
text-align:center;
padding:20px;
}
.error h1{font-size:24px}
ul{
margin:10px 0 20px 20px;
color:#c4d0db;
line-height:1.8;
}
@media(max-width:600px){
.logo{font-size:31px}
.card{padding:22px}
.info{grid-template-columns:1fr}
.nav a{
display:inline-block;
margin:5px 6px;
}
}
</style>
"""

HOME_HTML = """
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>ReelSave — Facebook Reels Downloader</title>

<meta name="description"
content="ReelSave adalah alat online sederhana untuk membantu mengunduh Facebook Reels yang Anda miliki atau berhak mengunduhnya.">

<meta name="robots" content="index,follow">

<meta property="og:title" content="ReelSave — Facebook Reels Downloader">
<meta property="og:description"
content="Download Facebook Reels dengan ReelSave. Gunakan hanya untuk konten yang Anda miliki atau berhak mengunduhnya.">
<meta property="og:type" content="website">

{{ style|safe }}
</head>

<body>

<div class="container">

<div class="logo">Reel<span>Save</span></div>

<div class="nav">
<a href="/">Home</a>
<a href="/how-to-download">Cara Download</a>
<a href="/faq">FAQ</a>
<a href="/about">About</a>
</div>

<div class="card">

<h1>Download Facebook Reels</h1>

<p class="desc">
Tempel URL Facebook Reel yang dapat diakses secara publik di bawah.
</p>

<form action="/download" method="post">

<input
type="url"
name="url"
placeholder="https://www.facebook.com/reel/..."
required
autocomplete="off">

<button type="submit">⬇ Download Reel</button>

</form>

<div class="info">
<div class="box">⚡ Cepat</div>
<div class="box">📱 Mobile Friendly</div>
<div class="box">🔒 Sederhana</div>
</div>

<div class="notice">
Gunakan ReelSave hanya untuk konten yang Anda miliki
atau memiliki izin/hak untuk mengunduhnya.
</div>

</div>

<h2>Facebook Reels Downloader</h2>

<p>
ReelSave adalah alat online sederhana untuk membantu pengguna
mengakses dan mengunduh Facebook Reels yang memang mereka miliki
atau berhak mengunduhnya.
</p>

<h2>Cara menggunakan ReelSave</h2>

<ul>
<li>Salin URL Facebook Reel.</li>
<li>Tempel URL ke kolom di atas.</li>
<li>Tekan tombol Download Reel.</li>
<li>Jika video dapat diproses, file akan dikirimkan untuk diunduh.</li>
</ul>

<h2>Gunakan secara bertanggung jawab</h2>

<p>
Pastikan Anda memiliki hak atau izin yang sesuai sebelum mengunduh,
menyimpan, atau menggunakan kembali video apa pun.
ReelSave tidak mengklaim kepemilikan atas konten yang diproses
melalui layanan ini.
</p>

<div class="footer">
© 2026 ReelSave · Facebook Reels Downloader<br>

<a href="/privacy">Privacy Policy</a> ·
<a href="/terms">Terms</a> ·
<a href="/disclaimer">Disclaimer</a> ·
<a href="/copyright">Copyright</a> ·
<a href="/contact">Contact</a>

<br><br>

ReelSave bukan bagian dari Facebook/Meta.
</div>

</div>

</body>
</html>
"""

PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ title }} — ReelSave</title>
<meta name="description" content="{{ description }}">
<meta name="robots" content="index,follow">
{{ style|safe }}
</head>

<body>

<div class="container">

<div class="logo">Reel<span>Save</span></div>

<div class="nav">
<a href="/">Home</a>
<a href="/how-to-download">Cara Download</a>
<a href="/faq">FAQ</a>
<a href="/about">About</a>
</div>

<div class="card">

<h1>{{ heading }}</h1>

{{ content|safe }}

</div>

<div class="footer">
© 2026 ReelSave<br>
<a href="/privacy">Privacy Policy</a> ·
<a href="/terms">Terms</a> ·
<a href="/disclaimer">Disclaimer</a> ·
<a href="/copyright">Copyright</a> ·
<a href="/contact">Contact</a>
<br><br>
ReelSave bukan bagian dari Facebook/Meta.
</div>

</div>

</body>
</html>
"""


def page(title, description, heading, content):
    return render_template_string(
        PAGE_TEMPLATE,
        title=title,
        description=description,
        heading=heading,
        content=content,
        style=BASE_STYLE
    )


def valid_facebook_url(url):
    """
    Membatasi input ke domain Facebook yang umum.
    """
    pattern = re.compile(
        r"^https?://("
        r"(www\.)?facebook\.com|"
        r"(m\.)?facebook\.com|"
        r"fb\.watch"
        r")(/|$)",
        re.IGNORECASE
    )

    return bool(pattern.match(url))


@app.route("/", methods=["GET"])
def home():
    return render_template_string(
        HOME_HTML,
        style=BASE_STYLE
    )


@app.route("/download", methods=["POST"])
def download():

    url = request.form.get("url", "").strip()

    if not url:
        return page(
            "URL kosong",
            "URL Facebook Reel tidak boleh kosong.",
            "URL Tidak Boleh Kosong",
            """
            <p>Silakan masukkan URL Facebook Reel terlebih dahulu.</p>
            <p><a href="/">← Kembali ke ReelSave</a></p>
            """
        ), 400

    if len(url) > 2000:
        return page(
            "URL terlalu panjang",
            "URL yang diberikan terlalu panjang.",
            "URL Tidak Valid",
            """
            <p>URL yang Anda masukkan terlalu panjang.</p>
            <p><a href="/">← Kembali</a></p>
            """
        ), 400

    if not valid_facebook_url(url):
        return page(
            "URL tidak valid",
            "ReelSave hanya menerima URL Facebook.",
            "URL Tidak Valid",
            """
            <p>
            Masukkan URL Facebook Reel yang valid dan dapat
            diakses secara publik.
            </p>

            <p><a href="/">← Kembali</a></p>
            """
        ), 400

    filename = f"/tmp/reelsave-{uuid.uuid4().hex}.mp4"

    try:

        subprocess.run(
            [
                "yt-dlp",
                "--no-playlist",
                "--no-part",
                "-f",
                "best[ext=mp4]/best",
                "-o",
                filename,
                url
            ],
            check=True,
            timeout=120,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True
        )

        if not os.path.exists(filename):
            return page(
                "Download gagal",
                "Video tidak berhasil dibuat.",
                "Download Gagal",
                """
                <p>
                Video tidak berhasil diproses.
                Pastikan Reel dapat diakses secara publik.
                </p>

                <p><a href="/">← Kembali</a></p>
                """
            ), 500

        response = send_file(
            filename,
            as_attachment=True,
            download_name="reelsave-video.mp4",
            mimetype="video/mp4"
        )

        @response.call_on_close
        def cleanup():
            try:
                if os.path.exists(filename):
                    os.remove(filename)
            except Exception:
                pass

        return response

    except subprocess.TimeoutExpired:

        try:
            if os.path.exists(filename):
                os.remove(filename)
        except Exception:
            pass

        return page(
            "Download timeout",
            "Proses download terlalu lama.",
            "Download Terlalu Lama",
            """
            <p>
            Proses download melebihi batas waktu.
            Silakan coba lagi dengan URL lain.
            </p>

            <p><a href="/">← Kembali</a></p>
            """
        ), 504

    except subprocess.CalledProcessError:

        try:
            if os.path.exists(filename):
                os.remove(filename)
        except Exception:
            pass

        return page(
            "Download gagal",
            "Facebook Reel tidak dapat diproses.",
            "Download Gagal",
            """
            <p>
            Reel tidak dapat diproses. Pastikan URL benar
            dan konten dapat diakses secara publik.
            </p>

            <p><a href="/">← Kembali</a></p>
            """
        ), 400

    except Exception:

        try:
            if os.path.exists(filename):
                os.remove(filename)
        except Exception:
            pass

        return page(
            "Terjadi kesalahan",
            "Terjadi kesalahan saat memproses permintaan.",
            "Terjadi Kesalahan",
            """
            <p>
            Terjadi kesalahan saat memproses permintaan.
            Silakan coba lagi beberapa saat kemudian.
            </p>

            <p><a href="/">← Kembali</a></p>
            """
        ), 500


@app.route("/how-to-download")
def how_to_download():

    content = """
    <h2>Langkah 1</h2>
    <p>Salin URL Facebook Reel yang ingin Anda proses.</p>

    <h2>Langkah 2</h2>
    <p>
    Kembali ke ReelSave dan tempel URL tersebut
    pada kolom download.
    </p>

    <h2>Langkah 3</h2>
    <p>
    Tekan tombol <strong>Download Reel</strong>.
    </p>

    <h2>Langkah 4</h2>
    <p>
    Jika Reel dapat diproses, file video akan dikirim
    untuk diunduh.
    </p>

    <p>
    Gunakan layanan ini hanya untuk konten yang Anda miliki
    atau berhak mengunduhnya.
    </p>
    """

    return page(
        "Cara Download Facebook Reels",
        "Panduan menggunakan ReelSave untuk Facebook Reels.",
        "Cara Download Facebook Reels",
        content
    )


@app.route("/faq")
def faq():

    content = """
    <h2>Apakah ReelSave gratis?</h2>
    <p>
    ReelSave dirancang sebagai alat online sederhana untuk
    memproses URL Facebook Reel yang dapat diakses secara publik.
    </p>

    <h2>Apakah saya perlu login?</h2>
    <p>
    ReelSave tidak meminta Anda memasukkan password Facebook
    atau kredensial akun Facebook.
    </p>

    <h2>Mengapa sebuah Reel tidak dapat diproses?</h2>
    <p>
    Tidak semua URL dapat diproses. Konten yang tidak publik,
    URL yang salah, perubahan pada platform sumber, atau
    keterbatasan teknis dapat menyebabkan proses gagal.
    </p>

    <h2>Apakah ReelSave bagian dari Facebook?</h2>
    <p>
    Tidak. ReelSave adalah layanan independen dan tidak
    berafiliasi dengan Facebook atau Meta.
    </p>

    <h2>Apakah semua video boleh diunduh?</h2>
    <p>
    Anda bertanggung jawab memastikan bahwa Anda memiliki
    hak atau izin yang diperlukan untuk mengunduh dan
    menggunakan konten tersebut.
    </p>
    """

    return page(
        "FAQ",
        "Pertanyaan umum tentang ReelSave Facebook Reels Downloader.",
        "Frequently Asked Questions",
        content
    )


@app.route("/about")
def about():

    content = """
    <h2>Tentang ReelSave</h2>

    <p>
    ReelSave adalah alat web yang dirancang untuk membantu
    pengguna memproses URL Facebook Reel yang dapat diakses
    secara publik.
    </p>

    <p>
    Fokus ReelSave adalah menyediakan antarmuka sederhana,
    cepat, dan mudah digunakan dari perangkat desktop maupun
    mobile.
    </p>

    <p>
    ReelSave tidak berafiliasi, disponsori, atau didukung
    oleh Facebook atau Meta.
    </p>
    """

    return page(
        "About ReelSave",
        "Tentang ReelSave Facebook Reels Downloader.",
        "Tentang ReelSave",
        content
    )


@app.route("/privacy")
def privacy():

    content = """
    <h2>Informasi Umum</h2>

    <p>
    Privasi pengunjung penting bagi ReelSave. Halaman ini
    menjelaskan secara umum bagaimana layanan dapat menangani
    informasi teknis yang diperlukan untuk menjalankan website.
    </p>

    <h2>URL yang diproses</h2>

    <p>
    URL yang dikirim melalui formulir digunakan untuk
    menjalankan proses download. Jangan memasukkan informasi
    pribadi atau rahasia ke dalam formulir.
    </p>

    <h2>Log dan informasi teknis</h2>

    <p>
    Infrastruktur hosting dapat membuat log teknis seperti
    alamat IP, waktu permintaan, status HTTP, dan informasi
    perangkat untuk keamanan, troubleshooting, dan operasional.
    </p>

    <h2>Cookies dan layanan pihak ketiga</h2>

    <p>
    Jika ReelSave menggunakan analytics, iklan, atau layanan
    pihak ketiga di kemudian hari, kebijakan privasi ini perlu
    diperbarui untuk menjelaskan layanan tersebut.
    </p>

    <h2>Kontak</h2>

    <p>
    Untuk pertanyaan mengenai privasi, silakan gunakan halaman
    Contact.
    </p>
    """

    return page(
        "Privacy Policy",
        "Kebijakan privasi ReelSave.",
        "Privacy Policy",
        content
    )


@app.route("/terms")
def terms():

    content = """
    <h2>Penggunaan Layanan</h2>

    <p>
    Anda bertanggung jawab atas URL dan konten yang Anda
    masukkan ke ReelSave.
    </p>

    <h2>Hak atas Konten</h2>

    <p>
    Jangan menggunakan ReelSave untuk mengunduh atau
    mendistribusikan konten yang Anda tidak memiliki hak
    atau izin untuk gunakan.
    </p>

    <h2>Penyalahgunaan</h2>

    <p>
    Penggunaan otomatis berlebihan, tindakan yang mengganggu
    server, atau aktivitas yang melanggar hukum tidak diperbolehkan.
    </p>

    <h2>Ketersediaan</h2>

    <p>
    ReelSave dapat mengalami gangguan, perubahan, atau
    penghentian fitur tanpa pemberitahuan sebelumnya.
    </p>
    """

    return page(
        "Terms of Service",
        "Ketentuan penggunaan ReelSave.",
        "Terms of Service",
        content
    )


@app.route("/disclaimer")
def disclaimer():

    content = """
    <h2>Disclaimer</h2>

    <p>
    ReelSave bukan bagian dari, tidak berafiliasi dengan,
    dan tidak didukung oleh Facebook atau Meta.
    </p>

    <p>
    ReelSave menyediakan alat pemrosesan URL. Pengguna tetap
    bertanggung jawab atas penggunaan konten yang diunduh
    melalui layanan ini.
    </p>

    <p>
    Pastikan Anda memiliki hak atau izin yang diperlukan
    sebelum mengunduh, menyimpan, atau menggunakan kembali
    konten.
    </p>
    """

    return page(
        "Disclaimer",
        "Disclaimer penggunaan ReelSave.",
        "Disclaimer",
        content
    )


@app.route("/copyright")
def copyright():

    content = """
    <h2>Copyright</h2>

    <p>
    ReelSave menghormati hak cipta dan hak kekayaan intelektual.
    </p>

    <p>
    Jika Anda memiliki kekhawatiran mengenai penggunaan
    konten melalui layanan ini, silakan hubungi kami dengan
    informasi yang cukup untuk mengidentifikasi masalah tersebut.
    </p>

    <p>
    <strong>Catatan:</strong> halaman ini merupakan informasi
    umum dan bukan nasihat hukum.
    </p>
    """

    return page(
        "Copyright",
        "Informasi copyright dan hak kekayaan intelektual ReelSave.",
        "Copyright",
        content
    )


@app.route("/contact")
def contact():

    content = """
    <h2>Hubungi ReelSave</h2>

    <p>
    Untuk pertanyaan mengenai layanan, masalah teknis,
    privasi, atau copyright, Anda dapat menghubungi pemilik
    website melalui alamat email resmi ReelSave.
    </p>

    <p>
    <strong>Email:</strong>
    johankupang27@gmail.com
    </p>

    <p>
    Sebelum website dipublikasikan secara resmi, ganti alamat
    email contoh di atas dengan email yang benar-benar Anda gunakan.
    </p>
    """

    return page(
        "Contact",
        "Hubungi ReelSave.",
        "Contact ReelSave",
        content
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
