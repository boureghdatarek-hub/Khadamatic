import streamlit as st
import pandas as pd
import urllib.parse

# 1. إعدادات الصفحة وإجبار الألوان الفاتحة (Light Mode)
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

st.markdown("""
<style>
    /* إجبار الخلفية البيضاء في كل مكان */
    .stApp { background-color: white !important; }
    
    /* تنسيق الخانات لتظهر بيضاء في الهاتف */
    input, div[data-baseweb="input"], div[data-baseweb="select"] {
        background-color: #f0f2f6 !important;
        color: black !important;
    }
    
    /* تصحيح لون النصوص في الهاتف */
    h1, h2, h3, p, span, label, .stMarkdown {
        color: black !important;
    }

    /* تنسيق كرت المنتج */
    .product-card {
        background: #ffffff;
        padding: 10px;
        border-radius: 12px;
        border: 1px solid #eeeeee;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .price-tag { color: #006341; font-weight: bold; font-size: 1.1rem; }
</style>
""", unsafe_allow_html=True)

# 2. جلب البيانات
SHEET_ID = "15R1XMLD-8FGG-WIsXM1PZ0JLTceGIJyjNIHgb_uNOZk"

@st.cache_data(ttl=60)
def get_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        return pd.read_csv(url).dropna(how='all')
    except:
        return pd.DataFrame()

prods_df = get_data("products")
drivers_df = get_data("drivers")

# تهيئة السلة
if 'cart' not in st.session_state:
    st.session_state.cart = {}

st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)

# 3. عرض المنتجات بشكل صحيح
if not prods_df.empty:
    search = st.text_input("🔍 ابحث عن منتج...", key="main_search")
    
    cats = ["الكل"] + prods_df['cat'].unique().tolist()
    selected_cat = st.selectbox("اختر القسم", cats, key="cat_selector")
    
    filtered = prods_df if selected_cat == "الكل" else prods_df[prods_df['cat'] == selected_cat]
    if search:
        filtered = filtered[filtered['name'].str.contains(search, case=False, na=False)]

    # عرض المنتجات في شبكة (Grid)
    for idx in range(0, len(filtered), 2):
        cols = st.columns(2)
        for j, (_, row) in enumerate(filtered.iloc[idx:idx+2].iterrows()):
            with cols[j]:
                st.markdown('<div class="product-card">', unsafe_allow_html=True)
                
                # عرض الصورة
                if not pd.isna(row.get('img')) and str(row['img']).startswith("http"):
                    st.image(row['img'], use_container_width=True)
                
                st.write(f"**{row['name']}**")
                st.markdown(f'<p class="price-tag">{row["price"]} دج</p>', unsafe_allow_html=True)
                
                # --- حل مشكلة الإضافة: مفتاح فريد لكل منتج ---
                prod_key = f"{row['name']}_{idx}_{j}"
                q = st.number_input("الكمية", 0.5, 50.0, 1.0, 0.5, key=f"q_{prod_key}")
                
                if st.button("🛒 أضف للسلة", key=f"btn_{prod_key}"):
                    # تحديث السلة في الـ Session State
                    st.session_state.cart[row['name']] = {'price': row['price'], 'qty': q}
                    st.success(f"تم إضافة {row['name']}")
                    st.rerun() # تحديث الصفحة فوراً لإظهار السلة
                
                st.markdown('</div>', unsafe_allow_html=True)

# 4. سلة المشتريات (تظهر في الأسفل)
if st.session_state.cart:
    st.markdown("---")
    st.header("🧺 سلتك الحالية")
    total = 0
    items_list = []
    
    for name, info in list(st.session_state.cart.items()):
        subtotal = info['price'] * info['qty']
        total += subtotal
        c1, c2 = st.columns([4, 1])
        c1.write(f"✅ {name} ({info['qty']} كغ) = {int(subtotal)} دج")
        if c2.button("❌", key=f"del_{name}"):
            del st.session_state.cart[name]
            st.rerun()
        items_list.append(f"{name} ({info['qty']} كغ)")

    st.subheader(f"المجموع النهائي: {int(total)} دج")
    
    # نموذج إرسال الطلب
    with st.form("checkout_form"):
        u_name = st.text_input("الاسم الكامل")
        u_addr = st.text_input("عنوان التوصيل")
        d_names = drivers_df['name'].tolist() if not drivers_df.empty else ["عام"]
        sel_d = st.selectbox("اختر الموصل", d_names)
        
        if st.form_submit_button("إرسال الطلب عبر واتساب"):
            if u_name and u_addr:
                phone = drivers_df[drivers_df['name']==sel_d]['phone'].iloc[0] if not drivers_df.empty else "213"
                msg = f"طلب من: {u_name}\nالعنوان: {u_addr}\nالمنتجات: {' + '.join(items_list)}\nالمجموع: {int(total)} دج"
                whatsapp_url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="background:green;color:white;padding:15px;display:block;text-align:center;border-radius:10px;text-decoration:none;">إضغط هنا لفتح واتساب</a>', unsafe_allow_html=True)
            else:
                st.error("يرجى ملء الاسم والعنوان")
