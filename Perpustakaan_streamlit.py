import streamlit as st
import csv
import os
import sys

# Mengatur limit rekursi agar tidak error saat string sangat panjang
sys.setrecursionlimit(2000)

# --- 1. FUNGSI LOAD DATA DARI CSV ---
@st.cache_data # Caching agar tidak baca file berulang-ulang setiap klik
def baca_data_buku(filename):
    data_buku = []
    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # Pastikan key 'penerbit_buku' ada jika di CSV tidak ada, beri default
                if 'penerbit_buku' not in row:
                    row['penerbit_buku'] = "-" 
                data_buku.append(row)
        return data_buku
    except FileNotFoundError:
        st.error(f"Error: File {filename} tidak ditemukan.")
        return []

# --- 2. ALGORITMA MERGE SORT (REKURSIF) ---
def merge_sort(data, key_sort='kode_buku'):
    if len(data) <= 1:
        return data

    tengah = len(data) // 2
    kiri = data[:tengah]
    kanan = data[tengah:]

    kiri_sorted = merge_sort(kiri, key_sort)
    kanan_sorted = merge_sort(kanan, key_sort)

    return merge(kiri_sorted, kanan_sorted, key_sort)

def merge(kiri, kanan, key_sort):
    hasil = []
    i = j = 0

    while i < len(kiri) and j < len(kanan):
        # Mengambil value berdasarkan key yang dipilih user
        val_kiri = kiri[i].get(key_sort, "").lower()
        val_kanan = kanan[j].get(key_sort, "").lower()

        if val_kiri <= val_kanan:
            hasil.append(kiri[i])
            i += 1
        else:
            hasil.append(kanan[j])
            j += 1

    hasil.extend(kiri[i:])
    hasil.extend(kanan[j:])
    
    return hasil

# --- 3. ALGORITMA FUZZY SEARCH (LEVENSHTEIN REKURSIF) ---
# Menggunakan lru_cache bawaan python atau memo manual tetap oke
def levenshtein_recursive(s1, s2, memo=None):
    if memo is None:
        memo = {}
        
    if (s1, s2) in memo:
        return memo[(s1, s2)]

    if len(s1) == 0: return len(s2)
    if len(s2) == 0: return len(s1)

    if s1[0] == s2[0]:
        res = levenshtein_recursive(s1[1:], s2[1:], memo)
    else:
        res = 1 + min(
            levenshtein_recursive(s1[1:], s2, memo),    # Hapus
            levenshtein_recursive(s1, s2[1:], memo),    # Sisip
            levenshtein_recursive(s1[1:], s2[1:], memo) # Ganti
        )
    
    memo[(s1, s2)] = res
    return res

# --- 4. LOGIKA PENCARIAN (MODIFIKASI KOLOM DINAMIS) ---
def cari_buku_fuzzy(keyword, data_buku, target_column='nama_buku'):
    hasil_pencarian = []
    
    keyword_clean = keyword.lower().strip()
    kata_kunci_user = keyword_clean.split()
    
    if not kata_kunci_user:
        return []

    for buku in data_buku:
        # MODIFIKASI: Mengambil data sesuai kolom yang dipilih user (Judul/Kode/Penulis)
        text_target = buku.get(target_column, "").lower()
        kata_target = text_target.split()
        
        total_score_buku = 0
        
        for k_user in kata_kunci_user:
            score_terkecil_untuk_kata_ini = float('inf')
            
            for k_target in kata_target:
                dist = levenshtein_recursive(k_user, k_target)
                if dist < score_terkecil_untuk_kata_ini:
                    score_terkecil_untuk_kata_ini = dist
            
            total_score_buku += score_terkecil_untuk_kata_ini
            
        # Toleransi
        panjang_karakter_user = len(keyword_clean.replace(" ", ""))
        batas_toleransi = panjang_karakter_user * 0.7 
        
        if total_score_buku <= batas_toleransi:
            hasil_pencarian.append({
                'Kode': buku['kode_buku'],
                'Judul': buku['nama_buku'],
                'Penulis': buku['penulis_buku'],
                'Penerbit': buku.get('penerbit_buku', '-'),
                'Offset': total_score_buku # Untuk keperluan debugging/sorting
            })
    
    # Urutkan berdasarkan score terendah
    hasil_pencarian.sort(key=lambda x: x['Offset'])
    return hasil_pencarian

