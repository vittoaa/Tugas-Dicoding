import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Judul Aplikasi
st.title("Kondisi Udara Kota Changping 🌍")

# **Load Dataset**
@st.cache_data
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), "PRSA_Data_Changping_20130301-20170228.csv")
    changping_df = pd.read_csv(file_path)
    return changping_df

changping_df = load_data()
st.subheader("Pilih jika ingin melihat detail perihal data Kota Changping")
# **Checkbox untuk Menampilkan Boxplot Sebelum Imputasi**
if st.checkbox("Tampilkan Boxplot Sebelum Imputasi"):
    st.subheader("Boxplot Sebelum Imputasi Outlier")
    fig, axes = plt.subplots(2, 2, figsize=(12, 6))
    sns.boxplot(y=changping_df['TEMP'], ax=axes[0, 0])
    axes[0, 0].set_title('Boxplot Suhu (TEMP)')
    sns.boxplot(y=changping_df['O3'], ax=axes[0, 1])
    axes[0, 1].set_title('Boxplot Konsentrasi O3')
    sns.boxplot(y=changping_df['SO2'], ax=axes[1, 0])
    axes[1, 0].set_title('Boxplot SO2')
    sns.boxplot(y=changping_df['NO2'], ax=axes[1, 1])
    axes[1, 1].set_title('Boxplot NO2')
    st.pyplot(fig)

# **Fungsi Imputasi Outlier**
def impute_outliers_with_median(df, column):
    outlier_exists = True
    while outlier_exists:
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
        if outliers.empty:
            outlier_exists = False
        else:
            median_value = df[column].median()
            df[column] = np.where((df[column] < lower_bound) | (df[column] > upper_bound),
                                  median_value, df[column])

# **Imputasi Outlier**
columns_to_fix = ['O3', 'SO2', 'NO2']
for col in columns_to_fix:
    impute_outliers_with_median(changping_df, col)

# **Menghapus Missing Values**
changping_df.dropna(inplace=True)

# **Checkbox untuk Menampilkan Boxplot Setelah Imputasi**
if st.checkbox("Tampilkan Boxplot Setelah Imputasi"):
    st.subheader("Boxplot Setelah Imputasi Outlier")
    fig, axes = plt.subplots(2, 2, figsize=(12, 6))
    sns.boxplot(y=changping_df['TEMP'], ax=axes[0, 0])
    axes[0, 0].set_title('Boxplot Suhu (TEMP)')
    sns.boxplot(y=changping_df['O3'], ax=axes[0, 1])
    axes[0, 1].set_title('Boxplot Konsentrasi O3')
    sns.boxplot(y=changping_df['SO2'], ax=axes[1, 0])
    axes[1, 0].set_title('Boxplot SO2')
    sns.boxplot(y=changping_df['NO2'], ax=axes[1, 1])
    axes[1, 1].set_title('Boxplot NO2')
    st.pyplot(fig)

# **Konversi ke Format Datetime**
changping_df['datetime'] = pd.to_datetime(changping_df[['year', 'month', 'day', 'hour']])

# **Buat Kolom Kuartal**
changping_df['quarter'] = changping_df['datetime'].dt.to_period('Q')

# **Hitung Rata-rata Kuartalan untuk SO2 dan NO2**
pollutants = ['SO2', 'NO2']
quarterly_pollution = changping_df.groupby('quarter')[pollutants].mean()

# **Visualisasi Tren Musiman**
st.subheader("Tren Musiman Konsentrasi SO₂ dan NO₂")
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(quarterly_pollution.index.astype(str), quarterly_pollution['SO2'], marker='o', linestyle='-', color='blue', label='SO2')
ax.plot(quarterly_pollution.index.astype(str), quarterly_pollution['NO2'], marker='s', linestyle='--', color='red', label='NO2')
ax.set_ylabel("Konsentrasi (µg/m³)")
ax.set_xlabel("Kuartal")
ax.set_title("Variasi Konsentrasi SO₂ dan NO₂ per Kuartal di Kota Changping")
ax.legend()
plt.xticks(rotation=45)
st.pyplot(fig)

# **Korelasi antara O3 dan Temp**
korelasi = changping_df[['TEMP', 'O3']].corr()

# **Visualisasi Heatmap Korelasi**
st.subheader("Korelasi antara Suhu (TEMP) dan Konsentrasi O₃")
fig, ax = plt.subplots(figsize=(6, 4))
sns.heatmap(korelasi, annot=True, cmap="coolwarm", ax=ax)
st.pyplot(fig)

# **Kesimpulan**
st.subheader("Kesimpulan")
st.write("""
- **Tren Musiman Konsentrasi SO₂ dan NO₂:** Apabila dilihat grafiknya terdapat pola musiman, yaitu setiap tahunnya pada kuartal ke-3 menjadi titik akhir menurunya data di mana setelah kuartal ke-3 mengalami lonjakan yang signifikan. Hal tersebut mungkin terjadi berdasarkan faktor eksternal(cuaca, manusia, dll).
- **Korelasi antara Suhu (TEMP) dan Konsentrasi O₃:** Terdapat korelasi antara O3 dengan Temp yang ditandakan dengan berdasarkan heatmap yang cukup positif. Artinya, ketika suhu meningkat maka konsentrasi O3 cenderung meningkat juga dan sebaliknya. Jadi, terlihat korelasinya.
""")
