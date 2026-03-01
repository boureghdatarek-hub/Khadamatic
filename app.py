import streamlit as st
import json
import os
import urllib.parse
import pandas as pd
from datetime import datetime

# 1. إعدادات الصفحة والوضع الليلي (Dark Theme)
st.set_page_config(page_title="KhadamaTic Pro", layout="wide", initial_sidebar_state="collapsed")

# تنسيق CSS لفرض الوضع الليلي وتجميل الأزرار والكروت
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    h1, h2, h3 { color: #4CAF50 !important; text-align: center; font-family: 'Arial'; }
    .product-card {
        background-color: #1C2128;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #333;
        text-align: center;
        margin-bottom: 15px;
        transition: 0.3s;
    }
    .product-card:hover { border-color: #4CAF50; transform: translateY(-5px); }
    div.stButton > button {
        background-color: #2E7D32 !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: bold;
        width: 100%;
        border: none;
        padding: 10px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #1C2128; border-radius: 5px; padding: 10px 20px; color: white;
    }
</style>
""", unsafe_allow_html=True)

# 2. إدارة البيانات (قاعدة بيانات JSON)
DB_FILE = "khadamatict_db.json"

def load_data():
    base = {"products": [], "categories": ["خضروات", "فواكه", "عروض"], "orders": []}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for key in base:
                    if key not in data: data[key] = base[key]
                return data
        except: return base
    return base

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if 'db' not in st.session_state: st.session_state.db = load_data()
if 'cart' not in st.session_state: st.session_state.cart = {}

# --- كلمة السر الخاصة بك ---
ADMIN_PASSWORD = "tarek_khadamatict"

# 3. دالة الحماية (Login)
def check_auth(area_id):
    key = f"is_authed_{area_id}"
    if key not in st.session_state: st.session_state[key] = False
    
    if not st.session_state[key]:
        st.markdown(f"### 🔒 منطقة محمية ({area_id})")
        pwd = st.text_input("أدخل كلمة السر:", type="password", key=f"in_{area_id}")
        if st.button("دخول", key=f"btn_{area_id}"):
            if pwd == ADMIN_PASSWORD:
                st.session_state[key] = True
                st.rerun()
            else: st.error("كلمة السر خاطئة!")
        return False
    return True

# --- واجهة التطبيق ---
st.markdown("<h1>🌿 KhadamaTic | خَدَماتِك 🌿</h1>", unsafe_allow_html=True)
t1, t2, t3 = st.tabs(["🛒 المتجر الرئيسي", "📊 سجل الطلبات", "⚙️ لوحة التحكم"])

# --- التبويب 1: المتجر (متاح للجميع) ---
with t1:
    col_products, col_cart = st.columns([2, 1])
    
    with col_products:
        st.subheader("المنتجات")
        if not st.session_state.db['products']:
            st.info("لا توجد منتجات حالياً. أضف بعضها من لوحة التحكم.")
        
        cols = st.columns(2)
        for i, p in enumerate(st.session_state.db['products']):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="product-card">
                    <h3>{p['name']}</h3>
                    <p style="font-size: 20px; color: #4CAF50;">{p['price']} دج</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"إضافة للسلة 🛒", key=f"add_{i}"):
                    st.session_state.cart[p['name']] = st.session_state.cart.get(p['name'], 0) + 1
                    st.rerun()

    with col_cart:
        st.subheader("🛒 السلة")
        total_price = 0
        order_summary = ""
        
        for name, qty in list(st.session_state.cart.items()):
            if qty > 0:
                p_info = next(x for x in st.session_state.db['products'] if x['name'] == name)
                item_total = qty * p_info['price']
                total_price += item_total
                st.write(f"**{name}** (x{qty}) = {item_total} دج")
                order_summary += f"- {name} (x{qty})\n"
                if st.button("إزالة ❌", key=f"rel_{name}"):
                    st.session_state.cart[name] = 0
                    st.rerun()
        
        st.divider()
        st.markdown(f"### الإجمالي: {total_price} دج")
        
        cust_name = st.text_input("اسم الزبون:")
        phone = st.text_input("رقم الهاتف:")
        
        if st.button("✅ تأكيد وحفظ الطلب") and total_price > 0 and cust_name:
            new_order = {
                "id": len(st.session_state.db['orders']) + 1,
                "customer": cust_name,
                "details": order_summary,
                "total": total_price,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "status": "قيد التجهيز 🟡"
            }
            st.session_state.db['orders'].append(new_order)
            save_data(st.session_state.db)
            st.success("تم تسجيل الطلب في السجل!")
            
        if total_price > 0 and cust_name:
            msg = f"طلب جديد من: {cust_name}\nالهاتف: {phone}\n{order_summary}الإجمالي: {total_price} دج"
            whatsapp_url = f"https://wa.me/213770000000?text={urllib.parse.quote(msg)}" # استبدل بالرقم الخاص بك
            st.link_button("📲 إرسال الطلب عبر واتساب", whatsapp_url)

# --- التبويب 2: السجل (محمي) ---
with t2:
    if check_auth("السجل"):
        st.subheader("📈 سجل المبيعات")
        if st.session_state.db['orders']:
            df = pd.DataFrame(st.session_state.db['orders'])
            st.dataframe(df, use_container_width=True)
            if st.button("مسح السجل 🗑️"):
                st.session_state.db['orders'] = []
                save_data(st.session_state.db)
                st.rerun()
        else:
            st.info("السجل فارغ.")

# --- التبويب 3: الإدارة (محمي) ---
with t3:
    if check_auth("الإدارة"):
        st.subheader("🛠 إضافة منتج جديد")
        with st.form("add_product", clear_on_submit=True):
            name = st.text_input("اسم المنتج")
            price = st.number_input("السعر (دج)", min_value=0)
            category = st.selectbox("الصنف", st.session_state.db['categories'])
            if st.form_submit_button("إضافة للمتجر ✅"):
                if name:
                    st.session_state.db['products'].append({"name": name, "price": price, "category": category})
                    save_data(st.session_state.db)
                    st.success(f"تمت إضافة {name} بنجاح!")
                    st.rerun()
        
        st.divider()
        st.subheader("📋 قائمة المنتجات الحالية")
        for i, p in enumerate(st.session_state.db['products']):
            col1, col2 = st.columns([3, 1])
            col1.write(f"**{p['name']}** - {p['price']} دج")
            if col2.button("حذف 🗑", key=f"del_p_{i}"):
                st.session_state.db['products'].pop(i)
                save_data(st.session_state.db)
                st.rerun()
