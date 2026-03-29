import streamlit as st
import pandas as pd
import urllib.parse

# --- 1. الإعدادات البصرية وإجبار نظام الـ Grid على الهاتف ---
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: white !important; }
    h1, h2, h3, p, b, span, label { color: black !important; }
    
    /* الكود المسؤول عن إجبار الأعمدة على الظهور بجانب بعضها في الهاتف */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 10px !important;
    }
    [data-testid="column"] {
        width: 50% !important;
        flex: 1 1 50% !important;
        min-width: 45% !important;
    }

    .product-card {
        background: white;
        padding: 8px;
        border-radius: 12px;
        border: 1px solid #f0f0f0;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* تنسيق الأزرار (بدون تغيير) */
    button, [data-testid="stBaseButton-secondary"] {
        background-color: white !important;
        color: #006341 !important;
        border: 2px solid #006341 !important;
        border-radius: 20px !important;
        width: 100% !important;
        height: 35px !important;
        padding: 0px !important;
    }
    
    /* تصغير حجم خانة الكمية لتناسب الشبكة */
    .stNumberInput div { height: 35px !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. جلب البيانات ---
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

# --- 3. عرض المنتجات بنظام Grid (2 في السطر) ---
if not prods_df.empty:
    search = st.text_input("", placeholder="🔍 ابحث هنا...", label_visibility="collapsed")
    
    # تحديد الأقسام
    cat_col = 'cat' if 'cat' in prods_df.columns else prods_df.columns[2]
    cats = ["الكل"] + prods_df[cat_col].unique().tolist()
    tabs = st.tabs(cats)
    
    for i, tab in enumerate(tabs):
        with tab:
            current_cat = cats[i]
            df = prods_df if current_cat == "الكل" else prods_df[prods_df[cat_col] == current_cat]
            if search:
                df = df[df[df.columns[0]].astype(str).str.contains(search, case=False, na=False)]
            
            # منطق عرض الشبكة
            for idx in range(0, len(df), 2):
                cols = st.columns(2)
                for j in range(2):
                    if (idx + j) < len(df):
                        row = df.iloc[idx + j]
                        p_name = str(row.iloc[0])
                        p_price = row.iloc[1]
                        
                        with cols[j]:
                            st.markdown('<div class="product-card">', unsafe_allow_html=True)
                            
                            # عرض الصورة
                            img_val = row.get('img') if 'img' in df.columns else None
                            if pd.notna(img_val) and str(img_val).startswith("http"):
                                st.image(img_val, use_container_width=True)
                            else:
                                st.markdown("<h2>📦</h2>", unsafe_allow_html=True)
                            
                            st.markdown(f"<p style='margin:0; font-size:14px;'><b>{p_name}</b></p>", unsafe_allow_html=True)
                            st.markdown(f"<p style='color:green; margin:0;'>{p_price} دج</p>", unsafe_allow_html=True)
                            
                            # مفتاح فريد لمنع خطأ Duplicate Key
                            unique_id = f"grid_{i}_{idx}_{j}"
                            
                            qty = st.number_input("الكمية", 0.5, 50.0, 1.0, 0.5, key=f"q_{unique_id}", label_visibility="collapsed")
                            
                            if st.button("أضف 🛒", key=f"b_{unique_id}"):
                                st.session_state.cart[p_name] = {'price': p_price, 'qty': qty}
                                st.toast(f"✅ تم إضافة {p_name}")
                            st.markdown('</div>', unsafe_allow_html=True)

# --- 4. السلة وإتمام الطلب (بدون تغيير) ---
if st.session_state.cart:
    st.divider()
    st.markdown("### 🧺 السلة")
    total = 0
    items_summary = []
    
    for name, info in list(st.session_state.cart.items()):
        sub = info['price'] * info['qty']
        total += sub
        c1, c2 = st.columns([4, 1])
        c1.write(f"• {name} ({info['qty']} كغ) = {int(sub)} دج")
        if c2.button("🗑️", key=f"del_{name}"):
            del st.session_state.cart[name]; st.rerun()
        items_summary.append(f"{name} ({info['qty']} كغ)")
    
    st.markdown(f"#### المجموع: {int(total)} دج")
    
    with st.expander("🚚 إتمام الطلب"):
        u_name = st.text_input("الاسم")
        u_addr = st.text_input("العنوان")
        if not drivers_df.empty:
            sel_d = st.selectbox("الموصل", drivers_df.iloc[:, 0].tolist())
            if st.button("إرسال الطلب 🚀"):
                if u_name and u_addr:
                    phone = str(drivers_df[drivers_df.iloc[:, 0] == sel_d].iloc[0, 1])
                    msg = f"طلب من: {u_name}\nالعنوان: {u_addr}\nالمنتجات: {' + '.join(items_summary)}\nالمجموع: {int(total)} دج"
                    st.markdown(f'<a href="https://wa.me/{phone}?text={urllib.parse.quote(msg)}" target="_blank" style="background:#25D366;color:white;display:block;text-align:center;padding:12px;border-radius:10px;text-decoration:none;font-weight:bold;">تأكيد عبر واتساب</a>', unsafe_allow_html=True)
