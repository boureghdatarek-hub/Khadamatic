import streamlit as st
import pandas as pd
import urllib.parse

# --- الإعدادات البصرية (أبيض ناصع) ---
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

# تم تعديل CSS لجعل العرض Grid على الهاتف
st.markdown("""
<style>
    .stApp { background-color: white !important; }
    h1, h2, h3, p, b, span, label { color: black !important; }
    
    /* تنسيق كرت المنتج لتناسب عرض الـ Grid */
    .product-card {
        background: white;
        padding: 8px;
        border-radius: 10px;
        border: 1px solid #eee;
        text-align: center;
        margin-bottom: 8px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    /* تصغير حجم الصور قليلاً لتناسب الشبكة */
    .stImage > img { max-height: 100px; object-fit: contain; }
    
    /* تنسيق الأزرار (بدون تغيير) */
    button, [data-testid="stBaseButton-secondary"] {
        background-color: white !important;
        color: #006341 !important;
        border: 2px solid #006341 !important;
        border-radius: 20px !important;
        width: 100% !important;
    }
    
    input, [data-baseweb="input"], [data-baseweb="select"] {
        background-color: #f0f2f6 !important;
        color: black !important;
        -webkit-text-fill-color: black !important;
    }
    
    /* جعل تصنيفات الأقسام مرنة على الهاتف */
    .stTabs [data-baseweb="tab-list"] { gap: 5px; }
    .stTabs [data-baseweb="tab"] { padding: 5px 10px !important; }
</style>
""", unsafe_allow_html=True)

# --- جلب البيانات (بدون تغيير) ---
SHEET_ID = "15R1XMLD-8FGG-WIsXM1PZ0JLTceGIJyjNIHgb_uNOZk"

@st.cache_data(ttl=10)
def load_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(url)
        return df.dropna(how='all')
    except:
        return pd.DataFrame()

prods_df = load_data("products")
drivers_df = load_data("drivers")

if 'cart' not in st.session_state: st.session_state.cart = {}

st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)

if not prods_df.empty:
    search = st.text_input("", placeholder="🔍 ابحث هنا...", label_visibility="collapsed")
    
    # تحديد عمود التصنيف
    cat_col = 'cat' if 'cat' in prods_df.columns else prods_df.columns[2]
    cats = ["الكل"] + prods_df[cat_col].unique().tolist()
    tabs = st.tabs(cats)
    
    for i, tab in enumerate(tabs):
        with tab:
            current_cat = cats[i]
            df = prods_df if current_cat == "الكل" else prods_df[prods_df[cat_col] == current_cat]
            if search:
                # تصفية البحث حسب اسم المنتج (العمود الأول)
                df = df[df[df.columns[0]].str.contains(search, case=False, na=False)]
            
            # --- عرض المنتجات بنظام Grid (2 في السطر) ---
            # نستخدم columns(2) لضمان بقاء الشبكة ثابتة على الهاتف
            for idx in range(0, len(df), 2):
                cols = st.columns(2)
                
                # المنتج الأول في الصف
                with cols[0]:
                    if idx < len(df):
                        row = df.iloc[idx]
                        p_name = row.iloc[0]
                        p_price = row.iloc[1]
                        
                        st.markdown('<div class="product-card">', unsafe_allow_html=True)
                        # عرض الصورة
                        img_val = row.get('img') if 'img' in df.columns else None
                        if pd.notna(img_val) and str(img_val).startswith("http"):
                            st.image(img_val)
                        else:
                            st.markdown("<h2 style='margin:0;'>📦</h2>", unsafe_allow_html=True)
                        
                        st.markdown(f"<b>{p_name}</b>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color:green;'>{p_price} دج</p>", unsafe_allow_html=True)
                        
                        qty = st.number_input("الكمية", 0.5, 50.0, 1.0, 0.5, key=f"q_{idx}_0", label_visibility="collapsed")
                        if st.button("أضف 🛒", key=f"btn_{idx}_0"):
                            st.session_state.cart[p_name] = {'price': p_price, 'qty': qty}
                            st.toast(f"✅ تم إضافة {p_name}")
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # المنتج الثاني في الصف
                with cols[1]:
                    if (idx + 1) < len(df):
                        row = df.iloc[idx + 1]
                        p_name = row.iloc[0]
                        p_price = row.iloc[1]
                        
                        st.markdown('<div class="product-card">', unsafe_allow_html=True)
                        # عرض الصورة
                        img_val = row.get('img') if 'img' in df.columns else None
                        if pd.notna(img_val) and str(img_val).startswith("http"):
                            st.image(img_val)
                        else:
                            st.markdown("<h2 style='margin:0;'>📦</h2>", unsafe_allow_html=True)
                        
                        st.markdown(f"<b>{p_name}</b>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color:green;'>{p_price} دج</p>", unsafe_allow_html=True)
                        
                        qty = st.number_input("الكمية", 0.5, 50.0, 1.0, 0.5, key=f"q_{idx}_1", label_visibility="collapsed")
                        if st.button("أضف 🛒", key=f"btn_{idx}_1"):
                            st.session_state.cart[p_name] = {'price': p_price, 'qty': qty}
                            st.toast(f"✅ تم إضافة {p_name}")
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
            del st.session_state.cart[name]; st.rerun()
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
                    # جلب رقم هاتف الموصل
                    row_d = drivers_df[drivers_df.iloc[:, 0] == sel_d]
                    phone = str(row_d.iloc[0, 1])
                    msg = f"طلب من: {u_name}\nالعنوان: {u_addr}\nالمنتجات: {' + '.join(items_summary)}\nالمجموع: {int(total)} دج"
                    st.markdown(f'<a href="https://wa.me/{phone}?text={urllib.parse.quote(msg)}" target="_blank" style="background:#25D366;color:white;display:block;text-align:center;padding:12px;border-radius:10px;text-decoration:none;font-weight:bold;">تأكيد الإرسال</a>', unsafe_allow_html=True)
                else:
                    st.error("يرجى ملء الاسم والعنوان")
