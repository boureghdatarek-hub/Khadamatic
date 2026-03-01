import streamlit as st
import json, os, pandas as pd

# تهيئة الصفحة
st.set_page_config(page_title="SM KhadamaTic", layout="wide")

# إدارة قاعدة البيانات
DB_FILE = "sm_database.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"products": [], "drivers": [], "sellers": [], "orders": [], "settings": {"phone": "213770000000"}}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

# التحقق من الإدارة
is_admin = st.query_params.get("view") == "tarek_king"

if is_admin:
    st.title("⚙️ لوحة التحكم الملكية")
    t1, t2, t3, t4, t5 = st.tabs(["📦 المنتجات", "🚚 الموصلين", "👥 البائعين", "📊 السجلات", "🔧 الإعدادات"])
    
    # 1. إدارة المنتجات
    with t1:
        st.subheader("إضافة منتج")
        name = st.text_input("اسم المنتج")
        price = st.number_input("السعر", 0)
        if st.button("حفظ المنتج"):
            st.session_state.db['products'].append({"name": name, "price": price})
            save_data(st.session_state.db)
            st.rerun()
        st.subheader("المنتجات الحالية")
        for i, p in enumerate(st.session_state.db['products']):
            c1, c2 = st.columns([4, 1])
            c1.write(f"{p['name']} - {p['price']} دج")
            if c2.button("حذف", key=f"del_p_{i}"):
                st.session_state.db['products'].pop(i)
                save_data(st.session_state.db)
                st.rerun()

    # 2. إدارة الموصلين (بالهاتف)
    with t2:
        st.subheader("إضافة موصل")
        name = st.text_input("اسم الموصل")
        phone = st.text_input("رقم هاتف الموصل")
        if st.button("حفظ الموصل"):
            st.session_state.db['drivers'].append({"name": name, "phone": phone})
            save_data(st.session_state.db)
            st.rerun()
        for i, d in enumerate(st.session_state.db['drivers']):
            c1, c2 = st.columns([4, 1])
            c1.write(f"🚚 {d['name']} - الهاتف: {d.get('phone', 'لا يوجد')}")
            if c2.button("حذف", key=f"del_d_{i}"):
                st.session_state.db['drivers'].pop(i)
                save_data(st.session_state.db)
                st.rerun()

    # 3. إدارة البائعين
    with t3:
        st.subheader("إضافة بائع")
        name = st.text_input("اسم البائع")
        if st.button("حفظ البائع"):
            st.session_state.db['sellers'].append({"name": name})
            save_data(st.session_state.db)
            st.rerun()
        for i, s in enumerate(st.session_state.db['sellers']):
            c1, c2 = st.columns([4, 1])
            c1.write(f"👤 {s['name']}")
            if c2.button("حذف", key=f"del_s_{i}"):
                st.session_state.db['sellers'].pop(i)
                save_data(st.session_state.db)
                st.rerun()

    with t4:
        st.subheader("📊 السجلات")
        if st.session_state.db['orders']:
            st.dataframe(pd.DataFrame(st.session_state.db['orders']))
            
    with t5:
        st.subheader("🔧 الإعدادات")
        phone = st.text_input("رقم واتساب استقبال الطلبات:", value=st.session_state.db['settings']['phone'])
        if st.button("حفظ الإعدادات"):
            st.session_state.db['settings']['phone'] = phone
            save_data(st.session_state.db)
            st.success("تم الحفظ!")
else:
    st.title("SM KhadamaTic")
    st.write("مرحباً بك في المتجر.")
