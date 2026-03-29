import streamlit as st
import pandas as pd
import urllib.parse

# --- 1. إعدادات المتصفح وفرض تنسيق الهاتف ---
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

st.markdown("""
<style>
    /* منع الوضع الليلي تماماً */
    .stApp { background-color: white !important; }
    h1, h2, h3, p, b, span, label { color: black !important; }

    /* --- إصلاح شريط الأقسام (Categories) للهاتف --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px !important;
        display: flex !important;
        overflow-x: auto !important;
        white-space: nowrap !important;
        padding: 5px !important;
        scrollbar-width: none;
    }
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f3f4 !important;
        border-radius: 20px !important;
        padding: 8px 20px !important;
        border: 1px solid #ddd !important;
    }

    /* --- توحيد حجم الصور في الشبكة --- */
    [data-testid="stImage"] img {
        width: 100% !important;
        height: 140px !important;
        object-fit: contain !important;
        background-color: white !important;
        border-radius: 10px;
    }

    /* كرت المنتج */
    .product-card {
        background: white;
        padding: 10px;
        border-radius: 15px;
        border: 1px solid #eee;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    /* تعديل أزرار الإضافة للهاتف */
    button[kind="secondary"] {
        width: 100% !important;
        border-radius: 10px !important;
        background-color: #006341 !important;
        color: white !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. جلب البيانات ---
SHEET_ID = "15R1XMLD-8FGG-WIsXM1PZ0JLTceGIJyjNIHgb_uNOZk"

@st.cache_data(ttl=10)
def load_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try: return pd.read_csv(url).dropna(how='all')
    except: return pd.DataFrame()

prods_df = load_data("products")
drivers_df = load_data("drivers")

if 'cart' not in st.session_state: st.session_state.cart = {}

st.markdown("<h2 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h2>", unsafe_allow_html=True)

# --- 3. عرض المنتجات ---
if not prods_df.empty:
    search = st.text_input("", placeholder="🔍 ابحث عن منتج هنا...", label_visibility="collapsed")
    
    # تحضير الأقسام
    cat_col = 'cat' if 'cat' in prods_df.columns else prods_df.columns[2]
    cats = ["الكل"] + prods_df[cat_col].unique().tolist()
    
    # تم نزع تبويب الطلبات من هنا
    tabs = st.tabs(cats)
    
    # عرض تبويبات المنتجات
    for i, tab in enumerate(tabs):
        with tab:
            current_cat = cats[i]
            df = prods_df if current_cat == "الكل" else prods_df[prods_df[cat_col] == current_cat]
            if search:
                df = df[df.iloc[:, 0].astype(str).str.contains(search, case=False, na=False)]
            
            # عرض شبكة 2 في كل صف
            for idx in range(0, len(df), 2):
                cols = st.columns(2)
                for j in range(2):
                    if (idx + j) < len(df):
                        row = df.iloc[idx + j]
                        with cols[j]:
                            st.markdown('<div class="product-card">', unsafe_allow_html=True)
                            
                            img_val = row.get('img')
                            if pd.notna(img_val): st.image(img_val)
                            else: st.write("📦")
                            
                            st.markdown(f"<b>{row.iloc[0]}</b><br><span style='color:green;'>{row.iloc[1]} دج</span>", unsafe_allow_html=True)
                            
                            u_key = f"key_{i}_{idx}_{j}"
                            qty = st.number_input("الكمية", 0.5, 100.0, 1.0, 0.5, key=f"q_{u_key}", label_visibility="collapsed")
                            if st.button("أضف 🛒", key=f"b_{u_key}"):
                                name = row.iloc[0]
                                if name in st.session_state.cart: st.session_state.cart[name]['qty'] += qty
                                else: st.session_state.cart[name] = {'price': row.iloc[1], 'qty': qty}
                                st.toast(f"تمت إضافة {name}")
                            st.markdown('</div>', unsafe_allow_html=True)

# --- 4. السلة وإرسال واتساب ---
if st.session_state.cart:
    with st.sidebar:
        st.header("🧺 سلتك")
        total = 0
        summary = []
        for n, info in list(st.session_state.cart.items()):
            sub = info['price'] * info['qty']
            total += sub
            st.write(f"**{n}** ({info['qty']}) = {int(sub)} دج")
            summary.append(f"{n} ({info['qty']} كغ)")
        
        st.divider()
        st.write(f"### المجموع: {int(total)} دج")
        
        u_name = st.text_input("اسمك")
        u_addr = st.text_input("عنوانك")
        if st.button("🚀 إرسال الطلب واتساب"):
            if u_name and u_addr:
                msg = f"طلب جديد من {u_name}\nالعنوان: {u_addr}\nالمنتجات: {', '.join(summary)}\nالمجموع: {int(total)} دج"
                # لا تنسَ وضع رقم الهاتف الصحيح هنا بدلاً من xxxxxxxxx
                st.markdown(f'<a href="https://wa.me/213xxxxxxxxx?text={urllib.parse.quote(msg)}" target="_blank" style="background:green;color:white;padding:10px;text-align:center;display:block;border-radius:5px;text-decoration:none;">تأكيد الإرسال</a>', unsafe_allow_html=True)
