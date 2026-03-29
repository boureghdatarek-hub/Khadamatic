import streamlit as st
import pandas as pd
import urllib.parse

# --- الإعدادات البصرية (بدون تغيير) ---
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: white !important; }
    h1, h2, h3, p, b, span, label { color: black !important; }
    button, [data-testid="stBaseButton-secondary"] {
        background-color: white !important;
        color: #006341 !important;
        border: 2px solid #006341 !important;
        border-radius: 20px !important;
    }
    input, [data-baseweb="input"], [data-baseweb="select"] {
        background-color: #f0f2f6 !important;
        color: black !important;
        -webkit-text-fill-color: black !important;
    }
    .product-card {
        background: white;
        padding: 10px;
        border-radius: 12px;
        border: 1px solid #eee;
        text-align: center;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- جلب البيانات ---
SHEET_ID = "15R1XMLD-8FGG-WIsXM1PZ0JLTceGIJyjNIHgb_uNOZk"

@st.cache_data(ttl=5)
def load_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        return pd.read_csv(url).dropna(how='all')
    except:
        return pd.DataFrame()

prods_df = load_data("products")
drivers_df = load_data("drivers")

if 'cart' not in st.session_state: st.session_state.cart = {}

st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)

if not prods_df.empty:
    search = st.text_input("", placeholder="🔍 ابحث هنا...", label_visibility="collapsed")
    cats = ["الكل"] + prods_df['cat'].unique().tolist()
    tabs = st.tabs(cats)
    
    for i, tab in enumerate(tabs):
        with tab:
            current_cat = cats[i]
            df = prods_df if current_cat == "الكل" else prods_df[prods_df['cat'] == current_cat]
            if search:
                df = df[df[df.columns[0]].str.contains(search, case=False, na=False)]
            
            for idx in range(0, len(df), 2):
                cols = st.columns(2)
                for j, (_, row) in enumerate(df.iloc[idx:idx+2].iterrows()):
                    with cols[j]:
                        st.markdown('<div class="product-card">', unsafe_allow_html=True)
                        img_val = row.get('img')
                        if pd.notna(img_val) and str(img_val).startswith("http"):
                            st.image(img_val, use_container_width=True)
                        else:
                            st.markdown("<h2 style='margin:0;'>📦</h2>", unsafe_allow_html=True)
                        
                        p_name = row.iloc[0]
                        p_price = row.iloc[1]
                        st.markdown(f"<b>{p_name}</b>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color:green;'>{p_price} دج</p>", unsafe_allow_html=True)
                        
                        # تم إصلاح المفتاح هنا لضمان عدم الاختفاء
                        m_key = f"qty_{p_name}_{i}_{idx}_{j}"
                        qty = st.number_input("الكمية", 0.5, 50.0, 1.0, 0.5, key=m_key, label_visibility="collapsed")
                        
                        # تم تعديل منطق الزر ليعمل باستمرارية
                        if st.button("أضف 🛒", key=f"btn_{p_name}_{i}_{idx}_{j}"):
                            if p_name in st.session_state.cart:
                                st.session_state.cart[p_name]['qty'] += qty
                            else:
                                st.session_state.cart[p_name] = {'price': p_price, 'qty': qty}
                            st.toast(f"✅ تم إضافة {p_name}")
                            # لا نحتاج لـ rerun هنا في كل مرة لضمان استقرار الواجهة
                st.markdown('</div>', unsafe_allow_html=True)

# --- عرض السلة والموصلين (بدون تغيير) ---
if st.session_state.cart:
    st.divider()
    st.markdown("### 🧺 طلبيتك")
    total = 0
    items_summary = []
    for name, info in list(st.session_state.cart.items()):
        sub = info['price'] * info['qty']
        total += sub
        c1, c2 = st.columns([4, 1])
        c1.write(f"• {name} ({info['qty']} كغ) = {int(sub)} دج")
        if c2.button("🗑️", key=f"del_{name}"):
            del st.session_state.cart[name]
            st.rerun()
        items_summary.append(f"{name} ({info['qty']} كغ)")
    
    st.markdown(f"#### المجموع: {int(total)} دج")
    
    with st.expander("🚚 إتمام الطلب", expanded=True):
        u_name = st.text_input("الاسم الكامل")
        u_addr = st.text_input("العنوان")
        if not drivers_df.empty:
            d_names = drivers_df.iloc[:, 0].tolist()
            sel_d = st.selectbox("اختر الموصل", d_names)
            if st.button("إرسال عبر واتساب 🚀"):
                if u_name and u_addr:
                    row_d = drivers_df[drivers_df.iloc[:, 0] == sel_d]
                    phone = str(row_d.iloc[0, 1])
                    msg = f"طلب من: {u_name}\nالعنوان: {u_addr}\nالمنتجات: {' + '.join(items_summary)}\nالمجموع: {int(total)} دج"
                    st.markdown(f'<a href="https://wa.me/{phone}?text={urllib.parse.quote(msg)}" target="_blank" style="background:#25D366;color:white;display:block;text-align:center;padding:12px;border-radius:10px;text-decoration:none;font-weight:bold;">تأكيد الإرسال</a>', unsafe_allow_html=True)
