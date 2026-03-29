import streamlit as st
import pandas as pd
import urllib.parse

# --- إعدادات الصفحة ---
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

# رابط الجدول (تأكد أنه Public - Anyone with link can view)
SHEET_URL = "https://docs.google.com/spreadsheets/d/15R1XMLD-8FGG-WIsXM1PZ0JLTceGIJyjNIHgb_uNOZk/export?format=csv"

# دالة لقراءة البيانات وتحويلها لروابط CSV مباشرة (أسرع وأضمن)
def get_data(gid):
    url = f"{SHEET_URL}&gid={gid}"
    return pd.read_csv(url)

# معرفات الصفحات (GIDs) - عادة أول صفحة هي 0
# يمكنك معرفة الـ gid من رابط الصفحة في المتصفح
PRODS_GID = "0" 
DRIVERS_GID = "1972620703" # مثال: ستحده في الرابط عند فتح صفحة الموصلين

st.markdown("""
<style>
    .stApp { background-color: #f4f4f4; }
    .prod-card { background: white; padding: 15px; border-radius: 15px; border: 1px solid #ddd; text-align: center; margin-bottom: 15px; }
    .price { color: #006341; font-weight: bold; font-size: 20px; }
</style>
""", unsafe_allow_html=True)

if 'cart' not in st.session_state: st.session_state.cart = {}

# --- تحميل البيانات ---
try:
    # القراءة من صفحة المنتجات (نستخدم الرابط المباشر للـ CSV لضمان العمل)
    prods_df = pd.read_csv("https://docs.google.com/spreadsheets/d/15R1XMLD-8FGG-WIsXM1PZ0JLTceGIJyjNIHgb_uNOZk/gviz/tq?tqx=out:csv&sheet=products")
    drivers_df = pd.read_csv("https://docs.google.com/spreadsheets/d/15R1XMLD-8FGG-WIsXM1PZ0JLTceGIJyjNIHgb_uNOZk/gviz/tq?tqx=out:csv&sheet=drivers")
except:
    st.error("يرجى التأكد من إضافة بيانات في جدول جوجل (products و drivers)")
    st.stop()

st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)

col_main, col_cart = st.columns([3, 1.8])

with col_main:
    # عرض التصنيفات
    cats = ["الكل"] + prods_df['cat'].unique().tolist()
    sel_cat = st.tabs(cats)
    
    for i, tab in enumerate(sel_cat):
        with tab:
            filtered = prods_df if cats[i] == "الكل" else prods_df[prods_df['cat'] == cats[i]]
            
            for idx, row in filtered.iterrows():
                with st.container():
                    c1, c2, c3 = st.columns([1, 2, 1])
                    # عرض الصورة (إذا كان هناك رابط أو نص)
                    if not pd.isna(row['img']): 
                        c1.image(row['img'], width=80) 
                    c2.write(f"### {row['name']}")
                    c2.write(f"السعر: {row['price']} دج")
                    q = c3.number_input("كغ", 0.5, 20.0, 1.0, 0.5, key=f"in_{idx}")
                    if c3.button("أضف 🛒", key=f"btn_{idx}"):
                        if row['name'] in st.session_state.cart:
                            st.session_state.cart[row['name']]['qty'] += q
                        else:
                            st.session_state.cart[row['name']] = {'price': row['price'], 'qty': q}
                        st.rerun()
                st.divider()

with col_cart:
    st.subheader("🧺 سلة المشتريات")
    total = 0
    items_list = []
    for name, info in list(st.session_state.cart.items()):
        sub = info['price'] * info['qty']
        total += sub
        st.write(f"**{name}** ({info['qty']} كغ) = {int(sub)} دج")
        items_list.append(f"{name} ({info['qty']} كغ)")
        if st.button("حذف", key=f"del_{name}"):
            del st.session_state.cart[name]; st.rerun()
            
    if total > 0:
        st.markdown(f"## المجموع: {int(total)} دج")
        with st.form("checkout"):
            u_name = st.text_input("الاسم")
            u_addr = st.text_input("العنوان")
            sel_d = st.selectbox("اختر الموصل", drivers_df['name'].tolist())
            if st.form_submit_button("إرسال الطلب عبر واتساب"):
                d_phone = drivers_df[drivers_df['name'] == sel_d]['phone'].iloc[0]
                msg = f"طلب جديد من: {u_name}\nالعنوان: {u_addr}\nالمشتريات: {' + '.join(items_list)}\nالمجموع: {int(total)} دج"
                st.markdown(f'<a href="https://wa.me/{d_phone}?text={urllib.parse.quote(msg)}" target="_blank" style="background:#006341;color:white;display:block;text-align:center;padding:12px;border-radius:10px;text-decoration:none;font-weight:bold;">🚀 تأكيد الإرسال للواتساب</a>', unsafe_allow_html=True)
