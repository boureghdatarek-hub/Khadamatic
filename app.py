import streamlit as st
import pandas as pd
import urllib.parse

# 1. إعدادات الصفحة
st.set_page_config(page_title="SM KhadamaTic", layout="wide")

# 2. تهيئة الذاكرة (لحل مشكلة الاختفاء)
if 'products' not in st.session_state:
    st.session_state.products = []
if 'drivers' not in st.session_state:
    st.session_state.drivers = []
if 'sellers' not in st.session_state:
    st.session_state.sellers = []
if 'orders' not in st.session_state:
    st.session_state.orders = []
if 'phone' not in st.session_state:
    st.session_state.phone = "213770000000"

# 3. التحقق من وضع الإدارة
is_admin = st.query_params.get("view") == "tarek_king"

if is_admin:
    st.markdown("<h1 style='text-align:center;'>⚙️ لوحة التحكم الملكية</h1>", unsafe_allow_html=True)
    t1, t2, t3, t4, t5 = st.tabs(["📦 المنتجات", "🚚 الموصلين", "👥 البائعين", "📊 السجلات", "🔧 الإعدادات"])

    with t1:
        st.subheader("إضافة منتج")
        with st.form("add_p", clear_on_submit=True):
            name = st.text_input("اسم المنتج")
            price = st.number_input("السعر (دج)", 0)
            if st.form_submit_button("حفظ ✅"):
                if name:
                    st.session_state.products.append({"الاسم": name, "السعر": price})
                    st.success(f"تمت إضافة {name}")
        
        st.divider()
        st.subheader("قائمة المنتجات")
        for i, p in enumerate(st.session_state.products):
            col1, col2 = st.columns([4, 1])
            col1.write(f"🏷️ {p['الاسم']} - {p['السعر']} دج")
            if col2.button("حذف", key=f"del_p_{i}"):
                st.session_state.products.pop(i)
                st.rerun()

    with t2:
        st.subheader("إدارة الموصلين")
        with st.form("add_d", clear_on_submit=True):
            d_name = st.text_input("اسم الموصل")
            d_phone = st.text_input("رقم الهاتف")
            if st.form_submit_button("إضافة 🚚"):
                st.session_state.drivers.append({"الاسم": d_name, "الهاتف": d_phone})
        
        for i, d in enumerate(st.session_state.drivers):
            col1, col2 = st.columns([4, 1])
            col1.write(f"🚚 {d['الاسم']} - {d['الهاتف']}")
            if col2.button("حذف", key=f"del_d_{i}"):
                st.session_state.drivers.pop(i)
                st.rerun()

    with t3:
        st.subheader("إدارة البائعين")
        with st.form("add_s", clear_on_submit=True):
            s_name = st.text_input("اسم البائع")
            if st.form_submit_button("إضافة 👤"):
                st.session_state.sellers.append({"الاسم": s_name})
        
        for i, s in enumerate(st.session_state.sellers):
            col1, col2 = st.columns([4, 1])
            col1.write(f"👤 {s['الاسم']}")
            if col2.button("حذف", key=f"del_s_{i}"):
                st.session_state.sellers.pop(i)
                st.rerun()

    with t4:
        st.subheader("📊 السجلات")
        if st.session_state.products:
            st.write("ملخص المنتجات:")
            st.table(pd.DataFrame(st.session_state.products))
        else: st.info("لا توجد بيانات.")

    with t5:
        st.subheader("🔧 الإعدادات")
        st.session_state.phone = st.text_input("رقم الواتساب الحالي:", value=st.session_state.phone)
        st.success("يتم حفظ الرقم تلقائياً")

else:
    # واجهة الزبائن
    st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KhadamaTic</h1>", unsafe_allow_html=True)
    
    if not st.session_state.products:
        st.warning("عذراً سيدي، المتجر فارغ حالياً. يرجى إضافة منتجات من لوحة الإدارة.")
    else:
        for p in st.session_state.products:
            with st.container():
                st.markdown(f"### {p['الاسم']}")
                st.write(f"السعر: {p['السعر']} دج")
                msg = urllib.parse.quote(f"أريد طلب منتج: {p['الاسم']}")
                st.markdown(f'<a href="https://wa.me/{st.session_state.phone}?text={msg}" target="_blank" style="background-color:green; color:white; padding:10px; border-radius:5px; text-decoration:none;">اطلب الآن عبر واتساب</a>', unsafe_allow_html=True)
                st.divider()
