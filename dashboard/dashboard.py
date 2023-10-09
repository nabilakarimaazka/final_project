import streamlit as st
import pandas as pd

# Sidebar
st.sidebar.markdown(
    """
    <div class="sidebar-header">
        <h1 style="text-align:center;margin-top:0;">Key Performance Indicator</h1>
    </div>
    """,
    unsafe_allow_html=True
)
# Tampilan header dalam sidebar
st.sidebar.markdown(
    """
    <style>
    .sidebar-header {
        padding: 5px;
        text-align: center;
        color: white;
        border-radius: 0 0 5px 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

all_df = pd.read_csv('https://raw.githubusercontent.com/nabilakarimaazka/final_project/main/dashboard/all.csv')
rfm = pd.read_csv('https://raw.githubusercontent.com/nabilakarimaazka/final_project/main/data/rfm_.csv')

# Hitung KPI dari data Anda
total_revenue = all_df['price'].sum()
total_customers = all_df['customer_id'].nunique()
total_orders = len(all_df)

# Tampilan informasi KPI
st.sidebar.markdown(
    f"""
    <div style="background-color:#f0f0f0;padding:20px;border-radius:5px;text-align:center;">
        <div style="font-size:24px;font-weight:bold;color:#333;">Total Revenue</div>
        <div style="font-size:36px;font-weight:bold;color:#0080FF;">${total_revenue:,.2f}</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown(
    f"""
    <div style="background-color:#f0f0f0;padding:20px;margin-top:20px;border-radius:5px;text-align:center;">
        <div style="font-size:24px;font-weight:bold;color:#333;">Jumlah Customer</div>
        <div style="font-size:36px;font-weight:bold;color:#FF5733;">{total_customers:,}</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown(
    f"""
    <div style="background-color:#f0f0f0;padding:20px;margin-top:20px;border-radius:5px;text-align:center;">
        <div style="font-size:24px;font-weight:bold;color:#333;">Total Order</div>
        <div style="font-size:36px;font-weight:bold;color:#33FF57;">{total_orders:,}</div>
    </div>
    """,
    unsafe_allow_html=True
)

import matplotlib.pyplot as plt
import seaborn as sns
from babel.numbers import format_currency


# jumlah order per bulan
def create_monthly_orders_df(df):
    monthly_orders_df = df.resample(rule='M', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })

    monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    
    return monthly_orders_df

# jumlah customer berdasarkan city
def create_bycity_df(df):
    bycity_df = df.groupby(by="customer_city").order_id.nunique().reset_index()
    bycity_df.rename(columns={
        "order_id" : "order_count"
    }, inplace = True)

    return bycity_df

# jumlah order berdasarkan city
def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").order_id.nunique().reset_index()
    bystate_df.rename(columns={
        "order_id" : "order_count"
    }, inplace = True)

    return bystate_df

# customer_segmen

def create_segment_df(df):
    segment_df = df.groupby(by="customer_segment",  as_index=False).cust_id.nunique().reset_index()
    segment_df['customer_segement'] = pd.Categorical(segment_df['customer_segment'],[
    "Lost Customer", "Low Value Customer", "Medium Value Customer",
    "High Value Customer", "Top Customer"
])

    return segment_df

# waktu pembelian

def waktu_pembelian(df):
    # Hitung jumlah pembelian pada setiap jam
    waktu_df = df.groupby("purchase_time").order_id.nunique().reset_index()
    return waktu_df

# create_sum_order_items_df()

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name").order_id.nunique().sort_values(ascending=False).reset_index()
    return sum_order_items_df

# seller_city_df()

def seller_city_df(df):
    seller_df = df.groupby(by="seller_city").order_id.nunique().reset_index()
    seller_df.rename(columns={
        "order_id": "order_count"
    }, inplace=True)

# create_rfm_df()

def create_rfm_df(df):
    rfm_df = df.groupby(by="cust_id", as_index=False).agg({
        "order_purchase_timestamp": "max", #mengambil tanggal order terakhir
        "order_id": "count",
        "price": "sum"
    })
    
    rfm_df.columns = ["cust_id", "max_order_timestamp", "frequency", "monetary"]

    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df

datetime_columns = ["order_purchase_timestamp"]
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

monthly_orders_df = create_monthly_orders_df(all_df)
bycity_df = create_bycity_df(all_df)
bystate_df = create_bystate_df(all_df)
sum_order_items_df = create_sum_order_items_df(all_df)
waktu_df = waktu_pembelian(all_df)
rfm_df = create_rfm_df(all_df)
segment_df = create_segment_df(rfm)


st.header('E-commerce Analysis Dashboard :sparkles:')
st.subheader('Jumlah Order per Bulan')

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_orders_df["order_purchase_timestamp"],
    monthly_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

st.subheader('Jumlah Pendapatan per Bulan')

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_orders_df["order_purchase_timestamp"],
    monthly_orders_df["revenue"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

st.subheader("Jumlah Order Berdasarkan City dan State")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="order_count", y="customer_city", data=bycity_df.sort_values(by="order_count", ascending=False).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Total Order Berdasarkan City", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
 
sns.barplot(x="order_count", y="customer_state", data=bystate_df.sort_values(by="order_count", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Total Order Berdasarkan State", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

st.subheader("Produk Paling Banyak dan Paling Sedikit Diorder")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="order_id", y="product_category_name", data=sum_order_items_df.sort_values(by="order_id", ascending=False).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
 
sns.barplot(x="order_id", y="product_category_name", data=sum_order_items_df.sort_values(by="order_id", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
 
st.pyplot(fig)

st.subheader('Distribusi Waktu Order Dalam 24 Jam')

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    waktu_df["purchase_time"],
    waktu_df["order_id"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

st.subheader("Customer Terbaik Berdasarkan Parameter RFM Analysis")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 10))
    colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Rata-rata Recency (hari)", value=avg_recency)

    sns.barplot(y="recency", x="cust_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors)
    ax.set_ylabel(None)
    ax.set_xlabel("cust_id", fontsize=30)
    ax.set_title("By Recency (days)", loc="center", fontsize=50)
    ax.tick_params(axis='y', labelsize=30)
    ax.tick_params(axis='x', labelsize=35)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots( figsize=(20, 10))
    colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

    avg_frequency = rfm_df.frequency.mean()
    st.metric("Rata-rata Frequency", value=avg_frequency)

    sns.barplot( 
    y="frequency", 
    x="cust_id", 
    data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors)
    ax.set_ylabel(None)
    ax.set_xlabel("cust_id", fontsize=30)
    ax.set_title("By Frequency", loc="center", fontsize=50)
    ax.tick_params(axis='y', labelsize=30)
    ax.tick_params(axis='x', labelsize=35)
    st.pyplot(fig)

fig, ax = plt.subplots( figsize=(20, 10))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
st.metric("Average Monetary", value=avg_frequency)

sns.barplot(y="monetary", x="cust_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors)
ax.set_ylabel(None)
ax.set_xlabel("cust_id", fontsize=30)
ax.set_title("By Monetary", loc="center", fontsize=50)
ax.tick_params(axis='y', labelsize=30)
ax.tick_params(axis='x', labelsize=35)
st.pyplot(fig)

st.subheader("Segmentasi Customer")

fig, ax = plt.subplots(figsize=(20, 10))
    
colors = ["#D3D3D3", "#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(
    x="cust_id", 
    y="customer_segment",
    data=segment_df.sort_values(by="customer_segment", ascending=False),
    palette=colors
    )
ax.set_title("Number of Customer for Each Segment", loc="center", fontsize=50)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=35)
ax.tick_params(axis='y', labelsize=30)
st.pyplot(fig)
 
st.caption('Copyright (c) Nabila Karima Azka 2023')
