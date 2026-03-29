import streamlit as st
import pandas as pd
import urllib.parse

# --- 1. إعدادات الصفحة وتنسيق Grid صارم للهاتف ---
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: white !important; }
    h1, h2, h3, p, b, span, label { color: black !important; }
    
    /* إجبار النظام على عرض منتجين بجانب بعضهما في الهاتف */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 5px !important;
    }
    [data-testid="column"] {
        width: 50% !important;
        flex: 1 1 50% !important;
        min-width: 0px !important;
    }

    /* تحسين كرت المنتج ليكون أصغر وأكثر تناسقاً */
    .product-card {
        background: white;
        padding: 5px;
        border-radius: 10px;
        border: 1px solid #f0f0f0;
        text-align: center;
        margin-bottom: 5px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* ضبط أحجام الخطوط لتناسب المساحة الصغيرة */
    .p-title { font-size: 13px !important; margin-bottom: 2px !important; font-weight: bold; }
    .p-price { font-size: 12px !important; color: green; margin-bottom: 5px !important; }

    /* تنسيق الأزرار لتكون نحيفة وتظهر كاملة */
    button, [data-testid="stBaseButton-secondary"] {
        background-color: white !important;
        color: #006341 !important;
        border: 1.5px solid #006341 !important;
        border-radius: 15px !important;
        width: 100% !important;
        height: 30px !important;
        padding: 0px !important;
        font-size: 12px !important;
        line-height: 1 !important;
    }
    
    /* منع ظهور السواد في خانات الإدخال */
    input { background-color: #f8f9fa !important; color: black !important; }
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

if 'cart' not in st.session_state: st.session_state.cart = {}

st.markdown("<h2 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h2>", unsafe_allow_html=True)

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
            
            # بناء الشبكة
            for idx in range(0, len(df), 2):
                cols = st.columns(2)
                for j in range(2):
                    if (idx + j) < len(df):
                        row = df.iloc[idx + j]
                        p_name = str(row.iloc[0])
                        p_price = row.iloc[1]
                        
                        with cols[j]:
                            st.markdown('<div class="product-card">', unsafe_allow_html=True)
                            
                            # الصورة مصغرة
                            img_val = row.get('img') if 'img' in df.columns else None
                            if pd.notna(img_val) and str(img_val).startswith("http"):
                                st.image(img_val, use_container_width=True)
                            else:
                                st.markdown("<h4>📦</h4>", unsafe_allow_html=True)
                            
                            st.markdown(f'<p class="p-title">{p_name}</p>', unsafe_allow_html=True)
                            st.markdown(f'<p class="p-price">{p_price} دج</p>', unsafe_allow_html=True)
                            
                            # حل مشكلة المفاتيح (Key) لضمان عمل زر الإضافة دائماً
                            u_key = f"grid_{i}_{idx}_{j}_{p_name.replace(' ', '_')}"
                            
                            qty = st.number_input("الكمية", 0.5, 50.0, 1.0, 0.5, key=f"q_{u_key}", label_visibility="collapsed")
                            
                            if st.button("أضف 🛒", key=f"b_{u_key}"):
                                if p_name in st.session_state.cart:
                                    st.session_state.cart[p_name]['qty'] += qty
                                else:
                                    st.session_state.cart[p_name] = {'price': p_price, 'qty': qty}
                                st.toast(f"✅ تم إضافة {p_name}")
                            st.markdown('</div>', unsafe_allow_html=True)

# --- 4. السلة (تظهر فقط عند وجود مشتريات) ---
if st.session_state.cart:
    st.divider()
    st.markdown("### 🧺 طلبيتك")
    total = 0
    items_summary = []
    
    for name, info in list(st.session_state.cart.items()):
        sub = info['price'] * info['qty']
        total += sub
        c1, c2 = st.columns([4, 1])
        c1.write(f"• {name} ({info['qty']} كغ)")
        if c2.button("🗑️", key=f"del_{name}"):
            del st.session_state.cart[name]
            st.rerun()
        items_summary.append(f"{name} ({info['qty']} كغ)")
    
    st.markdown(f"#### المجموع: {int(total)} دج")
    
    with st.expander("🚚 إتمام الطلب"):
        u_name = st.text_input("الاسم الكامل")
        u_addr = st.text_input("العنوان")
        if not drivers_df.empty:
            sel_d = st.selectbox("اختر الموصل", drivers_df.iloc[:, 0].tolist())
            if st.button("إرسال عبر واتساب 🚀"):
                if u_name and u_addr:
                    phone = str(drivers_df[drivers_df.iloc[:, 0] == sel_d].iloc[0, 1])
                    msg = f"طلب من: {u_name}\nالعنوان: {u_addr}\nالمنتجات: {' + '.join(items_summary)}\nالمجموع: {int(total)} دج"
                    st.markdown(f'<a href="https://wa.me/{phone}?text={urllib.parse.quote(msg)}" target="_blank" style="background:#25D366;color:white;display:block;text-align:center;padding:12px;border-radius:10px;text-decoration:none;font-weight:bold;">تأكيد الإرسال</a>', unsafe_allow_html=True)
