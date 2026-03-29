import streamlit as st
import pandas as pd
import urllib.parse

# --- إعدادات الصفحة وتحسين العرض على الهاتف ---
st.set_page_config(page_title="SM KHADAMATIC", layout="wide", initial_sidebar_state="collapsed")

# CSS مخصص لإصلاح الخطوط والتنسيق على الهاتف
st.markdown("""
<style>
    /* تصغير العناوين في الهاتف */
    @media (max-width: 640px) {
        h1 { font-size: 1.8rem !important; }
        .stMarkdown p { font-size: 0.9rem !important; }
        .product-card h3 { font-size: 1rem !important; }
        .price-text { font-size: 1rem !important; }
        div[data-testid="column"] { width: 50% !important; flex: 1 1 45% !important; min-width: 45% !important; }
    }
    
    .stApp { background-color: #f9f9f9; }
    .product-card { 
        background: white; 
        padding: 10px; 
        border-radius: 12px; 
        border: 1px solid #eee; 
        text-align: center; 
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .price-text { color: #006341; font-weight: bold; }
    .stButton > button { width: 100%; border-radius: 20px; }
</style>
""", unsafe_allow_html=True)

SHEET_ID = "15R1XMLD-8FGG-WIsXM1PZ0JLTceGIJyjNIHgb_uNOZk"

def get_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        return pd.read_csv(url).dropna(how='all')
    except:
        return pd.DataFrame()

# تحميل البيانات
prods_df = get_data("products")
drivers_df = get_data("drivers")

if 'cart' not in st.session_state: st.session_state.cart = {}

st.markdown("<h1 style='text-align:center; color:#006341; margin-bottom:0;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)

# شريط البحث وتصنيفات مبسطة للهاتف
search = st.text_input("🔍 ابحث هنا...", "")
cats = ["الكل"] + (prods_df['cat'].unique().tolist() if not prods_df.empty else [])
selected_cat = st.tabs(cats)

for i, tab in enumerate(selected_cat):
    with tab:
        current_cat = cats[i]
        filtered = prods_df if current_cat == "الكل" else prods_df[prods_df['cat'] == current_cat]
        if search:
            filtered = filtered[filtered['name'].str.contains(search, case=False, na=False)]
        
        # عرض المنتجات: في الهاتف ستظهر كـ 2 في كل سطر
        for idx in range(0, len(filtered), 2):
            cols = st.columns(2)
            for j, (_, row) in enumerate(filtered.iloc[idx:idx+2].iterrows()):
                with cols[j]:
                    st.markdown('<div class="product-card">', unsafe_allow_html=True)
                    img_url = row['img'] if not pd.isna(row.get('img')) else ""
                    if img_url and str(img_url).startswith("http"):
                        st.image(img_url, use_container_width=True)
                    else:
                        st.markdown("<h2 style='margin:0;'>📦</h2>", unsafe_allow_html=True)
                    
                    st.markdown(f"**{row['name']}**")
                    st.markdown(f'<p class="price-text">{row["price"]} دج</p>', unsafe_allow_html=True)
                    
                    q = st.number_input("كغ", 0.5, 20.0, 1.0, 0.5, key=f"q_{idx}_{j}")
                    if st.button("🛒 أضف", key=f"b_{idx}_{j}"):
                        st.session_state.cart[row['name']] = {'price': row['price'], 'qty': q}
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# سلة المشتريات تظهر في الأسفل بشكل عائم أو قسم منفصل
st.divider()
with st.expander(f"🧺 سلتك ({len(st.session_state.cart)} منتجات)", expanded=True):
    total = 0
    items_text = []
    for name, info in list(st.session_state.cart.items()):
        sub = info['price'] * info['qty']
        total += sub
        st.write(f"{name} | {info['qty']} كغ | {int(sub)} دج")
        items_text.append(f"{name} ({info['qty']} كغ)")
        if st.button(f"حذف {name}", key=f"del_{name}"):
            del st.session_state.cart[name]; st.rerun()
    
    if total > 0:
        st.markdown(f"### المجموع النهائي: {int(total)} دج")
        with st.form("order_form"):
            u_name = st.text_input("اسمك")
            u_addr = st.text_input("عنوانك")
            d_names = drivers_df['name'].tolist() if not drivers_df.empty else []
            sel_d = st.selectbox("الموصل", d_names)
            
            if st.form_submit_button("إرسال الطلب عبر واتساب ✅"):
                if u_name and u_addr and sel_d:
                    d_phone = drivers_df[drivers_df['name'] == sel_d]['phone'].iloc[0]
                    msg = f"طلب جديد:\nالزبون: {u_name}\nالعنوان: {u_addr}\nالمشتريات: {' + '.join(items_text)}\nالمجموع: {int(total)} دج"
                    st.markdown(f'<a href="https://wa.me/{d_phone}?text={urllib.parse.quote(msg)}" target="_blank" style="background:#25D366;color:white;display:block;text-align:center;padding:15px;border-radius:10px;text-decoration:none;font-weight:bold;">إرسال الآن للواتساب</a>', unsafe_allow_html=True)
