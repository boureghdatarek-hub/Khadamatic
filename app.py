import streamlit as st
import json, os, base64
import urllib.parse
import pandas as pd
from datetime import datetime

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f9f9f9; }
    .product-card { 
        background: white; padding: 15px; border-radius: 15px; 
        border: 1px solid #ddd; text-align: center; margin-bottom: 20px;
    }
    .stButton > button { border-radius: 25px !important; width: 100%; }
    .price-text { color: #006341; font-weight: bold; font-size: 1.2rem; }
</style>
""", unsafe_allow_html=True)

# --- 2. إدارة البيانات ---
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
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'selected_cat' not in st.session_state: st.session_state.selected_cat = "الكل"

# --- 3. التحقق من وضع الإدارة ---
is_admin_link = st.query_params.get("admin") == "true"

# --- 4. لوحة التحكم (Admin) ---
if is_admin_link:
    pwd = st.sidebar.text_input("كلمة المرور", type="password")
    if pwd == "tarek2026":
        st.title("⚙️ الإدارة")
        tab_p, tab_d, tab_o = st.tabs(["📦 المنتجات", "🚚 الموصلين", "📊 سجل الطلبات"])
        
        with tab_p:
            st.subheader("إضافة منتج جديد")
            with st.form("p_form", clear_on_submit=True):
                n = st.text_input("اسم المنتج")
                p = st.number_input("السعر", 0)
                c = st.selectbox("التصنيف", st.session_state.db["categories"])
                img = st.file_uploader("الصورة")
                if st.form_submit_button("حفظ المنتج"):
                    img_b64 = base64.b64encode(img.read()).decode() if img else ""
                    st.session_state.db["products"].append({"name": n, "price": p, "cat": c, "img": img_b64})
                    save_db(st.session_state.db); st.rerun()

        with tab_d:
            st.subheader("إدارة الموصلين")
            # نموذج إضافة موصل
            with st.form("d_form", clear_on_submit=True):
                d_name = st.text_input("اسم الموصل")
                d_phone = st.text_input("رقم الواتساب (مثال: 213665577427)")
                if st.form_submit_button("إضافة موصل 🚚"):
                    if d_name and d_phone:
                        st.session_state.db["drivers"].append({"name": d_name, "phone": d_phone, "status": "متاح"})
                        save_db(st.session_state.db); st.rerun()
            
            st.divider()
            # عرض الموصلين الحاليين
            for i, d in enumerate(st.session_state.db["drivers"]):
                col1, col2, col3 = st.columns([2, 2, 1])
                col1.write(f"👤 **{d['name']}**")
                col2.write(f"📞 {d['phone']}")
                if col3.button("حذف 🗑️", key=f"del_d_{i}"):
                    st.session_state.db["drivers"].pop(i)
                    save_db(st.session_state.db); st.rerun()

        with tab_o:
            if st.session_state.db["orders"]:
                st.dataframe(pd.DataFrame(st.session_state.db["orders"]), use_container_width=True)

# --- 5. واجهة المحل ---
if not is_admin_link or (is_admin_link and pwd != "tarek2026"):
    st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)
    
    # اختيار التصنيف
    cats = ["الكل"] + st.session_state.db["categories"]
    cols = st.columns(len(cats))
    for i, cat in enumerate(cats):
        if cols[i].button(cat, use_container_width=True): st.session_state.selected_cat = cat; st.rerun()

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
                    if p.get("img"): st.markdown(f'<img src="data:image/png;base64,{p["img"]}" style="width:100%; height:120px; object-fit:contain;">', unsafe_allow_html=True)
                    st.write(f"**{p['name']}**")
                    st.markdown(f'<p class="price-text">{p["price"]} دج</p>', unsafe_allow_html=True)
                    qty = st.number_input("الكمية", 0.5, 20.0, 1.0, 0.5, key=f"q_{p['name']}")
                    if st.button("إضافة 🛒", key=f"btn_{p['name']}"):
                        if p['name'] in st.session_state.cart:
                            st.session_state.cart[p['name']]['qty'] += qty
                        else:
                            st.session_state.cart[p['name']] = {'price': p['price'], 'qty': qty}
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    with col_cart:
        st.subheader("🛒 سلتك")
        total = 0
        summary = []
        if not st.session_state.cart:
            st.info("السلة فارغة")
        else:
            for name, info in list(st.session_state.cart.items()):
                sub = info['price'] * info['qty']
                total += sub
                st.write(f"**{name}**: {info['qty']} كغ = {int(sub)} دج")
                summary.append(f"{name} ({info['qty']} كغ)")
            
            st.markdown(f"### المجموع: {int(total)} دج")
            with st.form("order_form"):
                u_name = st.text_input("الاسم")
                u_phone = st.text_input("الهاتف")
                u_addr = st.text_area("العنوان")
                # قائمة الموصلين المضافة من لوحة التحكم تظهر هنا
                drivers = st.session_state.db["drivers"]
                sel_d = st.selectbox("اختر الموصل", [d['name'] for d in drivers]) if drivers else None
                
                if st.form_submit_button("إرسال للواتساب 🚀"):
                    if u_name and drivers:
                        d_info = next(d for d in drivers if d["name"] == sel_d)
                        items_str = " + ".join(summary)
                        msg = f"طلب من: {u_name}\n📱: {u_phone}\n📍: {u_addr}\n🛍️: {items_str}\n💰 المجموع: {int(total)} دج"
                        st.markdown(f'<a href="https://wa.me/{d_info["phone"]}?text={urllib.parse.quote(msg)}" target="_blank" style="background:#006341;color:white;display:block;text-align:center;padding:12px;border-radius:10px;text-decoration:none;">تأكيد عبر واتساب</a>', unsafe_allow_html=True)
                        st.session_state.cart = {}
