import streamlit as st
import pandas as pd
import urllib.parse

# 1. إعدادات الصفحة واللغة العربية
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

# تنسيق CSS لجعل الموقع يدعم العربية بالكامل (RTL) وإصلاح الألوان
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        direction: RTL; text-align: right; font-family: 'Cairo', sans-serif;
        background-color: white !important; color: black !important;
    }
    .stApp { background-color: white !important; }
    h1, h2, h3, p, span, label, button { color: black !important; font-family: 'Cairo', sans-serif; }
    
    /* تنسيق الخانات لتظهر بيضاء في الهاتف */
    input, div[data-baseweb="input"], div[data-baseweb="select"] {
        background-color: #f0f2f6 !important; color: black !important; direction: RTL;
    }
    
    /* تنسيق كرت المنتج */
    .product-card {
        background: white; padding: 15px; border-radius: 15px;
        border: 1px solid #eeeeee; text-align: center; margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
    .price-tag { color: #006341; font-weight: bold; font-size: 1.2rem; }
    
    /* تنسيق التبويبات (Categories) */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #f0f2f6; padding: 5px; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { border-radius: 5px !important; }
</style>
""", unsafe_allow_html=True)

# 2. جلب البيانات
SHEET_ID = "15R1XMLD-8FGG-WIsXM1PZ0JLTceGIJyjNIHgb_uNOZk"

@st.cache_data(ttl=5)
def get_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        return pd.read_csv(url).dropna(how='all')
    except: return pd.DataFrame()

prods_df = get_data("products")
drivers_df = get_data("drivers")

# تهيئة السلة
if 'cart' not in st.session_state:
    st.session_state.cart = {}

# --- لوحة التحكم المخفية ---
with st.sidebar:
    st.title("🔐 الإدارة")
    pw = st.text_input("كلمة مرور الإدارة", type="password")
    if pw == "123": # يمكنك تغييرها لاحقاً
        st.success("تم الدخول للوحة التحكم")
        st.write("بيانات المنتجات:")
        st.dataframe(prods_df)
        if st.button("تحديث البيانات 🔄"):
            st.cache_data.clear()
            st.rerun()

# 3. الواجهة الرئيسية
st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)

search = st.text_input("", placeholder="🔍 ابحث عن منتج هنا...", key="search_ar")

if not prods_df.empty:
    categories = ["الكل"] + prods_df['cat'].unique().tolist()
    tabs = st.tabs(categories)
    
    for i, tab in enumerate(tabs):
        with tab:
            current_cat = categories[i]
            filtered = prods_df if current_cat == "الكل" else prods_df[prods_df['cat'] == current_cat]
            if search:
                filtered = filtered[filtered['name'].str.contains(search, case=False, na=False)]
            
            # عرض المنتجات (2 في كل سطر للهاتف)
            for idx in range(0, len(filtered), 2):
                cols = st.columns(2)
                for j, (_, row) in enumerate(filtered.iloc[idx:idx+2].iterrows()):
                    with cols[j]:
                        st.markdown('<div class="product-card">', unsafe_allow_html=True)
                        if not pd.isna(row.get('img')) and str(row['img']).startswith("http"):
                            st.image(row['img'], use_container_width=True)
                        
                        st.write(f"**{row['name']}**")
                        st.markdown(f'<p class="price-tag">{row["price"]} دج</p>', unsafe_allow_html=True)
                        
                        # رقم تعريف فريد لكل منتج لمنع تعليق الإضافة
                        item_id = f"{row['name']}_{current_cat}_{idx}_{j}".replace(" ", "_")
                        
                        q = st.number_input("الكمية", 0.5, 100.0, 1.0, 0.5, key=f"q_{item_id}")
                        
                        if st.button("🛒 أضف للسلة", key=f"btn_{item_id}"):
                            p_name = row['name']
                            if p_name in st.session_state.cart:
                                st.session_state.cart[p_name]['qty'] += q
                            else:
                                st.session_state.cart[p_name] = {'price': row['price'], 'qty': q}
                            st.toast(f"تم إضافة {p_name} بنجاح ✅")
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

# 4. عرض السلة في الأسفل
if st.session_state.cart:
    st.markdown("---")
    st.header("🧺 سلة المشتريات")
    
    total_val = 0
    msg_items = []
    
    for name, info in list(st.session_state.cart.items()):
        sub = info['price'] * info['qty']
        total_val += sub
        c1, c2 = st.columns([4, 1])
        c1.write(f"**{name}** ({info['qty']} كغ) = {int(sub)} دج")
        if c2.button("❌", key=f"del_{name}"):
            del st.session_state.cart[name]
            st.rerun()
        msg_items.append(f"{name} ({info['qty']} كغ)")

    st.subheader(f"المجموع الإجمالي: {int(total_val)} دج")
    
    # نموذج الطلب
    with st.form("order_form"):
        u_name = st.text_input("الاسم الكامل")
        u_addr = st.text_input("عنوان التوصيل (البلدية/الحي)")
        d_options = drivers_df['name'].tolist() if not drivers_df.empty else ["الموصل الافتراضي"]
        selected_d = st.selectbox("اختر الموصل", d_options)
        
        if st.form_submit_button("إرسال الطلب عبر واتساب 🚀"):
            if u_name and u_addr:
                try:
                    d_phone = drivers_df[drivers_df['name']==selected_d]['phone'].iloc[0]
                except: d_phone = "213"
                
                final_msg = (f"طلب جديد من تطبيق SM:\n"
                             f"👤 الاسم: {u_name}\n"
                             f"📍 العنوان: {u_addr}\n"
                             f"🛒 المنتجات: {' + '.join(msg_items)}\n"
                             f"💰 المجموع: {int(total_val)} دج")
                
                wa_url = f"https://wa.me/{d_phone}?text={urllib.parse.quote(final_msg)}"
                st.markdown(f'<a href="{wa_url}" target="_blank" style="background:#25D366;color:white;display:block;text-align:center;padding:15px;border-radius:12px;text-decoration:none;font-weight:bold;font-size:1.2rem;">إضغط هنا لتأكيد الإرسال عبر واتساب</a>', unsafe_allow_html=True)
            else:
                st.error("يرجى ملء الاسم والعنوان")
