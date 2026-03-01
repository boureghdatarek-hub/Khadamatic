import streamlit as st
import json
import os
import urllib.parse
import pandas as pd
from datetime import datetime
from io import BytesIO

# 1. إعدادات الصفحة
st.set_page_config(page_title="SM KhadamaTic", layout="wide")

# 2. التنسيق الاحترافي (مريح للعين ومتوافق مع الهاتف)
st.markdown("""
<style>
    .stApp { background-color: #F8F9FA; color: #333; }
    .main-title { color: #006341; text-align: center; font-size: clamp(24px, 5vw, 40px); font-weight: bold; margin: 20px 0; }
    .product-card {
        background-color: white; padding: 15px; border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center;
        border: 1px solid #EEE; margin-bottom: 15px;
    }
    div.stButton > button { 
        background-color: #006341 !important; color: white !important; 
        border-radius: 8px; width: 100%; font-weight: bold; height: 45px;
    }
    /* إخفاء القائمة الجانبية تماماً عن الناس */
    [data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# 3. إدارة البيانات
DB_FILE = "khadamatict_db.json"
ADMIN_KEY = "tarek_king" # الكلمة السرية للرابط

def load_data():
    base = {"products": [], "categories": ["خضروات", "فواكه", "عروض"], 
            "delivery_fees": {"باتنة": 200, "الجزائر": 500}, "orders": []}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return base

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if 'db' not in st.session_state: st.session_state.db = load_data()
if 'cart' not in st.session_state: st.session_state.cart = {}

# التحقق من الرابط السري (أضف ?view=tarek_king للرابط)
is_admin = st.query_params.get("view") == ADMIN_KEY

# --- واجهة المتجر ---
if not is_admin:
    st.markdown("<div class='main-title'>SM KhadamaTic</div>", unsafe_allow_html=True)
    
    col_main, col_cart = st.columns([2, 1])
    
    with col_main:
        selected_cat = st.selectbox("الأقسام:", ["الكل"] + st.session_state.db['categories'])
        prods = [p for p in st.session_state.db['products'] if selected_cat == "الكل" or p.get('category') == selected_cat]
        
        cols = st.columns(2) # متوافق مع الهاتف
        for i, p in enumerate(prods):
            with cols[i % 2]:
                st.markdown(f"<div class='product-card'><h4>{p['name']}</h4><p style='color:#006341;'><b>{p['price']} دج</b></p></div>", unsafe_allow_html=True)
                if st.button(f"أضف للسلة 🛒", key=f"btn_{p['name']}"):
                    st.session_state.cart[p['name']] = st.session_state.cart.get(p['name'], 0) + 1
                    st.rerun()

    with col_cart:
        st.subheader("🛒 طلباتك")
        total = 0
        details = ""
        for n, q in list(st.session_state.cart.items()):
            if q > 0:
                p_info = next(x for x in st.session_state.db['products'] if x['name'] == n)
                total += q * p_info['price']
                st.write(f"✅ {n} (x{q})")
                details += f"- {n} (x{q})\n"
                if st.button(f"حذف {n}", key=f"del_{n}"):
                    st.session_state.cart[n] = 0
                    st.rerun()
        
        if total > 0:
            reg = st.selectbox("المنطقة:", list(st.session_state.db['delivery_fees'].keys()))
            fee = st.session_state.db['delivery_fees'][reg]
            st.markdown(f"### الإجمالي: {total + fee} دج")
            
            # معلومات الزبون الإجبارية
            name = st.text_input("الاسم:")
            phone = st.text_input("الهاتف:")
            addr = st.text_area("العنوان:")
            
            if st.button("إرسال عبر واتساب 📲"):
                if name and phone and addr:
                    st.session_state.db['orders'].append({"التاريخ": datetime.now().strftime("%Y-%m-%d"), "الزبون": name, "المجموع": total+fee, "الطلبات": details})
                    save_data(st.session_state.db)
                    
                    msg = f"طلب جديد: {name}\nالهاتف: {phone}\nالعنوان: {addr}\nالطلبات:\n{details}الإجمالي: {total+fee} دج"
                    url = f"https://wa.me/213770000000?text={urllib.parse.quote(msg)}"
                    st.markdown(f'<a href="{url}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:8px; cursor:pointer;">تأكيد وفتح واتساب ✅</button></a>', unsafe_allow_html=True)
                else:
                    st.error("مولاي، املأ المعلومات!")

# --- لوحة التحكم (للملك فقط) ---
else:
    st.title("👑 لوحة تحكم مولاي طارق")
    t1, t2, t3 = st.tabs(["📦 المنتجات", "🚚 التوصيل", "📊 السجلات"])
    
    with t1:
        with st.form("p_f"):
            n = st.text_input("الاسم")
            p = st.number_input("السعر")
            c = st.selectbox("القسم", st.session_state.db['categories'])
            if st.form_submit_button("إضافة"):
                st.session_state.db['products'].append({"name": n, "price": p, "category": c})
                save_data(st.session_state.db)
                st.rerun()
    
    with t3:
        if st.session_state.db['orders']:
            df = pd.DataFrame(st.session_state.db['orders'])
            st.dataframe(df)
            # تصدير إكسل
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 تحميل سجل إكسل", data=buffer.getvalue(), file_name="orders.xlsx")