# --- 5. INTERFACE STREAMLIT ---
def main():
    st.set_page_config(page_title="Sistem Pencarian Buku", layout="wide")
    
    st.title("📚 Sistem Pencarian Buku Perpustakaan")
    st.markdown("Implementasi: **Merge Sort** & **Fuzzy Search (Levenshtein)**")
    
    # Load Data
    nama_file = 'FP_buku.csv'
    if not os.path.exists(nama_file):
        st.error(f"File database '{nama_file}' tidak ditemukan! Harap upload file CSV.")
        return

    data_raw = baca_data_buku(nama_file)
    
    # --- SIDEBAR CONFIGURATION ---
    st.sidebar.header("Navigasi & Filter")
    
    # Pilihan Mode: Tabel Utama atau Pencarian
    mode_aplikasi = st.sidebar.radio("Pilih Mode:", ["Lihat Daftar Buku", "Pencarian Spesifik"])

    # --- MODE 1: LIHAT DAFTAR BUKU (SORTING) ---
    if mode_aplikasi == "Lihat Daftar Buku":
        st.subheader("📂 Daftar Koleksi Buku")
        
        # Opsi Sorting
        sort_options = {
            "Kode Buku": "kode_buku",
            "Judul Buku": "nama_buku",
            "Penulis": "penulis_buku",
            "Penerbit": "penerbit_buku"
        }
        
        # Default sort by Kode Buku (index 0)
        pilihan_sort = st.sidebar.selectbox(
            "Urutkan berdasarkan:", 
            list(sort_options.keys()), 
            index=0
        )
        
        key_sorting = sort_options[pilihan_sort]
        
        # Proses Sorting (Merge Sort)
        with st.spinner(f"Mengurutkan data berdasarkan {pilihan_sort}..."):
            data_sorted = merge_sort(data_raw, key_sort=key_sorting)
        
        st.success(f"Menampilkan {len(data_sorted)} buku diurutkan berdasarkan **{pilihan_sort}**.")
        
        # Tampilkan Tabel
        st.dataframe(
            data_sorted, 
            use_container_width=True,
            column_config={
                "kode_buku": "Kode",
                "nama_buku": "Judul Buku",
                "penulis_buku": "Penulis",
                "penerbit_buku": "Penerbit"
            }
        )

    # --- MODE 2: PENCARIAN (FUZZY SEARCH) ---
    elif mode_aplikasi == "Pencarian Spesifik":
        st.subheader("🔍 Pencarian Fuzzy Search")
        
        # Input User
        col1, col2 = st.columns([3, 1])
        
        with col1:
            keyword = st.text_input("Masukkan kata kunci pencarian:", placeholder="Contoh: sytem programing")
            
        with col2:
            # Pilihan Kolom Pencarian
            search_field_map = {
                "Judul Buku": "nama_buku",
                "Kode Buku": "kode_buku",
                "Penulis": "penulis_buku",
                "Penerbit": "penerbit_buku"
            }
            search_category = st.selectbox("Cari di kolom:", list(search_field_map.keys()))
            target_col = search_field_map[search_category]

        tombol_cari = st.button("Cari Buku")
        
        if tombol_cari:
            if not keyword:
                st.warning("Silakan masukkan kata kunci terlebih dahulu.")
            else:
                with st.spinner("Sedang mencari..."):
                    # Eksekusi Fuzzy Search
                    hasil = cari_buku_fuzzy(keyword, data_raw, target_column=target_col)
                
                if hasil:
                    st.success(f"Ditemukan {len(hasil)} hasil yang mirip.")
                    st.dataframe(hasil, use_container_width=True)
                else:
                    st.error("Tidak ditemukan buku yang cocok dengan kata kunci tersebut.")
                    st.markdown("*Tips: Coba kurangi kata kunci atau periksa kembali ejaan (sistem toleransi typo aktif).*")

if __name__ == "__main__":

    main()


