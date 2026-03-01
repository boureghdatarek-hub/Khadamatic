import streamlit as st
import json, os, pandas as pd

st.set_page_config(page_title="SM KhadamaTic", layout="wide")

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

is_admin = st.query_params.get("view") == "tarek_king"

if is_admin:
    st.title("⚙️ لوحة التحكم الملكية")
    t1, t2, t3, t4, t5 = st.tabs(["📦 المنتجات", "🚚 الموصلين", "👥 البائعين", "📊 السجلات", "🔧 الإعدادات"])
    
    # 1. إدارة المنتجات
    with t1:
        st.subheader("إضافة منتج جديد")
        n = st.text_input("اسم المنتج")
        p = st.number_input("السعر", 0)
        if st.button("حفظ المنتج"):
            st.session_state.db['products'].append({"name": n, "price": p})
            save_data(st.session_state.db)
            st.rerun()
        st.divider()
        for i, item in enumerate(st.session_state.db['products']):
            c1, c2 = st.columns([4, 1])
            c1.write(f"🏷️ {item['name']} - {item['price']} دج")
            if c2.button("حذف", key=f"del_p_{i}"):
                st.session_state.db['products'].pop(i)
                save_data(st.session_state.db)
                st.rerun()

    # 2. إدارة الموصلين
    with t2:
        st.subheader("إضافة موصل")
        dn = st.text_input("اسم الموصل")
        dp = st.text_input("رقم الهاتف")
        if st.button("حفظ الموصل"):
            st.session_state.db['drivers'].append({"name": dn, "phone": dp})
            save_data(st.session_state.db)
            st.rerun()
        st.divider()
        for i, item in enumerate(st.session_state.db['drivers']):
            c1, c2 = st.columns([4, 1])
            c1.write(f"🚚 {item['name']} | الهاتف: {item.get('phone', '')}")
            if c2.button("حذف", key=f"del_d_{i}"):
                st.session_state.db['drivers'].pop(i)
                save_data(st.session_state.db)
                st.rerun()

    # 3. إدارة البائعين
    with t3:
        st.subheader("إضافة بائع")
        sn = st.text_input("اسم البائع")
        if st.button("حفظ البائع"):
            st.session_state.db['sellers'].append({"name": sn})
            save_data(st.session_state.db)
            st.rerun()
        st.divider()
        for i, item in enumerate(st.session_state.db['sellers']):
            c1, c2 = st.columns([4, 1])
            c1.write(f"👤 {item['name']}")
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
        phone = st.text_input("رقم الواتساب:", value=st.session_state.db['settings']['phone'])
        if st.button("حفظ الإعدادات"):
            st.session_state.db['settings']['phone'] = phone
            save_data(st.session_state.db)
            st.success("تم الحفظ!")
else:
    st.title("SM KhadamaTic")
    st.write("مرحباً بك في المتجر، هذا هو المكان الذي سيتم عرض المنتجات فيه للزبائن.")
