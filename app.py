import streamlit as st
import json, os, urllib.parse, pandas as pd
import base64

# 1. إعدادات الصفحة
st.set_page_config(page_title="SM KhadamaTic", layout="wide")

# تنسيق METRO
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    .main-title { color: #006341; text-align: center; font-size: 30px; font-weight: bold; border-bottom: 3px solid #006341; padding: 10px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# 2. إدارة قاعدة البيانات
DB_FILE = "sm_database.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                for k in ["products", "categories", "drivers", "sellers", "orders", "settings"]:
                    if k not in d: d[k] = [] if k != "settings" else {"phone": "213770000000"}
                return d
        except: pass
    return {"products": [], "categories": ["خضروات", "فواكه"], "drivers": [], "sellers": [], "orders": [], "settings": {"phone": "213770000000"}}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if 'db' not in st.session_state: st.session_state.db = load_data()

# 3. التحقق من وضع الإدارة
is_admin = st.query_params.get("view") == "tarek_king"

if is_admin:
    st.markdown("<h1 style='text-align:center;'>⚙️ لوحة التحكم الملكية</h1>", unsafe_allow_html=True)
    # التبويبات الخمسة المطلوبة
    t1, t2, t3, t4, t5 = st.tabs(["📦 المنتجات", "🚚 الموصلين", "👥 البائعين", "📊 السجلات", "🔧 الإعدادات"])
    
    with t1:
        st.subheader("إدارة المنتجات")
        with st.form("p_add", clear_on_submit=True):
            n = st.text_input("اسم المنتج")
            p = st.number_input("السعر", 0)
            if st.form_submit_button("حفظ المنتج ✅"):
                if n:
                    st.session_state.db['products'].append({"name":n,"price":p})
                    save_data(st.session_state.db); st.rerun()
    
    with t2:
        st.subheader("إدارة الموصلين")
        with st.form("d_add", clear_on_submit=True):
            dn = st.text_input("اسم الموصل")
            if st.form_submit_button("إضافة موصل"):
                st.session_state.db['drivers'].append({"name": dn})
                save_data(st.session_state.db); st.rerun()

    with t3:
        st.subheader("إدارة البائعين")
        with st.form("s_add", clear_on_submit=True):
            sn = st.text_input("اسم البائع")
            if st.form_submit_button("إضافة بائع"):
                st.session_state.db['sellers'].append({"name": sn})
                save_data(st.session_state.db); st.rerun()

    with t4:
        st.subheader("📊 سجلات المبيعات")
        if st.session_state.db['orders']:
            st.dataframe(pd.DataFrame(st.session_state.db['orders']))
        else: st.info("لا توجد مبيعات حالياً.")

    with t5:
        st.subheader("🔧 الإعدادات العامة")
        curr_ph = st.session_state.db['settings'].get('phone', '213770000000')
        new_ph = st.text_input("رقم استقبال الطلبات:", value=curr_ph)
        if st.button("حفظ الإعدادات 💾"):
            st.session_state.db['settings']['phone'] = new_ph
            save_data(st.session_state.db); st.success("تم الحفظ!")

else:
    st.markdown("<div class='main-title'>SM KhadamaTic</div>", unsafe_allow_html=True)
    st.info("مرحباً بك يا سيدي. يرجى إضافة المنتجات من لوحة الإدارة ليراها الزبائن.")
