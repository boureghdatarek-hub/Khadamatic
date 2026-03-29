import streamlit as st
import json, os, base64
import urllib.parse
import pandas as pd
from datetime import datetime

# --- 1. إعدادات الصفحة والتنسيق ---
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f9f9f9; color: #333333; }
    .product-card { 
        background: white !important; padding: 15px; border-radius: 15px; 
        border: 1px solid #ddd; text-align: center; margin-bottom: 20px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
    }
    .product-img { width: 100%; height: 150px; object-fit: contain; margin-bottom: 10px; }
    .price-text { color: #006341 !important; font-weight: bold; font-size: 1.3rem; }
    .stButton > button { border-radius: 25px !important; border: 2px solid #006341 !important; color: #006341 !important; width: 100%; }
    .stButton > button:hover { background-color: #006341 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. إدارة قاعدة البيانات ---
DB_FILE = "sm_khadamat_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {"products": [], "drivers": [], "orders": [], "categories": ["خضر", "فواكه", "عروض"]}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if 'db' not in st.session_state: st.session_state.db = load_db()
if 'cart' not in st.session_state: st.session_state.cart = {} # تغيير السلة لتكون قاموساً للتجميع
if 'selected_cat' not in st.session_state: st.session_state.selected_cat = "الكل"

# --- 3. الصلاحيات ---
is_admin_link = st.query_params.get("admin") == "true"

# --- 4. لوحة التحكم (مختصرة للسرعة) ---
if is_admin_link:
    pwd = st.sidebar.text_input("كلمة المرور", type="password")
    if pwd == "tarek2026":
        st.title("⚙️ الإدارة")
        t1, t2 = st.tabs(["📦 المنتجات", "🚚 الموصلين"])
        with t1:
            with st.form("add_p"):
                n = st.text_input("الاسم"); p = st.number_input("السعر", 0); cat = st.selectbox("التصنيف", st.session_state.db["categories"])
                img = st.file_uploader("الصورة")
                if st.form_submit_button("حفظ"):
                    img_data = base64.b64encode(img.read()).decode() if img else ""
                    st.session_state.db["products"].append({"name": n, "price": p, "cat": cat, "img": img_data})
                    save_db(st.session_state.db); st.rerun()

# --- 5. واجهة الزبائن ---
if not is_admin_link or (is_admin_link and pwd != "tarek2026"):
    st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)
    
    # تصنيفات
    cats = ["الكل"] + st.session_state.db["categories"]
    cols = st.columns(len(cats))
    for i, c in enumerate(cats):
        if cols[i].button(c, use_container_width=True): st.session_state.selected_cat = c; st.rerun()

    st.divider()
    col_main, col_cart = st.columns([3, 1.8])

    with col_main:
        prods = st.session_state.db["products"]
        if st.session_state.selected_cat != "الكل":
            prods = [p for p in prods if p.get("cat") == st.session_state.selected_cat]
        
        for i in range(0, len(prods), 3):
            grid = st.columns(3)
            for j, p in enumerate(prods[i:i+3]):
                with grid[j]:
                    st.markdown('<div class="product-card">', unsafe_allow_html=True)
                    if p.get("img"): st.markdown(f'<img src="data:image/png;base64,{p["img"]}" class="product-img">', unsafe_allow_html=True)
                    st.write(f"### {p['name']}")
                    st.markdown(f'<p class="price-text">{p["price"]} دج</p>', unsafe_allow_html=True)
                    qty = st.number_input("الكمية", 0.5, 50.0, 1.0, 0.5, key=f"q_{p['name']}")
                    if st.button("إضافة 🛒", key=f"b_{p['name']}"):
                        # منطق التجميع: إذا المنتج موجود نزيد الكمية، إذا لا ننشئه
                        if p['name'] in st.session_state.cart:
                            st.session_state.cart[p['name']]['qty'] += qty
                        else:
                            st.session_state.cart[p['name']] = {'price': p['price'], 'qty': qty}
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    with col_cart:
        st.subheader("🛒 سلتك")
        total = 0
        summary_list = []
        
        if not st.session_state.cart:
            st.info("السلة فارغة")
        else:
            for name, info in list(st.session_state.cart.items()):
                c1, c2 = st.columns([4, 1])
                item_total = info['price'] * info['qty']
                total += item_total
                c1.write(f"**{name}** \n {info['qty']} كغ = {int(item_total)} دج")
                if c2.button("❌", key=f"rm_{name}"):
                    del st.session_state.cart[name]; st.rerun()
                summary_list.append(f"{name} ({info['qty']} كغ)")

            st.markdown(f"## المجموع: {int(total)} دج")
            
            with st.form("checkout"):
                u_name = st.text_input("الاسم")
                u_phone = st.text_input("الهاتف")
                u_addr = st.text_area("العنوان بالتفصيل")
                drivers = [d for d in st.session_state.db["drivers"] if d["status"] == "متاح"]
                sel_d = st.selectbox("اختر الموصل", [d['name'] for d in drivers]) if drivers else None
                
                if st.form_submit_button("إرسال الطلب عبر واتساب"):
                    if u_name and u_phone and sel_d:
                        d_info = next(d for d in drivers if d["name"] == sel_d)
                        items_text = " + ".join(summary_list)
                        
                        # رسالة الواتساب منسقة ومرتبة
                        msg = (f"طلب جديد من: {u_name}\n"
                               f"📱 الهاتف: {u_phone}\n"
                               f"📍 العنوان: {u_addr}\n"
                               f"🛍️ المشتريات: {items_text}\n"
                               f"💰 المجموع: {int(total)} دج")
                        
                        encoded_msg = urllib.parse.quote(msg)
                        whatsapp_url = f"https://wa.me/{d_info['phone']}?text={encoded_msg}"
                        
                        st.success("تم تجهيز الطلب!")
                        st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="background:#006341;color:white;display:block;text-align:center;padding:15px;border-radius:10px;text-decoration:none;font-weight:bold;">🚀 اضغط هنا لإرسال الطلب للموصل</a>', unsafe_allow_html=True)
                    else:
                        st.error("يرجى إكمال البيانات")
