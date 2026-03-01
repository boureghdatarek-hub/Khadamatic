import streamlit as st
import json, os, urllib.parse, pandas as pd
from datetime import datetime
import base64

# إعدادات الصفحة
st.set_page_config(page_title="SM KhadamaTic", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    .main-title { color: #006341; text-align: center; font-size: 35px; font-weight: bold; border-bottom: 3px solid #006341; padding: 10px; }
    .product-card { border: 1px solid #EEE; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.05); margin-bottom: 10px; }
    div.stButton > button { background-color: #006341 !important; color: white !important; font-weight: bold; width: 100%; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

DB_FILE = "sm_database.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {"products": [], "categories": ["خضروات", "فواكه", "عروض"], "drivers": [], "sellers": [], "orders": [], "settings": {"phone": "213770000000"}}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

if 'db' not in st.session_state: st.session_state.db = load_data()
if 'cart' not in st.session_state: st.session_state.cart = {}

is_admin = st.query_params.get("view") == "tarek_king"

def img_to_base64(img_file):
    return base64.b64encode(img_file.getvalue()).decode()

# --- واجهة المتجر ---
if not is_admin:
    st.markdown("<div class='main-title'>SM KhadamaTic</div>", unsafe_allow_html=True)
    c_m, c_s = st.columns([2.5, 1])
    with c_m:
        cat = st.selectbox("الأقسام:", ["الكل"] + st.session_state.db['categories'])
        prods = [p for p in st.session_state.db['products'] if cat == "الكل" or p.get('category') == cat]
        for i in range(0, len(prods), 3):
            cols = st.columns(3)
            for j, p in enumerate(prods[i:i+3]):
                with cols[j]:
                    st.markdown("<div class='product-card'>", unsafe_allow_html=True)
                    if p.get('image'): st.image(f"data:image/png;base64,{p['image']}", use_container_width=True)
                    st.markdown(f"<h4>{p['name']}</h4><h2 style='color:#006341;'>{p['price']} دج</h2></div>", unsafe_allow_html=True)
                    if st.button(f"أضف للسلة 🛒", key=f"b_{i+j}"):
                        st.session_state.cart[p['name']] = st.session_state.cart.get(p['name'], 0) + 1
                        st.rerun()
    with c_s:
        st.subheader("🛒 السلة")
        total = 0
        msg_items = ""
        for n, q in list(st.session_state.cart.items()):
            if q > 0:
                p_info = next(x for x in st.session_state.db['products'] if x['name'] == n)
                total += q * p_info['price']
                st.write(f"✅ {n} (x{q})")
                msg_items += f"- {n} (x{q})\n"
        if total > 0:
            st.write(f"**الإجمالي: {total} دج**")
            u_name = st.text_input("اسمك:")
            if st.button("طلب عبر واتساب 📲"):
                target = st.session_state.db.get('settings', {}).get('phone', '213770000000')
                msg = urllib.parse.quote(f"طلب من {u_name}\n{msg_items}الإجمالي: {total} دج")
                st.markdown(f'<meta http-equiv="refresh" content="0;url=https://wa.me/{target}?text={msg}">', unsafe_allow_html=True)

# --- لوحة الإدارة ---
else:
    st.markdown("<h2 style='text-align:center;'>⚙️ لوحة الإدارة</h2>", unsafe_allow_html=True)
    if st.button("🔄 تحديث البيانات"): st.rerun()
    t1, t2, t3, t4, t5 = st.tabs(["📦 المنتجات", "🚚 الموصلين", "👥 البائعين", "📊 السجلات", "🔧 الإعدادات"])
    with t1:
        with st.form("add"):
            n = st.text_input("الاسم")
            p = st.number_input("السعر", 0)
            c = st.selectbox("القسم", st.session_state.db['categories'])
            img = st.file_uploader("الصورة", type=['png','jpg','jpeg'])
            if st.form_submit_button("إضافة ✅"):
                b64 = img_to_base64(img) if img else ""
                st.session_state.db['products'].append({"name":n,"price":p,"category":c,"image":b64})
                save_data(st.session_state.db); st.rerun()
        for i, prod in enumerate(st.session_state.db['products']):
            c1, c2 = st.columns([4,1])
            c1.write(f"{prod['name']} - {prod['price']} دج")
            if c2.button("حذف", key=f"d_{i}"):
                st.session_state.db['products'].pop(i); save_data(st.session_state.db); st.rerun()
    with t5:
        curr = st.session_state.db.get('settings', {}).get('phone', '213770000000')
        new = st.text_input("رقم الواتساب الخاص بك:", value=curr)
        if st.button("حفظ"):
            st.session_state.db['settings'] = {"phone": new}
            save_data(st.session_state.db); st.success("تم!")
