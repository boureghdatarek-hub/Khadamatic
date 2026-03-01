import streamlit as st
import json, os, urllib.parse, pandas as pd
from datetime import datetime
import base64

# 1. إعدادات الصفحة والواجهة المتجاوبة (للكمبيوتر والهاتف)
st.set_page_config(page_title="SM KhadamaTic", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    .main-title { color: #006341; text-align: center; font-size: 35px; font-weight: bold; border-bottom: 3px solid #006341; padding: 10px; }
    .product-card { border: 1px solid #EEE; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.05); margin-bottom: 10px; }
    .product-img { width: 100%; height: 180px; object-fit: cover; border-radius: 10px; }
    div.stButton > button { background-color: #006341 !important; color: white !important; font-weight: bold; width: 100%; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# 2. إدارة قاعدة البيانات (JSON)
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

# الدخول للوحة الإدارة عبر الرابط
is_admin = st.query_params.get("view") == "tarek_king"

# دالة الصور
def img_to_base64(img_file):
    return base64.b64encode(img_file.getvalue()).decode()

# --- [1] واجهة المتجر ---
if not is_admin:
    st.markdown("<div class='main-title'>SM KhadamaTic</div>", unsafe_allow_html=True)
    c_m, c_s = st.columns([2.5, 1])
    
    with c_m:
        cat = st.selectbox("تصفح الأقسام:", ["الكل"] + st.session_state.db['categories'])
        prods = [p for p in st.session_state.db['products'] if cat == "الكل" or p.get('category') == cat]
        
        for i in range(0, len(prods), 3):
            cols = st.columns(3)
            for j, p in enumerate(prods[i:i+3]):
                with cols[j]:
                    img_src = f"data:image/png;base64,{p['image']}" if p.get('image') else ""
                    st.markdown(f"<div class='product-card'>", unsafe_allow_html=True)
                    if img_src: st.image(img_src, use_container_width=True)
                    st.markdown(f"<h4>{p['name']}</h4><h2 style='color:#006341;'>{p['price']} دج</h2></div>", unsafe_allow_html=True)
                    if st.button(f"أضف للسلة 🛒", key=f"btn_{p['name']}_{i+j}"):
                        st.session_state.cart[p['name']] = st.session_state.cart.get(p['name'], 0) + 1
                        st.rerun()

    with c_s:
        st.subheader("🛒 السلة")
        total = 0
        summary = ""
        for n, q in list(st.session_state.cart.items()):
            if q > 0:
                p_info = next(x for x in st.session_state.db['products'] if x['name'] == n)
                total += q * p_info['price']
                st.write(f"✅ {n} (x{q})")
                summary += f"- {n} (x{q})\n"
        if total > 0:
            st.markdown(f"### الإجمالي: {total} دج")
            u_n = st.text_input("الاسم:")
            if st.button("تأكيد الطلب عبر واتساب 📲"):
                target = st.session_state.db.get('settings', {}).get('phone', '213770000000')
                msg = urllib.parse.quote(f"طلب جديد من {u_n}\n{summary}الإجمالي: {total} دج")
                st.markdown(f'<meta http-equiv="refresh" content="0;url=https://wa.me/{target}?text={msg}">', unsafe_allow_html=True)

# --- [2] لوحة الإدارة ---
else:
    st.markdown("<h1 style='text-align:center;'>⚙️ لوحة الإدارة</h1>", unsafe_allow_html=True)
    t1, t2, t3, t4, t5 = st.tabs(["📦 المنتجات", "🚚 الموصلين", "👥 البائعين", "📊 السجلات", "🔧 الإعدادات"])

    with t1:
        with st.form("add_p", clear_on_submit=True):
            n = st.text_input("اسم المنتج")
            p = st.number_input("السعر", 0)
            c = st.selectbox("القسم", st.session_state.db['categories'])
            img = st.file_uploader("الصورة", type=['png','jpg','jpeg'])
            if st.form_submit_button("إضافة ✅"):
                if n:
                    b64 = img_to_base64(img) if img else ""
                    st.session_state.db['products'].append({"name":n,"price":p,"category":c,"image":b64})
                    save_data(st.session_state.db); st.rerun()
        for i, prod in enumerate(st.session_state.db['products']):
            c1, c2, c3 = st.columns([1,3,1])
            if prod.get('image'): c1.image(f"data:image/png;base64,{prod['image']}", width=60)
            c2.write(f"**{prod['name']}** - {prod['price']} دج")
            if c3.button("حذف", key=f"del_{i}"):
                st.session_state.db['products'].pop(i); save_data(st.session_state.db); st.rerun()

    with t2:
        with st.form("add_d", clear_on_submit=True):
            dn = st.text_input("الموصل")
            dp = st.text_input("الهاتف")
            if st.form_submit_button("إضافة موصل"):
                st.session_state.db['drivers'].append({"name":dn, "phone":dp})
                save_data(st.session_state.db); st.rerun()
        st.write(pd.DataFrame(st.session_state.db['drivers']))

    with t3:
        with st.form("add_s", clear_on_submit=True):
            sn = st.text_input("البائع")
            if st.form_submit_button("إضافة بائع"):
                st.session_state.db['sellers'].append({"name":sn})
                save_data(st.session_state.db); st.rerun()
        st.write(pd.DataFrame(st.session_state.db['sellers']))

    with t4:
        if st.session_state.db['orders']:
            df = pd.DataFrame(st.session_state.db['orders'])
            st.dataframe(df)
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 تحميل التقرير (CSV/Excel)", csv, "Report.csv")

    with t5:
        curr_ph = st.session_state.db.get('settings', {}).get('phone', '213770000000')
        new_ph = st.text_input("رقمك لاستلام الطلبات:", value=curr_ph)
        if st.button("حفظ الإعدادات"):
            st.session_state.db['settings'] = {"phone": new_ph}
            save_data(st.session_state.db); st.success("تم الحفظ!")
