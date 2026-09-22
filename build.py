#!/usr/bin/env python3
"""Assemble index.html for Apotek Waluya (redesign) from parts/ + css/ + data/.

Same contract as the first version: no npm, this script IS the build step.
New in this version: CSS lives in css/*.css and is injected at {{CSS}}, so the
stylesheet is written as plain CSS instead of being smuggled through the
part-concatenation trick.

Usage: python3 build.py
"""
import json, os, re, html
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
PARTS = os.path.join(ROOT, "parts")
CSSDIR = os.path.join(ROOT, "css")

WA = "6281234567890"          # ganti nomor ini saat dipakai klien asli
SITE = "https://apotek-waluya.example.id"

meta = json.load(open(os.path.join(ROOT, "assets/img-meta.json")))
data = json.load(open(os.path.join(ROOT, "data/produk.json")))

# prefix kode label per kategori — dipakai sebagai "nomor rak" di kartu produk
KODE = {"vitamin": "VIT", "obat": "OBT", "alkes": "ALK",
        "bayi": "BYI", "kulit": "KLT", "higienis": "HGN"}


def rupiah(n):
    return "Rp " + f"{n:,}".replace(",", ".")


def wa_link(teks):
    return f"https://wa.me/{WA}?text={quote(teks)}"


def picture(key, alt, cls="", sizes="100vw", lazy=True, card=False, ratio=None):
    """Responsive <picture>: WebP srcset + LQIP + intrinsic size (no CLS).

    ratio: optional CSS aspect-ratio. When set, the rendered box is governed by
    CSS, so the HTML height attribute can never win over it (the old page had a
    photo stuck at 800px tall for exactly that reason).
    """
    m = meta[key]
    e = html.escape(alt, quote=True)
    lq = m["lqip"]
    st = f"background-image:url({lq});background-size:cover"
    if ratio:
        st += f";aspect-ratio:{ratio};height:auto;object-fit:cover"
    if card:
        c = m["card"]
        return (f'<img class="{cls}" src="assets/webp/{c["file"]}" '
                f'width="{c["w"]}" height="{c["h"]}" alt="{e}" '
                f'loading="{"lazy" if lazy else "eager"}" decoding="async" '
                f'style="{st}">')
    v = m["variants"]
    srcset = ", ".join(f'assets/webp/{v[w]["file"]} {w}w' for w in ("480", "800", "1200"))
    big = v["1200"]
    return (f'<picture><source type="image/webp" srcset="{srcset}" sizes="{sizes}">'
            f'<img class="{cls}" src="assets/webp/{v["800"]["file"]}" '
            f'width="{big["w"]}" height="{big["h"]}" alt="{e}" '
            f'loading="{"lazy" if lazy else "eager"}" decoding="async" '
            f'style="{st}"></picture>')


def render_produk():
    """Kartu produk = label apotek: kode rak, nama, isi, harga, aksi teks."""
    nama_kat = {k["id"]: k["nama"] for k in data["kategori"]}
    out = []
    seq = {}
    for p in data["produk"]:
        stem = os.path.splitext(p["foto"])[0]
        seq[p["kat"]] = seq.get(p["kat"], 0) + 1
        kode = f'{KODE.get(p["kat"], "OBT")}-{seq[p["kat"]]:02d}'
        pesan = (f"Halo Apotek Waluya, saya mau tanya stok "
                 f"{p['nama']} ({p['satuan']}). Apakah tersedia?")
        tag = f'<span class="pcard__tag">{p["tag"]}</span>' if p["tag"] else ""
        cari = html.escape((p["nama"] + " " + p["desc"] + " " + kode).lower(), quote=True)
        out.append(f'''<article class="pcard" data-kat="{p['kat']}" data-katnama="{nama_kat.get(p['kat'], '')}" data-satuan="{p['satuan']}" data-cari="{cari}">
  <div class="pcard__foto">
    <button type="button" class="pcard__buka" aria-label="Lihat keterangan {html.escape(p['nama'], quote=True)}">{picture(stem, p['nama'], "pcard__img", "(max-width:640px) 96px, (max-width:1000px) 30vw, 260px", card=True)}</button>{tag}
  </div>
  <div class="pcard__body">
    <span class="pcard__code">{kode} &middot; {p['satuan']}</span>
    <h3 class="pcard__nama">{p['nama']}</h3>
    <p class="pcard__desc">{p['desc']}</p>
    <div class="pcard__foot">
      <span class="pcard__harga">{rupiah(p['harga'])}</span>
      <a class="pcard__cta" href="{wa_link(pesan)}" target="_blank" rel="noopener">Cek stok</a>
    </div>
  </div>
</article>''')
    return "\n".join(out)


