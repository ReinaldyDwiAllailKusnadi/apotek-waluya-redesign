# Apotek Waluya — Redesign "Label Apotek"

Versi desain ulang dari landing page Apotek Waluya. **Topik sama, arah desain
berbeda**: bukan hero tengah + tiga kartu layanan, tapi **papan counter farmasi**
— surface utama halaman adalah katalog, bukan tagline.

**Live:** http://20.193.68.109/apotek2/
**Versi lama (v1):** http://20.193.68.109/apotek/

## Kenapa didesain ulang

Versi pertama memakai pola yang terlalu mudah ditebak mesin: hero tengah,
tiga kartu fitur sejajar, gradient, kartu membulat. Versi ini menghindari
semua itu dengan aturan yang bisa diukur, bukan selera:

- **Nol gradient, nol elemen bernada ungu/biru, nol emoji.** Terukur 0/0/0.
- **Radius hampir nol.** Hanya 0px, 2px, dan 50% (titik status & tombol bulat mobile).
- **Surface = Explore.** Yang pertama dilihat adalah isi rak (23 produk), bukan slogan.
- **Layanan = baris editorial bernomor**, bukan tiga kartu sejajar.
- **Data pakai mono** (IBM Plex Mono) — kode rak, harga, jam buka. Judul pakai Archivo.
- **Foto sendiri, bukan stok.** Papan bukti menyebut bahwa foto itu rak asli.

## Struktur

```
build.py                    rakit parts/ + data/ + css/ -> index.html (build step, tanpa npm)
parts/                      potongan HTML (head, katalog, layanan, kunjungi, footer, scripts)
css/                        CSS asli, dipisah per lapisan:
  10-base.css                 token, reset, tipografi, tombol
  20-masthead.css             baris atas + papan counter pembuka
  30-catalog.css              rail filter + kisi produk (surface utama)
  40-detail.css               panel <dialog> keterangan produk + tombol WA mengambang
  50-sections.css             layanan, alur, kunjungi, footer
data/produk.json            23 produk, 6 kategori (sumber katalog)
index.html                  hasil build — jangan diedit langsung
assets/webp/                varian WebP responsif (kartu 600 + 480/800/1200) — ini yang dipakai halaman
deploy.py                   deploy ke /var/www/apotek2 + verifikasi setiap aset via HTTP
qa/                         screenshot QA (bukan bagian dari website)
```

## Alur kerja

```bash
python3 build.py             # parts/ + css/ + data/ -> index.html
python3 deploy.py            # deploy ke /var/www/apotek2 + verifikasi 200 tiap aset
```

`index.html` adalah **hasil build**. Untuk mengubah isi halaman, edit
`parts/*.html`, `css/*.css`, atau `data/produk.json`, lalu jalankan
`python3 build.py`. Edit langsung ke `index.html` akan hilang di build berikutnya.

## Yang membedakan dari versi lama

- **Katalog jadi halaman utama.** Rail filter menempel di kiri saat scroll;
  pencarian menyaring nama, kategori, dan kode rak sekaligus. Ada dua kolom cari
  (papan pembuka + rail) yang **menyaring katalog yang sama** — bukan dua daftar hasil.
- **Kartu produk = label rak**: kode, nama, isi, harga mono, dua aksi teks.
  Deskripsi lengkap tidak ditaruh di kartu, tapi di panel `<dialog>` "Keterangan".
- **Tanpa tombol mengambang.** Baris atas *sticky* sudah memuat WhatsApp & Telepon,
  jadi satu aksi WhatsApp yang selalu terlihat — bukan dua yang saling menutupi.
- **Jam buka dihitung di zona Asia/Jakarta**, bukan zona waktu pengunjung —
  supaya status "Buka/Tutup" benar untuk siapa pun yang membuka dari luar WIB.
  Kalau hari ini sudah tutup, yang disebut jam buka hari berikutnya
  (Sabtu malam -> "buka besok 08.00", karena Minggu buka jam 8).
- **Layanan bernomor 01–04** dengan foto, bukan tiga kartu sejajar.

## Hasil audit terukur

Semua angka di bawah hasil pengukuran di browser, bukan perkiraan visual.

- **Overflow horizontal: 0px di 19 lebar viewport** (320 → 1920px).
- **Kontras WCAG AA: 0 pelanggaran** (dihitung dengan komposit alpha).
- **Ring fokus keyboard: 0 dari 47 elemen interaktif yang tanpa ring.**
- **Tepi kiri rata sempurna**: tagline, H1, paragraf, dan judul bagian semua di 156.5px.
- **Pencarian ada di atas lipatan** — desktop y=536, mobile y=474 (viewport 900/844).
  Versi lama menaruh input cari di y=402 desktop tapi **y=961 di mobile** (di bawah lipatan).
- **Nol elemen tertutup** oleh elemen mengambang. Tombol WhatsApp mengambang
  dihapus karena baris atas *sticky* sudah memuat tombol WA yang selalu terlihat;
  sebelumnya tombol itu terukur menutupi 2 elemen di 390px, 1 di 360px, 1 di 1440px.
- **Kartu produk seragam** dalam satu baris (215×429 dan 215×448 — tinggi beda
  karena deskripsi dua baris vs satu baris, bukan karena lebar).
- **Status jam buka lolos 6/6 kasus** (Selasa pagi/malam, Sabtu pagi/malam,
  Minggu pagi/malam) dengan jam sistem dipalsukan.
- **Panel keterangan produk terverifikasi**: nama, harga, kategori, isi, dan
  pesan WhatsApp terisi otomatis ("Halo Apotek Waluya, saya mau tanya stok
  Paracetamol 500mg (strip (10 tablet)). Apakah tersedia?").
- Target sentuh: hanya tautan *inline* di dalam kalimat yang di bawah 24px —
  itu pengecualian eksplisit WCAG 2.5.8. Tautan yang berdiri sendiri (footer,
  nav, tombol) semuanya >= 24px.

## Bagian yang perlu diganti sebelum dipakai client

- Nomor WhatsApp `6281234567890` (tombol mengambang, footer, "Cek stok",
  tebus resep, dan form kontak)
- Email `halo@apotek-waluya.example.id`, alamat `Jl. Dipatiukur No. 112`,
  jam buka (`Sen–Sab 07.00–22.00 · Min 08.00–20.00`)
- Nama apotek, nomor Surat Izin Apotek, daftar produk di `data/produk.json`
- Foto: diganti foto asli apotek

## Catatan teknis

- **Foto master tidak di-commit.** Yang masuk repo hanya varian WebP
  (`assets/webp/`, 4,7 MB). `assets/img/` dan `photo-manifest.json` ada di `.gitignore`.
- **Tidak ada harga stok real-time.** Tombol "Cek stok" membuka WhatsApp dengan
  pesan yang sudah terisi nama produk, jadi apoteker yang mengonfirmasi
  ketersediaan dan harga. Ini disengaja: harga obat berubah dan stok tidak boleh
  ditampilkan basi.
- **Tanpa backend, tanpa npm.** Build step cuma Python standar + nginx.
