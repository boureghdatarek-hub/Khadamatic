import streamlit as st
import pandas as pd
import urllib.parse

# --- إعدادات الصفحة ---
st.set_page_config(page_title="SM KHADAMATIC", layout="wide", page_icon="🛒")

# رابط الجدول الأساسي (يجب أن يكون Anyone with the link can VIEW)
SHEET_ID = "15R1XMLD-8FGG-WIsXM1PZ0JLTceGIJyjNIHgb_uNOZk"

def get_google_sheet_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(url)
        # تنظيف البيانات من أي أسطر فارغة
        return df.dropna(how='all')
    except Exception as e:
        st.error(f"خطأ في الاتصال بصفحة {sheet_name}: {e}")
        return pd.DataFrame()

# تحميل البيانات
prods_df = get_google_sheet_data("products")
drivers_df = get_google_sheet_data("drivers")

if 'cart' not in st.session_state:
    st.session_state.cart = {}

# --- التنسيق البصري ---
st.markdown("""
<style>
    .stApp { background-color: #f9f9f9; }
    .product-card { background: white; padding: 15px; border-radius: 15px; border: 1px solid #eee; text-align: center; margin-bottom: 20px; }
    .price-text { color: #006341; font-weight: bold; font-size: 1.2rem; }
    div[data-testid="stExpander"] { border: none !important; box-shadow: none !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)

# التحقق من وجود منتجات
if prods_df.empty or "name" not in prods_df.columns:
    st.warning("⚠️ لم يتم العثور على منتجات. تأكد من أن اسم الورقة في جوجل هو 'products' وأن العناوين في السطر الأول صحيحة (name, price, cat, img)")
    st.stop()

col_main, col_cart = st.columns([3, 1.5])

with col_main:
    # شريط البحث
    search = st.text_input("🔍 ابحث عن منتج...", "")
    
    # التصنيفات
    cats = ["الكل"] + (prods_df['cat'].unique().tolist() if 'cat' in prods_df.columns else [])
    selected_cat = st.radio("التصنيفات:", cats, horizontal=True)
    
    # تصفية البيانات
    filtered_df = prods_df.copy()
    if selected_cat != "الكل":
        filtered_df = filtered_df[filtered_df['cat'] == selected_cat]
    if search:
        filtered_df = filtered_df[filtered_df['name'].str.contains(search, case=False, na=False)]

    # عرض المنتجات
    for idx in range(0, len(filtered_df), 3):
        cols = st.columns(3)
        for j, (_, row) in enumerate(filtered_df.iloc[idx:idx+3].iterrows()):
            with cols[j]:
                st.markdown('<div class="product-card">', unsafe_allow_html=True)
                
                # عرض الصورة
                img_url = row['img'] if not pd.isna(row.get('img')) else ""
                if img_url and str(img_url).startswith("http"):
                    st.image(img_url, use_container_width=True)
                else:
                    st.markdown("<h1 style='font-size:50px;'>📦</h1>", unsafe_allow_html=True)
                
                st.subheader(row['name'])
                st.markdown(f'<p class="price-text">{row["price"]} دج</p>', unsafe_allow_html=True)
                
                q = st.number_input("الكمية", 0.5, 50.0, 1.0, 0.5, key=f"q_{idx}_{j}")
                if st.button("إضافة 🛒", key=f"b_{idx}_{j}"):
                    p_name = row['name']
                    if p_name in st.session_state.cart:
                        st.session_state.cart[p_name]['qty'] += q
                    else:
                        st.session_state.cart[p_name] = {'price': row['price'], 'qty': q}
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

with col_cart:
    st.markdown("### 🧺 سلتك")
    total = 0
    items_summary = []
    
    if not st.session_state.cart:
        st.info("السلة فارغة")
    else:
        for name, info in list(st.session_state.cart.items()):
            sub = info['price'] * info['qty']
            total += sub
            c1, c2 = st.columns([4, 1])
            c1.write(f"**{name}**\n{info['qty']} كغ = {int(sub)} دج")
            if c2.button("❌", key=f"del_{name}"):
                del st.session_state.cart[name]; st.rerun()
            items_summary.append(f"{name} ({info['qty']} كغ)")
        
        st.divider()
        st.markdown(f"## المجموع: {int(total)} دج")
        
        with st.form("checkout"):
            u_name = st.text_input("الاسم")
            u_addr = st.text_input("العنوان")
            
            # اختيار الموصل
            d_names = drivers_df['name'].tolist() if not drivers_df.empty else ["لا يوجد موصلين"]
            sel_d = st.selectbox("الموصل", d_names)
            
            if st.form_submit_button("إرسال الطلب ✅"):
                if u_name and not drivers_df.empty:
                    d_phone = drivers_df[drivers_df['name'] == sel_d]['phone'].iloc[0]
                    msg = f"طلب من: {u_name}\nالعنوان: {u_addr}\nالمشتريات: {' + '.join(items_summary)}\nالمجموع: {int(total)} دج"
                    whatsapp_url = f"https://wa.me/{d_phone}?text={urllib.parse.quote(msg)}"
                    st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="background:#006341;color:white;display:block;text-align:center;padding:12px;border-radius:10px;text-decoration:none;font-weight:bold;">🚀 أرسل الآن عبر واتساب</a>', unsafe_allow_html=True)
                else:
                    st.error("يرجى إكمال البيانات")
