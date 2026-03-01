import streamlit as st
import json
import os
import urllib.parse
import pandas as pd
from datetime import datetime

# إعداد الصفحة
st.set_page_config(page_title="KhadamaTic Pro", layout="wide")

# --- كلمة السر الخاصة بك ---
ADMIN_PASSWORD = "tarek_khadamatict" 

# --- إدارة البيانات ---
DB_FILE = "khadamatict_db.json"

def load_data():
    base = {"products": [], "categories": ["عام"], "orders": []}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return base

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if 'db' not in st.session_state: st.session_state.db = load_data()
if 'cart' not in st.session_state: st.session_state.cart = {}

# --- دالة الحماية (القفل الحقيقي) ---
def is_authenticated(area_name):
    auth_key = f"is_authed_{area_name}"
    if auth_key not in st.session_state: st.session_state[auth_key] = False
    return st.session_state[auth_key]

def login_form(area_name):
    st.markdown(f"### 🔒 منطقة محمية ({area_name})")
    pwd = st.text_input("كلمة السر المطلوبة:", type="password", key=f"pwd_{area_name}")
    if st.button("دخول", key=f"btn_{area_name}"):
        if pwd == ADMIN_PASSWORD:
            st.session_state[f"is_authed_{area_name}"] = True
            st.rerun()
        else: st.error("كلمة السر خاطئة!")

# --- واجهة المستخدم ---
st.markdown("<h1 style='text-align:center;'>KhadamaTic | خَدَماتِك 🌿</h1>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["🛒 المتجر", "📊 السجل", "⚙️ الإدارة"])

# --- المتجر (متاح للجميع) ---
with tab1:
    col_p, col_c = st.columns([2, 1])
    with col_p:
        st.subheader("المنتجات المتاحة")
        for i, p in enumerate(st.session_state.db['products']):
            with st.container():
                st.markdown(f"**{p['name']}** - {p['price']} دج")
                # منع خطأ الصورة: لا نعرض الصورة إلا إذا كانت موجودة فعلاً
                if p.get('img') and p['img'].strip() != "":
                    try: st.image(p['img'], width=100)
                    except: pass
                if st.button(f"إضافة للسلة {p['name']}", key=f"add_{i}"):
                    st.session_state.cart[p['name']] = st.session_state.cart.get(p['name'], 0) + 1
                    st.rerun()
    with col_c:
        st.subheader("🛒 سلة الطلبات")
        total = 0
        summary = ""
        for name, qty in st.session_state.cart.items():
            if qty > 0:
                p_data = next(x for x in st.session_state.db['products'] if x['name'] == name)
                item_total = qty * p_data['price']
                total += item_total
                st.write(f"{name} x{qty} = {item_total} دج")
                summary += f"- {name} (x{qty})\n"
        
        st.markdown(f"### الإجمالي: {total} دج")
        c_name = st.text_input("اسمك الكريم:")
        if st.button("إرسال الطلب عبر واتساب") and total > 0 and c_name:
            msg = f"طلب جديد من: {c_name}\n{summary}الإجمالي: {total} دج"
            st.link_button("اضغط هنا للإرسال", f"https://wa.me/213770000000?text={urllib.parse.quote(msg)}")

# --- السجل (مغلق بكلمة سر) ---
with tab2:
    if not is_authenticated("records"):
        login_form("records")
    else:
        st.success("أهلاً بك يا مدير. إليك سجل المبيعات:")
        st.write(pd.DataFrame(st.session_state.db['orders']))
        if st.button("خروج من السجل"):
            st.session_state.is_authed_records = False
            st.rerun()

# --- الإدارة (مغلقة بكلمة سر) ---
with tab3:
    if not is_authenticated("admin"):
        login_form("admin")
    else:
        st.success("أدوات الإدارة متاحة الآن")
        with st.form("new_product"):
            n = st.text_input("اسم المنتج")
            p = st.number_input("السعر", min_value=0)
            if st.form_submit_button("إضافة للمحل"):
                st.session_state.db['products'].append({"name": n, "price": p})
                save_data(st.session_state.db)
                st.rerun()
        
        st.divider()
        st.subheader("حذف منتجات")
        for i, p in enumerate(st.session_state.db['products']):
            if st.button(f"🗑 حذف {p['name']}", key=f"del_{i}"):
                st.session_state.db['products'].pop(i)
                save_data(st.session_state.db)
                st.rerun()
