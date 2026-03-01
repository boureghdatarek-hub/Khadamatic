import streamlit as st
import json, os, urllib.parse, pandas as pd
import base64
st.set_page_config(page_title="SM KhadamaTic", layout="wide")
st.markdown("<style>.stApp { background-color: #FFFFFF; }</style>", unsafe_allow_html=True)
DB_FILE = "sm_database.json"
def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {"products": [], "categories": ["خضروات", "فواكه"], "drivers": [], "sellers": [], "orders": [], "settings": {"phone": "213770000000"}}
def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)
if 'db' not in st.session_state: st.session_state.db = load_data()
    is_admin = st.query_params.get("view") == "tarek_king"
if is_admin:
    t1, t2, t3, t4, t5 = st.tabs(["📦 المنتجات", "🚚 الموصلين", "👥 البائعين", "📊 السجلات", "🔧 الإعدادات"])
    with t1:
        st.subheader("إضافة منتج")
        with st.form("p_add", clear_on_submit=True):
            n = st.text_input("اسم المنتج")
            p = st.number_input("السعر", 0)
            if st.form_submit_button("حفظ"):
                st.session_state.db['products'].append({"name":n,"price":p})
                save_data(st.session_state.db); st.rerun()
    with t2:
        st.subheader("إضافة موصل")
        with st.form("d_add", clear_on_submit=True):
            dn = st.text_input("اسم الموصل")
            if st.form_submit_button("إضافة"):
                st.session_state.db['drivers'].append({"name": dn})
                save_data(st.session_state.db); st.rerun()
    with t3:
        st.subheader("إضافة بائع")
        with st.form("s_add", clear_on_submit=True):
            sn = st.text_input("اسم البائع")
            if st.form_submit_button("إضافة"):
                st.session_state.db['sellers'].append({"name": sn})
                save_data(st.session_state.db); st.rerun()
                with t4:
        st.subheader("السجلات")
        if st.session_state.db['orders']: st.dataframe(pd.DataFrame(st.session_state.db['orders']))
    with t5:
        st.subheader("الإعدادات")
        new_ph = st.text_input("رقم الواتساب:", value=st.session_state.db['settings']['phone'])
        if st.button("حفظ"):
            st.session_state.db['settings']['phone'] = new_ph
            save_data(st.session_state.db); st.success("تم الحفظ")
else:
    st.title("مرحباً بك في متجرنا")
    st.write("يرجى الدخول عبر رابط الإدارة لعرض لوحة التحكم.")
