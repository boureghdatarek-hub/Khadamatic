import streamlit as st
import pandas as pd
import urllib.parse

# --- 1. إعدادات صارمة للمظهر والأداء ---
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

st.markdown("""
<style>
    /* فرض الخلفية البيضاء على كامل التطبيق */
    .stApp { background-color: #FFFFFF !important; }
    
    /* إجبار الأزرار على مظهر فاتح ونصوص واضحة */
    button, .stButton>button {
        background-color: #FFFFFF !important;
        color: #006341 !important;
        border: 2px solid #006341 !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        height: 35px !important;
    }
    
    /* تغيير مظهر الزر عند الضغط */
    button:active, button:focus {
        background-color: #006341 !important;
        color: #FFFFFF !important;
    }

    /* تنظيف خانات الإدخال من أي سواد ناتج عن الهاتف */
    input, [data-baseweb="input"], [data-baseweb="select"] {
        background-color: #F0F2F6 !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }

    /* تنسيق كرت المنتج */
    .product-card {
        background: white;
        padding: 10px;
        border-radius: 12px;
        border: 1px solid #EEEEEE;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* نصوص سوداء واضحة */
    h1, h2, h3, p, b, span { color: #000000 !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. ربط البيانات ---
SHEET_ID = "15R1XMLD-8FGG-WIsXM1PZ0JLTceGIJyjNIHgb_uNOZk"

@st.cache_data(ttl=20)
def load_data(sheet):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&sheet={sheet}"
    try: return pd.read_csv(url).dropna(how='all')
    except: return pd.DataFrame()

prods = load_data("products")
drivers = load_data("drivers")

if 'cart' not in st.session_state: st.session_state.cart = {}

# --- 3. الواجهة الرئيسية ---
st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)

if not prods.empty:
    # شريط البحث
    search = st.text_input("", placeholder="🔍 ابحث عن منتج...", label_visibility="collapsed")
    
    # تبويبات الأقسام
    cats = ["الكل"] + prods['cat'].unique().tolist()
    tabs = st.tabs(cats)
    
    for i, tab in enumerate(tabs):
        with tab:
            current_cat = cats[i]
            df = prods if current_cat == "الكل" else prods[prods['cat'] == current_cat]
            if search:
                df = df[df['name'].str.contains(search, case=False, na=False)]
            
            # عرض المنتجات
            for idx in range(0, len(df), 2):
                cols = st.columns(2)
                for j, (_, row) in enumerate(df.iloc[idx:idx+2].iterrows()):
                    with cols[j]:
                        st.markdown('<div class="product-card">', unsafe_allow_html=True)
                        if not pd.isna(row.get('img')):
                            st.image(row['img'], use_container_width=True)
                        st.markdown(f"<b>{row['name']}</b>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color:green; margin:0;'>{row['price']} دج</p>", unsafe_allow_html=True)
                        
                        # --- الحل الذكي لمشكلة الإضافة (تغيير المفاتيح ديناميكياً) ---
                        # نستخدم اسم المنتج + التصنيف لضمان مفتاح فريد لكل خانة
                        item_key = f"q_{row['name']}_{i}_{idx}_{j}"
                        qty = st.number_input("الكمية", 0.5, 50.0, 1.0, 0.5, key=item_key, label_visibility="collapsed")
                        
                        if st.button("إضافة 🛒", key=f"btn_{item_key}"):
                            p_name = row['name']
                            if p_name in st.session_state.cart:
                                st.session_state.cart[p_name]['qty'] += qty
                            else:
                                st.session_state.cart[p_name] = {'price': row['price'], 'qty': qty}
                            st.success(f"تم إضافة {p_name}")
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

# --- 4. سلة المشتريات ---
if st.session_state.cart:
    st.divider()
    st.subheader("🧺 سلة الطلب")
    total = 0
    items_list = []
    
    for name, info in list(st.session_state.cart.items()):
        sub = info['price'] * info['qty']
        total += sub
        c1, c2 = st.columns([4, 1])
        c1.write(f"• {name} ({info['qty']} كغ) = {int(sub)} دج")
        if c2.button("🗑️", key=f"del_{name}"):
            del st.session_state.cart[name]; st.rerun()
        items_list.append(f"{name} ({info['qty']} كغ)")
    
    st.markdown(f"### المجموع: {int(total)} دج")
    
    with st.form("checkout"):
        u_name = st.text_input("الاسم الكامل")
        u_addr = st.text_input("العنوان")
        d_list = drivers['name'].tolist() if not drivers.empty else ["توصيل"]
        sel_d = st.selectbox("الموصل", d_list)
        
        if st.form_submit_button("إرسال الطلب واتساب ✅"):
            if u_name and u_addr:
                phone = drivers[drivers['name'] == sel_d]['phone'].iloc[0] if not drivers.empty else "213..."
                msg = f"طلب من: {u_name}\nالعنوان: {u_addr}\nالمنتجات: {' + '.join(items_list)}\nالمجموع: {int(total)} دج"
                st.markdown(f'<a href="https://wa.me/{phone}?text={urllib.parse.quote(msg)}" target="_blank" style="background:#25D366;color:white;display:block;text-align:center;padding:12px;border-radius:10px;text-decoration:none;font-weight:bold;">🚀 اضغط هنا للإرسال</a>', unsafe_allow_html=True)
