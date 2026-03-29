import streamlit as st
import pandas as pd
import urllib.parse
import uuid

# --- 1. إعدادات صارمة للمظهر لمنع "السواد" في الهاتف ---
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

st.markdown("""
<style>
    /* فرض الخلفية البيضاء */
    .stApp { background-color: white !important; }
    
    /* إجبار الأزرار على اللون الأبيض والنص الأخضر */
    button, [data-testid="stBaseButton-secondary"] {
        background-color: white !important;
        color: #006341 !important;
        border: 2px solid #006341 !important;
        border-radius: 20px !important;
        font-weight: bold !important;
    }

    /* إصلاح خانات الإدخال (الكمية والبحث) لتبقى فاتحة */
    input, [data-baseweb="input"] {
        background-color: #f0f2f6 !important;
        color: black !important;
        -webkit-text-fill-color: black !important;
    }

    /* نصوص سوداء */
    h1, h2, h3, p, b, span, label { color: black !important; }

    /* تنسيق كرت المنتج */
    .product-card {
        background: white;
        padding: 10px;
        border-radius: 12px;
        border: 1px solid #eee;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. جلب البيانات ---
SHEET_ID = "15R1XMLD-8FGG-WIsXM1PZ0JLTceGIJyjNIHgb_uNOZk"

@st.cache_data(ttl=10) # تحديث سريع للبيانات
def load_sheet(name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&sheet={name}"
    try:
        return pd.read_csv(url).dropna(how='all')
    except:
        return pd.DataFrame()

prods_df = load_sheet("products")
drivers_df = load_sheet("drivers")

if 'cart' not in st.session_state: st.session_state.cart = {}

# --- 3. الواجهة الرئيسية ---
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
                df = df[df['name'].str.contains(search, case=False, na=False)]
            
            # عرض المنتجات (2 في السطر للهاتف)
            for idx in range(0, len(df), 2):
                cols = st.columns(2)
                for j, (_, row) in enumerate(df.iloc[idx:idx+2].iterrows()):
                    with cols[j]:
                        st.markdown('<div class="product-card">', unsafe_allow_html=True)
                        if not pd.isna(row.get('img')):
                            st.image(row['img'], use_container_width=True)
                        st.markdown(f"<b>{row['name']}</b>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color:green;'>{row['price']} دج</p>", unsafe_allow_html=True)
                        
                        # --- حل مشكلة التكرار (Unique Keys) ---
                        # نستخدم UUID أو تركيب معقد للمفتاح لضمان عدم التكرار
                        m_key = f"qty_{i}_{idx}_{j}_{row['name']}"
                        qty = st.number_input("الكمية", 0.5, 50.0, 1.0, 0.5, key=m_key, label_visibility="collapsed")
                        
                        if st.button("أضف 🛒", key=f"btn_{i}_{idx}_{j}_{row['name']}"):
                            p_name = row['name']
                            if p_name in st.session_state.cart:
                                st.session_state.cart[p_name]['qty'] += qty
                            else:
                                st.session_state.cart[p_name] = {'price': row['price'], 'qty': qty}
                            st.toast(f"✅ أضفت {p_name}")
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

# --- 4. سلة المشتريات ---
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
        if c2.button("🗑️", key=f"del_{name}_{uuid.uuid4().hex[:4]}"):
            del st.session_state.cart[name]; st.rerun()
        items_summary.append(f"{name} ({info['qty']} كغ)")
    
    st.markdown(f"#### المجموع: {int(total)} دج")
    
    with st.expander("🚚 إتمام الطلب", expanded=True):
        u_name = st.text_input("الاسم")
        u_addr = st.text_input("العنوان")
        d_list = drivers_df['name'].tolist() if not drivers_df.empty else ["موصل 1"]
        sel_d = st.selectbox("الموصل", d_list)
        
        if st.button("إرسال عبر واتساب 🚀"):
            if u_name and u_addr:
                phone = drivers_df[drivers_df['name'] == sel_d]['phone'].iloc[0] if not drivers_df.empty else "213"
                msg = f"طلب من: {u_name}\nالعنوان: {u_addr}\nالمنتجات: {' + '.join(items_summary)}\nالمجموع: {int(total)} دج"
                st.markdown(f'<a href="https://wa.me/{phone}?text={urllib.parse.quote(msg)}" target="_blank" style="background:#25D366;color:white;display:block;text-align:center;padding:12px;border-radius:10px;text-decoration:none;font-weight:bold;">تأكيد الإرسال</a>', unsafe_allow_html=True)
