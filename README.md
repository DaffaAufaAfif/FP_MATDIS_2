#  FP_MATDIS_2: Smart Library Search System

**Implementasi Fuzzy Search (Levenshtein Recursion) dan Merge Sort pada Sistem Perpustakaan.**

##
###  Latar Belakang

Mencari buku pada perpustakaan yang memiliki ribuan koleksi data dapat memakan waktu yang sangat lama jika dilakukan secara manual. Tantangan utamanya adalah:

1.  **Inefisiensi:** Sistem pencarian biasa (Linear Search) dan pengurutan naif (Bubble Sort) berjalan lambat pada data dalam jumlah besar.
2.  **Human Error:** Pengguna sering melakukan kesalahan pengetikan (*typo*) saat mencari judul buku, menyebabkan sistem pencarian konvensional gagal menemukan hasil yang relevan.

Proyek ini dibuat untuk mengatasi masalah tersebut dengan menerapkan algoritma **Merge Sort** untuk pengurutan data yang efisien dan **Fuzzy Search (Levenshtein Distance)** untuk menangani kesalahan input.

### Input/Variabel:

* **data_raw (list of dict):** Kumpulan data buku mentah yang dibaca dari file CSV (berisi Kode, Judul, Penulis, Penerbit).
* **mode_aplikasi (string):** Pilihan menu navigasi user ("Lihat Daftar Buku" atau "Pencarian Spesifik").
* **key_sort (string):** Atribut yang dipilih user sebagai dasar pengurutan (misal: 'nama_buku', 'penulis_buku').
* **keyword (string):** Kata kunci pencarian yang diinputkan pengguna (bisa mengandung *typo*).
* **target_column (string):** Kolom target pencarian yang dipilih user (Judul/Kode/Penulis/Penerbit).
* **hasil_pencarian (list):** Daftar buku yang relevan setelah dihitung skor kemiripannya.

### Penjelasan Fungsi:

* **merge_sort(data, key_sort):** Fungsi ini mengimplementasikan algoritma pengurutan *Divide and Conquer* dengan kompleksitas waktu $O(n \log n)$. Data dipecah menjadi sub-list terkecil secara rekursif, kemudian digabungkan kembali (*merge*) sambil dibandingkan nilainya berdasarkan `key_sort`. return: List data buku yang sudah terurut.
* **levenshtein_recursive(s1, s2):** Fungsi inti untuk *Fuzzy Search*. Menghitung jarak edit minimum (jumlah operasi hapus, sisip, ganti) yang diperlukan untuk mengubah string `s1` (input user) menjadi `s2` (data buku). Menggunakan pendekatan rekursif dengan *memoization*. return: Nilai integer (jarak edit/skor error).
* **cari_buku_fuzzy(keyword, data_buku):** Fungsi *wrapper* yang memproses input user. Fungsi ini memecah `keyword` menjadi per kata, memanggil `levenshtein_recursive` terhadap setiap data buku, dan memfilter hasil berdasarkan batas toleransi. return: List buku yang memiliki skor error di bawah batas toleransi.

### Link Stramlit:
https://github.com/DaffaAufaAfif/FP_MATDIS_2
