import streamlit as st
import csv
import os
import sys

sys.setrecursionlimit(2000)

@st.cache_data # Caching 
def baca_data_buku(filename, timestamp):
    data_buku = []
    with open(filename, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
        data_buku.append(row)
    return data_buku


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
        # sort berdasarkan key
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

def levenshtein_distance(s1, s2):
    l_s1 = len(s1)
    l_s2 = len(s2)
    table = [[0 for _ in range(l_s1+1)] for _ in range(l_s2+1)] #zeros table
    for i in range(1, (l_s1+1)):
        table[0][i] = i
    for i in range(1, (l_s2+1)):
        table[i][0] = i
    for i in range(1,l_s2+1):
        for j in range(1,l_s1+1):
            if s1[j-1] == s2[i-1]:
                table[i][j] = table[i-1][j-1]
            else:
                table[i][j] = (min(
                    table[i-1][j], #Hapus
                    table[i][j-1], #Sisip
                    table[i-1][j-1]) #ganti
                +1)
    return table[l_s2][l_s1]

def cari_buku_fuzzy(keyword, data_buku, target_column='nama_buku'):
    hasil_pencarian = []
    
    keyword_clean = keyword.lower().strip()
    kata_kunci_user = keyword_clean.split()
    
    if not kata_kunci_user:
        return []

    for buku in data_buku:
        text_target = buku.get(target_column, "").lower()
        kata_target = text_target.split()
        
        total_score_buku = 0
        
        for k_user in kata_kunci_user:
            score_terkecil_untuk_kata_ini = float('inf')
            
            for k_target in kata_target:
                dist = levenshtein_distance(k_user, k_target)
                if dist < score_terkecil_untuk_kata_ini:
                    score_terkecil_untuk_kata_ini = dist
            
            total_score_buku += score_terkecil_untuk_kata_ini
            
        panjang_karakter_user = len(keyword_clean.replace(" ", ""))
        batas_toleransi = panjang_karakter_user * 0.7 #Toleransi
        
        if total_score_buku <= batas_toleransi:
            hasil_pencarian.append({
                'Kode': buku['kode_buku'],
                'Judul': buku['nama_buku'],
                'Penulis': buku['penulis_buku'],
                'Penerbit': buku.get('penerbit_buku', '-'),
                'Offset': total_score_buku #offset
            })
    
    # Urutkan berdasarkan score lalu kode
    hasil_pencarian.sort(key=lambda x: (x['Offset'], x['Kode']))
    return hasil_pencarian

# --- 5. INTERFACE STREAMLIT ---
def main():
    st.set_page_config(page_title="Sistem Pencarian Buku", layout="wide")
    
    st.title("📚 Sistem Pencarian Buku Perpustakaan")
    st.markdown("Implementasi: **Merge Sort** & **Fuzzy Search (Levenshtein)**")
    
    
    nama_file = 'FP_buku.csv'
    if not os.path.exists(nama_file):
        st.error(f"File database '{nama_file}' tidak ditemukan! Harap upload file CSV.")
        return
    timestamp = os.path.getmtime(nama_file) #load file's time of update
    data_raw = baca_data_buku(nama_file, timestamp)# Load Data
    
    st.sidebar.header("Navigasi & Filter")
    mode_aplikasi = st.sidebar.radio("Pilih Mode:", ["Lihat Daftar Buku", "Pencarian Spesifik"])

    if mode_aplikasi == "Lihat Daftar Buku":      
        st.subheader("📂 Daftar Koleksi Buku")
        sort_options = {
            "Kode Buku": "kode_buku",
            "Judul Buku": "nama_buku",
            "Penulis": "penulis_buku",
            "Penerbit": "penerbit_buku"
        }        
        pilihan_sort = st.sidebar.selectbox(
            "Urutkan berdasarkan:", 
            list(sort_options.keys()), 
            index=0
        )      
        key_sorting = sort_options[pilihan_sort]
        with st.spinner(f"Mengurutkan data berdasarkan {pilihan_sort}..."):
            data_sorted = merge_sort(data_raw, key_sort=key_sorting)
        st.success(f"Menampilkan {len(data_sorted)} buku diurutkan berdasarkan **{pilihan_sort}**.")
        st.dataframe( #tabel
            data_sorted, 
            use_container_width=True,
            column_config={
                "kode_buku": "Kode",
                "nama_buku": "Judul Buku",
                "penulis_buku": "Penulis",
                "penerbit_buku": "Penerbit"
            }
        )
    elif mode_aplikasi == "Pencarian Spesifik":
        st.subheader("🔍 Pencarian Fuzzy Search")
        col1, col2 = st.columns([3, 1]) #user Input
        
        with col1:
            keyword = st.text_input("Masukkan kata kunci pencarian:", placeholder="Contoh: sytem programing")
            
        with col2:
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
                    hasil = cari_buku_fuzzy(keyword, data_raw, target_column=target_col)
                if hasil:
                    st.success(f"Ditemukan {len(hasil)} hasil yang mirip.")
                    st.dataframe(hasil, use_container_width=True)
                else:
                    st.error("Tidak ditemukan buku yang cocok dengan kata kunci tersebut.")
                    st.markdown("*Tips: Coba kurangi kata kunci atau periksa kembali ejaan.*")


if __name__ == "__main__":
    main()











