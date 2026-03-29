import streamlit as st
import json, os, base64
import urllib.parse
import pandas as pd
from datetime import datetime
import io

# --- 1. إعدادات الصفحة والتنسيق ---
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f9f9f9; color: #333333; }
    div[data-baseweb="select"] * { color: #ffffff !important; background-color: #262730 !important; }
    .stSelectbox label p { color: #006341 !important; font-weight: bold; font-size: 1.1rem; }
    .product-card { 
        background: white !important; padding: 15px; border-radius: 15px; 
        border: 1px solid #ddd; text-align: center; margin-bottom: 20px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
    }
    .product-img { 
        width: 100%; height: 150px; object-fit: contain; 
        background-color: white; margin-bottom: 10px; border-radius: 10px;
    }
    .stButton > button { 
        border-radius: 25px !important; border: 2px solid #006341 !important; 
        background-color: white !important; color: #006341 !important; 
        font-weight: bold !important; width: 100%; transition: 0.3s;
    }
    .stButton > button:hover { background-color: #006341 !important; color: white !important; }
    .price-text { color: #006341 !important; font-weight: bold; font-size: 1.3rem; margin: 10px 0; }
    h1, h2, h3, p, span, label { color: #1a1a1a !important; }
    input, textarea { background-color: white !important; color: black !important; border: 1px solid #ccc !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. إدارة قاعدة البيانات ---
DB_FILE = "sm_khadamat_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"products": [], "drivers": [], "sellers": [], "orders": [], "categories": ["خضر", "فواكه", "عروض"]}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# تهيئة بيانات الجلسة
if 'db' not in st.session_state:
    st.session_state.db = load_db()
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'selected_cat' not in st.session_state:
    st.session_state.selected_cat = "الكل"

# --- 3. تحديد الصلاحيات (الرابط السري) ---
# سيعمل وضع الإدارة فقط إذا كان الرابط يحتوي على ?admin=true
is_admin_link = st.query_params.get("admin") == "true"

# --- 4. لوحة التحكم (Admin) ---
if is_admin_link:
    st.sidebar.title("🔐 دخول الإدارة")
    pwd = st.sidebar.text_input("كلمة المرor", type="password")
    
    if pwd == "tarek2026":
        st.title("⚙️ لوحة التحكم - SM KHADAMATIC")
        tabs = st.tabs(["📦 المنتجات", "🚚 الموصلين", "👥 البائعين", "📊 السجلات"])

        with tabs[0]: # المنتجات
            st.subheader("إضافة منتج")
            with st.form("add_p"):
                n = st.text_input("اسم المنتج")
                p = st.number_input("السعر للكيلو", 0)
                cat = st.selectbox("التصنيف", st.session_state.db["categories"])
                img_file = st.file_uploader("الصورة", type=['png','jpg','jpeg'])
                if st.form_submit_button("حفظ ✅"):
                    img_data = base64.b64encode(img_file.read()).decode() if img_file else ""
                    st.session_state.db["products"].append({"name": n, "price": p, "cat": cat, "img": img_data, "seller": ""})
                    save_db(st.session_state.db)
                    st.rerun()
            
            for i, pr in enumerate(st.session_state.db["products"]):
                c1, c2, c3 = st.columns([1, 4, 1])
                if pr.get("img"): c1.image(base64.b64decode(pr["img"]), width=50)
                c2.write(f"**{pr['name']}** - {pr['price']} دج")
                if c3.button("🗑️", key=f"del_{i}"):
                    st.session_state.db["products"].pop(i)
                    save_db(st.session_state.db)
                    st.rerun()

        with tabs[1]: # الموصلين
            st.subheader("إدارة الموصلين")
            with st.form("add_d"):
                dn = st.text_input("الاسم")
                dp = st.text_input("رقم الهاتف (213...)")
                if st.form_submit_button("إضافة 🚚"):
                    st.session_state.db["drivers"].append({"name": dn, "phone": dp, "status": "متاح"})
                    save_db(st.session_state.db)
                    st.rerun()
            for i, d in enumerate(st.session_state.db["drivers"]):
                st.write(f"🚚 {d['name']} ({d['status']})")
                if st.button(f"تغيير الحالة لـ {d['name']}", key=f"stat_{i}"):
                    st.session_state.db["drivers"][i]["status"] = "مشغول" if d['status'] == "متاح" else "متاح"
                    save_db(st.session_state.db)
                    st.rerun()

        with tabs[3]: # السجلات
            if st.session_state.db["orders"]:
                st.dataframe(pd.DataFrame(st.session_state.db["orders"]))
                if st.button("🗑️ مسح السجل"):
                    st.session_state.db["orders"] = []
                    save_db(st.session_state.db)
                    st.rerun()

# --- 5. واجهة الزبائن (تظهر دائماً) ---
# إذا لم يكن في وضع الإدارة أو كلمة السر خطأ، تظهر واجهة المحل فقط
if not is_admin_link or (is_admin_link and pwd != "tarek2026"):
    st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)
    
    # الفلترة والبحث
    search_q = st.text_input("🔍 ابحث عن منتج...", "").lower()
    cat_list = ["الكل"] + st.session_state.db["categories"]
    c_btns = st.columns(len(cat_list))
    for i, cat in enumerate(cat_list):
        if c_btns[i].button(cat, use_container_width=True):
            st.session_state.selected_cat = cat
            st.rerun()

    st.divider()
    col_main, col_cart = st.columns([3, 1.8]) 
    
    with col_main:
        prods = st.session_state.db["products"]
        if st.session_state.selected_cat != "الكل": 
            prods = [p for p in prods if p.get("cat") == st.session_state.selected_cat]
        if search_q:
            prods = [p for p in prods if search_q in p['name'].lower()]

        for i in range(0, len(prods), 3):
            grid = st.columns(3)
            for j, p in enumerate(prods[i:i+3]):
                with grid[j]:
                    st.markdown('<div class="product-card">', unsafe_allow_html=True)
                    if p.get("img"): 
                        st.markdown(f'<img src="data:image/png;base64,{p["img"]}" class="product-img">', unsafe_allow_html=True)
                    st.subheader(p['name'])
                    st.markdown(f'<p class="price-text">{p["price"]} دج</p>', unsafe_allow_html=True)
                    q = st.number_input("الكمية", 0.5, 50.0, 1.0, 0.5, key=f"q_{p['name']}_{i+j}")
                    if st.button("إضافة 🛒", key=f"a_{p['name']}_{i+j}"):
                        st.session_state.cart.append({"name": p['name'], "price": p['price']*q, "qty": q})
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    with col_cart:
        st.subheader("🛒 سلتك")
        total = 0
        if not st.session_state.cart:
            st.info("السلة فارغة")
        else:
            for item in st.session_state.cart:
                st.write(f"**{item['name']}**: {item['qty']} كغ")
                total += item['price']
            
            st.write(f"### المجموع: {int(total)} دج")
            with st.form("order"):
                u_name = st.text_input("الاسم")
                u_phone = st.text_input("الهاتف")
                drivers = [d for d in st.session_state.db["drivers"] if d["status"] == "متاح"]
                d_names = [d['name'] for d in drivers]
                sel_d = st.selectbox("الموصل", d_names) if drivers else "لا يوجد موصل"
                
                if st.form_submit_button("إرسال الطلب"):
                    if u_name and u_phone and drivers:
                        d_info = next(d for d in drivers if d["name"] == sel_d)
                        st.session_state.db["orders"].append({
                            "name": u_name, "phone": u_phone, "total": int(total), 
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        save_db(st.session_state.db)
                        msg = f"طلب جديد من {u_name} بمجموع {int(total)} دج"
                        st.markdown(f'<a href="https://wa.me/{d_info["phone"]}?text={urllib.parse.quote(msg)}" target="_blank" style="background:#006341;color:white;display:block;text-align:center;padding:12px;border-radius:10px;text-decoration:none;font-weight:bold;">واتساب الموصل 🚚</a>', unsafe_allow_html=True)
