import streamlit as st
import pandas as pd
import urllib.parse

# 1. Force Light Mode and Mobile Fixes
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: white !important; color: black !important; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    
    /* Input field visibility for mobile */
    input, div[data-baseweb="input"], div[data-baseweb="select"], .stSelectbox {
        background-color: #f0f2f6 !important;
        color: black !important;
        border-radius: 10px !important;
    }
    
    h1, h2, h3, p, span, label { color: black !important; }
    
    .product-card {
        background: #ffffff;
        padding: 10px;
        border-radius: 12px;
        border: 1px solid #eeeeee;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .price-tag { color: #006341; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 2. Data Connection
SHEET_ID = "15R1XMLD-8FGG-WIsXM1PZ0JLTceGIJyjNIHgb_uNOZk"

@st.cache_data(ttl=30)
def get_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        return pd.read_csv(url).dropna(how='all')
    except:
        return pd.DataFrame()

prods_df = get_data("products")
drivers_df = get_data("drivers")

# --- CRITICAL: Initialize Cart State ---
if 'cart' not in st.session_state:
    st.session_state.cart = {}

st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)

# 3. Product Display
if not prods_df.empty:
    search = st.text_input("🔍 البحث", placeholder="ابحث عن منتج...", key="search_bar")
    
    # Filter products
    filtered = prods_df.copy()
    if search:
        filtered = filtered[filtered['name'].str.contains(search, case=False, na=False)]

    # Grid Display (2 per row for mobile)
    for idx in range(0, len(filtered), 2):
        cols = st.columns(2)
        for j, (_, row) in enumerate(filtered.iloc[idx:idx+2].iterrows()):
            with cols[j]:
                st.markdown('<div class="product-card">', unsafe_allow_html=True)
                
                # Image
                img_url = row['img'] if not pd.isna(row.get('img')) else ""
                if img_url and str(img_url).startswith("http"):
                    st.image(img_url, use_container_width=True)
                
                st.write(f"**{row['name']}**")
                st.markdown(f'<p class="price-tag">{row["price"]} دج</p>', unsafe_allow_html=True)
                
                # Quantity & Add Button
                # We use a very specific key to avoid conflicts
                unique_id = f"{row['name']}_{idx}_{j}".replace(" ", "_")
                
                qty = st.number_input("الكمية", 0.5, 100.0, 1.0, 0.5, key=f"qty_{unique_id}")
                
                if st.button("🛒 أضف", key=f"btn_{unique_id}"):
                    # Update dictionary instead of replacing it
                    item_name = row['name']
                    item_price = float(row['price'])
                    
                    if item_name in st.session_state.cart:
                        st.session_state.cart[item_name]['qty'] += qty
                    else:
                        st.session_state.cart[item_name] = {'price': item_price, 'qty': qty}
                    
                    st.success(f"تم إضافة {item_name}")
                    st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)

# 4. Shopping Cart Summary
if st.session_state.cart:
    st.divider()
    st.subheader("🧺 سلتك الحالية")
    
    grand_total = 0
    order_items = []
    
    # Use a list to iterate to allow deletion
    for name, details in list(st.session_state.cart.items()):
        line_total = details['price'] * details['qty']
        grand_total += line_total
        
        c1, c2 = st.columns([4, 1])
        c1.write(f"**{name}**: {details['qty']} وحدة = {int(line_total)} دج")
        
        if c2.button("❌", key=f"del_{name}"):
            del st.session_state.cart[name]
            st.rerun()
            
        order_items.append(f"{name} ({details['qty']})")

    st.markdown(f"### المجموع: {int(grand_total)} دج")
    
    # 5. WhatsApp Checkout Form
    with st.form("checkout_form"):
        u_name = st.text_input("الاسم الكامل")
        u_addr = st.text_input("العنوان بالتفصيل")
        
        d_options = drivers_df['name'].tolist() if not drivers_df.empty else ["توصيل افتراضي"]
        sel_driver = st.selectbox("اختر الموصل", d_options)
        
        if st.form_submit_button("إرسال الطلب عبر واتساب ✅"):
            if u_name and u_addr:
                # Get driver phone
                try:
                    d_phone = drivers_df[drivers_df['name'] == sel_driver]['phone'].iloc[0]
                except:
                    d_phone = "213" # Fallback

                msg = (f"طلب جديد:\n"
                       f"👤 الزبون: {u_name}\n"
                       f"📍 العنوان: {u_addr}\n"
                       f"🛍️ المشتريات: {' + '.join(order_items)}\n"
                       f"💰 المجموع: {int(grand_total)} دج")
                
                whatsapp_link = f"https://wa.me/{d_phone}?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{whatsapp_link}" target="_blank" style="background:#25D366;color:white;display:block;text-align:center;padding:15px;border-radius:10px;text-decoration:none;font-weight:bold;">🚀 اضغط هنا لفتح الواتساب</a>', unsafe_allow_html=True)
            else:
                st.error("يرجى إكمال البيانات")