def render_kategori():
    """Filter kategori sebagai daftar baris + jumlah produk, bukan chip."""
    hitung = {}
    for p in data["produk"]:
        hitung[p["kat"]] = hitung.get(p["kat"], 0) + 1
    out = [f'<button type="button" data-filter="all" aria-pressed="true">'
           f'Semua<span>{len(data["produk"])}</span></button>']
    for k in data["kategori"]:
        out.append(f'<button type="button" data-filter="{k["id"]}" aria-pressed="false">'
                   f'{k["nama"]}<span>{hitung.get(k["id"], 0)}</span></button>')
    return "\n          ".join(out)


def render_layanan():
    """Daftar layanan sebagai baris editorial bernomor, bukan 3 kartu sejajar."""
    layanan = [
        ("farmasi-rak", "Tebus Resep Dokter",
         "Kirim foto resep lewat WhatsApp, obat disiapkan lalu diambil atau diantar. "
         "Resep obat keras kami catat sesuai aturan."),
        ("konsul-apoteker", "Konsultasi Apoteker",
         "Bingung bedanya dua obat, atau dosis untuk anak? Tanya langsung ke apoteker "
         "berlisensi, tanpa biaya."),
        ("farmasi-pelanggan", "Cek Tekanan & Gula Darah",
         "Pemeriksaan singkat di tempat, gratis untuk pembeli. Hasilnya dicatat supaya "
         "bisa dipantau dari bulan ke bulan."),
        ("alkes-tensi-digital", "Alat Kesehatan & Sewa",
         "Tensimeter, nebulizer, termometer, kursi roda. Sebagian bisa disewa harian "
         "kalau hanya butuh sementara."),
    ]
    out = []
    for i, (foto, judul, teks) in enumerate(layanan):
        out.append(f'''<article class="svc">
  <span class="svc__n">{i+1:02d}</span>
  <div class="svc__txt">
    <h3>{judul}</h3>
    <p>{teks}</p>
  </div>
  <div class="svc__foto">{picture(foto, judul, "svc__img", "(max-width:880px) 92vw, 300px", ratio="4/3")}</div>
</article>''')
    return "\n".join(out)


def render_alur():
    """Cara pesan: 3 langkah sebagai timeline bernomor mono."""
    langkah = [
        ("Kirim daftar atau foto resep",
         "Sebutkan nama obat dan jumlahnya. Kalau pakai resep, foto yang terbaca sudah cukup."),
        ("Kami konfirmasi ketersediaan &amp; total",
         "Dibalas apoteker di jam buka. Kalau ada yang kosong, kami tawarkan padanannya."),
        ("Ambil di toko atau minta diantar",
         "Bayar di kasir atau transfer/QRIS. Antar sekitar Dipatiukur, bisa juga kurir instan."),
    ]
    out = []
    for i, (judul, teks) in enumerate(langkah):
        out.append(f'''<li class="step">
  <span class="step__n">LANGKAH {i+1}</span>
  <div>
    <h3>{judul}</h3>
    <p>{teks}</p>
  </div>
</li>''')
    return "\n".join(out)


def render_stats():
    hitung = {}
    for p in data["produk"]:
        hitung[p["kat"]] = hitung.get(p["kat"], 0) + 1
    return "".join(f'<span>{k["nama"]} <b>{hitung.get(k["id"], 0)}</b></span>'
                   for k in data["kategori"])


def main():
    css = "\n".join(
        open(os.path.join(CSSDIR, f), encoding="utf-8").read().strip()
        for f in sorted(os.listdir(CSSDIR)) if f.endswith(".css"))

    ctx = {
        "CSS": css,
        "PRODUK": render_produk(),
        "KATEGORI": render_kategori(),
        "LAYANAN": render_layanan(),
        "ALUR": render_alur(),
        "STATS": render_stats(),
        "JUMLAH": str(len(data["produk"])),
        "WA": WA,
        "SITE": SITE,
    }

    order = ["head", "katalog", "layanan", "kunjungi", "footer", "scripts"]
    doc = "\n".join(open(os.path.join(PARTS, n + ".html"), encoding="utf-8").read()
                    for n in order)

    def sub_img(m):
        key, alt, cls, sizes = m.group(1), m.group(2), m.group(3), m.group(4) or "100vw"
        return picture(key, alt, cls, sizes)

    def sub_card(m):
        key, alt, cls = m.group(1), m.group(2), m.group(3)
        return picture(key, alt, cls, "(max-width:640px) 46vw, 260px", card=True)

    doc = re.sub(r"\{\{IMG:([^|}]+)\|([^|}]*)\|([^|}]*)\|?([^}]*)\}\}", sub_img, doc)
    doc = re.sub(r"\{\{CARD:([^|}]+)\|([^|}]*)\|([^}]*)\}\}", sub_card, doc)
    for k, v in ctx.items():
        doc = doc.replace("{{" + k + "}}", v)

    left = re.findall(r"\{\{[A-Z_]+[^}]*\}\}", doc)
    if left:
        raise SystemExit(f"placeholder belum diganti: {left[:5]}")

    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"index.html  {len(doc)/1024:.1f} KB  ({len(data['produk'])} produk)")


if __name__ == "__main__":
    main()
