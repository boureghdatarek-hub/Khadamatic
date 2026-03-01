import streamlit as st
import json, os, urllib.parse, pandas as pd
from datetime import datetime
import base64

# إعدادات الصفحة - متجاوب للكمبيوتر والهاتف
st.set_page_config(page_title="SM KhadamaTic", layout="wide")

# تنسيق METRO المتقدم
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    .main-title { color: #006341; text-align: center; font-size: 30px; font-weight: bold; border-bottom: 3px solid #006341; padding: 5px; }
    .product-card { border: 1px solid #EEE; padding: 10px; border-radius: 12px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 15px; background: white; }
    .stButton>button { background-color: #006341 !important; color: white !important; border-radius: 8px; width: 100%; height: 45px; font-size: 16px; }
    /* تحسين عرض الهاتف */
    @media (max-width: 600px) { .main-title { font-size: 22px; } }
</style>
""", unsafe_allow_html=True)

DB_FILE = "sm_database.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("products"): return data
        except: pass
    # بيانات افتراضية لكي لا يظهر الموقع فارغاً في أول مرة
    return {
        "products": [{"name": "منتج تجريبي", "price": 100, "category": "خضروات", "image": ""}],
        "categories": ["خضروات", "فواكه", "عروض"],
        "drivers": [], "sellers": [], "orders": [],
        "settings": {"phone": "213770000000"}
    }

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if 'db' not in st.session_state: st.session_state.db = load_data()
if 'cart' not in st.session_state: st.session_state.cart = {}

is_admin = st.query_params.get("view") == "tarek_king"

def img_to_base64(img_file):
    return base64.b64encode(img_file.getvalue()).decode()

# --- واجهة المتجر ---
if not is_admin:
    st.markdown("<div class='main-title'>SM KhadamaTic</div>", unsafe_allow_html=True)
    
    # اختيار القسم (يظهر بشكل رائع في الهاتف)
    cat_list = ["الكل"] + st.session_state.db['categories']
    cat = st.selectbox("📂 اختر القسم:", cat_list)
    
    prods = [p for p in st.session_state.db['products'] if cat == "الكل" or p.get('category') == cat]
    
    # توزيع المنتجات (3 في الكمبيوتر، 1 في الهاتف تلقائياً بفضل Streamlit)
    for i in range(0, len(prods), 3):
        cols = st.columns(3)
        for j, p in enumerate(prods[i:i+3]):
            with cols[j]:
                st.markdown("<div class='product-card'>", unsafe_allow_html=True)
                if p.get('image'): 
                    st.image(f"data:image/png;base64,{p['image']}", use_container_width=True)
                else:
                    st.markdown("<div style='height:150px; background:#f9f9f9; border-radius:8px; display:flex; align-items:center; justify-content:center; color:#ccc;'>بدون صورة</div>", unsafe_allow_html=True)
                st.markdown(f"<h4>{p['name']}</h4><h3 style='color:#006341;'>{p['price']} دج</h3></div>", unsafe_allow_html=True)
                if st.button(f"أضف للسلة 🛒", key=f"btn_{i+j}"):
                    st.session_state.cart[p['name']] = st.session_state.cart.get(p['name'], 0) + 1
                    st.toast(f"تمت إضافة {p['name']}")

    # سلة المشتريات (تظهر في الأسفل للهواتف)
    with st.expander("🛒 عرض سلة الطلبات"):
        total = 0
        summary = ""
        for n, q in list(st.session_state.cart.items()):
            if q > 0:
                p_info = next(x for x in st.session_state.db['products'] if x['name'] == n)
                total += q * p_info['price']
                st.write(f"✅ {n} (x{q})")
                summary += f"- {n} (x{q})\n"
        if total > 0:
            st.markdown(f"**الإجمالي: {total} دج**")
            u_n = st.text_input("اسمك الكريم:")
            if st.button("إرسال الطلب عبر واتساب"):
                target = st.session_state.db.get('settings', {}).get('phone', '213770000000')
                msg = urllib.parse.quote(f"طلب جديد:\n{u_n}\n{summary}الإجمالي: {total} دج")
                st.markdown(f'<meta http-equiv="refresh" content="0;url=https://wa.me/{target}?text={msg}">', unsafe_allow_html=True)

# --- لوحة الإدارة ---
else:
    st.markdown("<h2 style='text-align:center;'>⚙️ لوحة التحكم المطلقة</h2>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["📦 المنتجات", "👥 الموظفين", "🔧 الإعدادات"])
    
    with t1:
        with st.form("p_add", clear_on_submit=True):
            n = st.text_input("اسم المنتج")
            p = st.number_input("السعر", 0)
            c = st.selectbox("القسم", st.session_state.db['categories'])
            img = st.file_uploader("صورة المنتج", type=['png','jpg','jpeg'])
            if st.form_submit_button("حفظ وإضافة للمتجر"):
                b64 = img_to_base64(img) if img else ""
                st.session_state.db['products'].append({"name":n,"price":p,"category":c,"image":b64})
                save_data(st.session_state.db); st.rerun()
        
        st.divider()
        for i, prod in enumerate(st.session_state.db['products']):
            c1, c2, c3 = st.columns([1,3,1])
            if prod.get('image'): c1.image(f"data:image/png;base64,{prod['image']}", width=60)
            c2.write(f"**{prod['name']}** - {prod['price']} دج")
            if c3.button("حذف", key=f"del_{i}"):
                st.session_state.db['products'].pop(i); save_data(st.session_state.db); st.rerun()

    with t3:
        curr = st.session_state.db.get('settings', {}).get('phone', '213770000000')
        new_ph = st.text_input("رقم الواتساب الخاص بك (بدون +):", value=curr)
        if st.button("حفظ الرقم"):
            st.session_state.db['settings'] = {"phone": new_ph}
            save_data(st.session_state.db); st.success("تم!")
