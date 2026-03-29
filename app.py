import streamlit as st
import pandas as pd
import urllib.parse

# --- 1. إعدادات المظهر وإجبار الـ Grid ---
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: white !important; }
    h1, h2, h3, p, b, span, label { color: black !important; }
    
    /* إجبار الأعمدة على البقاء جنباً إلى جنب في الهاتف */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: stretch !important;
        gap: 8px !important;
    }
    [data-testid="column"] {
        flex: 1 !important;
        width: 50% !important;
        min-width: 0px !important; /* منع التمدد */
    }

    .product-card {
        background: white;
        padding: 10px;
        border-radius: 12px;
        border: 1px solid #eee;
        text-align: center;
        margin-bottom: 10px;
        height: 100%;
    }

    /* تنسيق الأزرار (أبيض ناصع) */
    button, [data-testid="stBaseButton-secondary"] {
        background-color: white !important;
        color: #006341 !important;
        border: 2px solid #006341 !important;
        border-radius: 20px !important;
        width: 100% !important;
        font-size: 14px !important;
    }

    /* منع السواد في خانات الإدخال */
    input {
        background-color: #f0f2f6 !important;
        color: black !important;
        -webkit-text-fill-color: black !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. جلب البيانات ---
SHEET_ID = "15R1XMLD-8FGG-WIsXM1PZ0JLTceGIJyjNIHgb_uNOZk"

@st.cache_data(ttl=5)
def load_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try: return pd.read_csv(url).dropna(how='all')
    except: return pd.DataFrame()

prods_df = load_data("products")
drivers_df = load_data("drivers")

# تأمين السلة في الذاكرة
if 'cart' not in st.session_state:
    st.session_state.cart = {}

st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)

# --- 3. عرض المنتجات (Grid 2x2) ---
if not prods_df.empty:
    search = st.text_input("", placeholder="🔍 ابحث هنا...", label_visibility="collapsed")
    
    cat_col = 'cat' if 'cat' in prods_df.columns else prods_df.columns[2]
    cats = ["الكل"] + prods_df[cat_col].unique().tolist()
    tabs = st.tabs(cats)
    
    for i, tab in enumerate(tabs):
        with tab:
            current_cat = cats[i]
            df = prods_df if current_cat == "الكل" else prods_df[prods_df[cat_col] == current_cat]
            if search:
                df = df[df[df.columns[0]].astype(str).str.contains(search, case=False, na=False)]
            
            for idx in range(0, len(df), 2):
                cols = st.columns(2)
                for j in range(2):
                    if (idx + j) < len(df):
                        row = df.iloc[idx + j]
                        p_name = str(row.iloc[0])
                        p_price = row.iloc[1]
                        
                        with cols[j]:
                            st.markdown('<div class="product-card">', unsafe_allow_html=True)
                            
                            # الصورة
                            img_val = row.get('img') if 'img' in df.columns else None
                            if pd.notna(img_val) and str(img_val).startswith("http"):
                                st.image(img_val)
                            else:
                                st.markdown("<h3>📦</h3>", unsafe_allow_html=True)
                            
                            st.markdown(f"<b>{p_name}</b>", unsafe_allow_html=True)
                            st.markdown(f"<p style='color:green; margin:0;'>{p_price} دج</p>", unsafe_allow_html=True)
                            
                            # مفتاح فريد جداً
                            u_id = f"{i}_{idx}_{j}_{p_name}"
                            
                            q = st.number_input("الكمية", 0.5, 50.0, 1.0, 0.5, key=f"q_{u_id}", label_visibility="collapsed")
                            
                            # منطق الإضافة المحسن
                            if st.button("أضف 🛒", key=f"b_{u_id}"):
                                if p_name in st.session_state.cart:
                                    st.session_state.cart[p_name]['qty'] += q
                                else:
                                    st.session_state.cart[p_name] = {'price': p_price, 'qty': q}
                                st.toast(f"✅ تم إضافة {p_name}")
                            st.markdown('</div>', unsafe_allow_html=True)

# --- 4. السلة (بدون تغيير) ---
if st.session_state.cart:
    st.divider()
    st.subheader("🧺 سلتك")
    total = 0
    items_text = []
    
    for name, info in list(st.session_state.cart.items()):
        sub = info['price'] * info['qty']
        total += sub
        c1, c2 = st.columns([4, 1])
        c1.write(f"• {name} ({info['qty']} كغ)")
        if c2.button("🗑️", key=f"del_{name}"):
            del st.session_state.cart[name]
            st.rerun()
        items_text.append(f"{name} ({info['qty']} كغ)")
    
    st.markdown(f"**المجموع: {int(total)} دج**")
    
    with st.expander("🚚 إرسال الطلب"):
        un = st.text_input("اسمك")
        ua = st.text_input("عنوانك")
        if not drivers_df.empty:
            dn = st.selectbox("الموصل", drivers_df.iloc[:, 0].tolist())
            if st.button("تأكيد الواتساب"):
                ph = str(drivers_df[drivers_df.iloc[:, 0] == dn].iloc[0, 1])
                msg = f"طلب من: {un}\nالعنوان: {ua}\nالمشتريات: {' + '.join(items_text)}\nالمجموع: {int(total)} دج"
                st.markdown(f'<a href="https://wa.me/{ph}?text={urllib.parse.quote(msg)}" target="_blank" style="background:#25D366;color:white;display:block;text-align:center;padding:12px;border-radius:10px;text-decoration:none;font-weight:bold;">🚀 أرسل الآن</a>', unsafe_allow_html=True)
