import streamlit as st
import json, os, base64
import urllib.parse
import pandas as pd
from datetime import datetime

# --- 1. تنسيق الواجهة (إلغاء الفراغات والـ CSS) ---
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

st.markdown("""
<style>
    /* تقليل الفراغ العلوي */
    .block-container { padding-top: 1rem !important; }
    
    /* أزرار التصنيفات */
    .stButton > button { border-radius: 10px; font-weight: bold; }
    
    /* كارت المنتج والـ Grid */
    .product-box { 
        border: 1px solid #ddd; padding: 10px; border-radius: 15px; 
        text-align: center; background: white; margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        min-height: 380px; display: flex; flex-direction: column; justify-content: space-between;
    }
    .product-img { width: 100%; height: 140px; object-fit: contain; border-radius: 8px; }
    
    /* زر الإضافة للسلة (ملون ومميز) */
    .stButton > button[kind="primary"] { 
        background-color: #e67e22 !important; border: none !important; color: white !important; 
    }
    
    .price-text { color: #27ae60; font-weight: bold; font-size: 1.2rem; }
</style>
""", unsafe_allow_html=True)

# --- 2. قاعدة البيانات ---
DB_FILE = "sm_khadamat_db.json"

def load_db():
    
    
    
    
    defaults = {"products": [], "drivers": [], "orders": [], "categories": ["خضر", "فواكه", "عروض"]}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                for k in defaults:
                    if k not in d: d[k] = defaults[k]
                return d
        except: return defaults
    return defaults

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if 'db' not in st.session_state: st.session_state.db = load_db()
if 'cart' not in st.session_state: st.session_state.cart = []

# --- 3. لوحة التحكم ---
is_admin = st.sidebar.checkbox("🔒 لوحة الإدارة")
if is_admin:
    if st.sidebar.text_input("كلمة السر", type="password") == "tarek2026":
        st.title("⚙️ إدارة SM KHADAMATIC")
        t1, t2, t3 = st.tabs(["📦 المنتجات", "🚚 الموصلين", "📊 سجل الطلبات"])
        
        with t1:
            with st.form("add_p_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                n = col1.text_input("اسم المنتج")
                p = col2.number_input("السعر", min_value=1)
                c = st.selectbox("التصنيف", st.session_state.db["categories"])
                img = st.file_uploader("الصورة")
                if st.form_submit_button("إضافة المنتج ✅"):
                    img_b64 = base64.b64encode(img.read()).decode() if img else ""
                    st.session_state.db["products"].append({"name": n, "price": p, "cat": c, "img": img_b64})
                    save_db(st.session_state.db); st.rerun()
            
            for i, pr in enumerate(st.session_state.db["products"]):
                c1, c2, c3 = st.columns([1, 4, 1])
                c2.write(f"**{pr['name']}** - {pr['price']} DA ({pr.get('cat', '')})")
                if c3.button("🗑️", key=f"del_{i}"):
                    st.session_state.db["products"].pop(i); save_db(st.session_state.db); st.rerun()

        with t2:
            with st.form("d_form"):
                dn = st.text_input("اسم الموصل"); dp = st.text_input("رقم الواتساب (213...)")
                if st.form_submit_button("إضافة موصل"):
                    st.session_state.db["drivers"].append({"name": dn, "phone": dp, "status": "متاح"})
                    save_db(st.session_state.db); st.rerun()

        with t3:
            if st.session_state.db["orders"]:
                # عرض السجل كما كان سابقاً
                df = pd.DataFrame(st.session_state.db["orders"])
                st.table(df[::-1]) # عرض الجدول بشكل كلاسيكي مرتب
                if st.button("🗑️ حذف السجلات"):
                    st.session_state.db["orders"] = []; save_db(st.session_state.db); st.rerun()

# --- 4. المتجر (الزبائن) ---
else:
    st.markdown("<h2 style='text-align:center;'>🛒 SM KHADAMATIC</h2>", unsafe_allow_html=True)
    
    # تصنيفات (بدون فراغ كبير)
    cats = ["الكل"] + st.session_state.db["categories"]
    selected_cat = st.segmented_control("التصنيف:", cats, default="الكل")

    prods = st.session_state.db["products"]
    if selected_cat != "الكل":
        prods = [p for p in prods if p.get("cat") == selected_cat]

    # Grid المنتجات
    for i in range(0, len(prods), 3):
        cols = st.columns(3)
        for j, p in enumerate(prods[i:i+3]):
            with cols[j]:
                st.markdown('<div class="product-box">', unsafe_allow_html=True)
                if p.get("img"):
                    st.markdown(f'<img src="data:image/png;base64,{p["img"]}" class="product-img">', unsafe_allow_html=True)
                st.markdown(f"**{p['name']}**")
                st.markdown(f'<p class="price-text">{p["price"]} DA</p>', unsafe_allow_html=True)
                qty = st.number_input("الكمية (كغ)", 0.5, 50.0, 1.0, 0.5, key=f"q_{i+j}")
                if st.button(f"إضافة 🛒", key=f"btn_{i+j}", type="primary"):
                    st.session_state.cart.append({"name": p['name'], "price": p['price']*qty, "qty": qty})
                    st.toast(f"✅ تم الإضافة")
                st.markdown('</div>', unsafe_allow_html=True)

# --- 5. السلة وتأكيد الطلب (حل مشكلة الواتساب) ---
if st.session_state.cart:
    with st.sidebar:
        st.header("🛒 طلبياتك")
        # تجميع الطلبات المتشابهة
        summary = {}
        total = 0
        for item in st.session_state.cart:
            name = item['name']
            summary[name] = summary.get(name, 0) + item['qty']
            total += item['price']
        
        for n, q in summary.items():
            st.write(f"• {n}: {q} كغ")
        
        st.markdown(f"### المجموع: {int(total)} DA")
        
        with st.form("checkout_form"):
            un = st.text_input("الاسم")
            up = st.text_input("الهاتف")
            ua = st.text_area("العنوان")
            drivers = [d for d in st.session_state.db["drivers"] if d.get("status") == "متاح"]
            target_d = st.selectbox("اختر الموصل", [d['name'] for d in drivers]) if drivers else None
            
            if st.form_submit_button("إرسال الطلب ✅"):
                if un and up and target_d:
                    driver = next(d for d in drivers if d['name'] == target_d)
                    items_list = " | ".join([f"{n} ({q}كغ)" for n, q in summary.items()])
                    
                    # حفظ في السجل
                    st.session_state.db["orders"].append({
                        "الزبون": un, "الهاتف": up, "الطلبات": items_list, 
                        "المجموع": int(total), "التاريخ": datetime.now().strftime("%Y-%m-%d")
                    })
                    save_db(st.session_state.db)
                    
                    # بناء رسالة الواتساب بدقة
                    msg = f"طلب جديد من: {un}\nالهاتف: {up}\nالعنوان: {ua}\nالطلبات: {items_list}\nالمجموع: {int(total)} DA"
                    encoded_msg = urllib.parse.quote(msg)
                    url = f"https://wa.me/{driver['phone']}?text={encoded_msg}"
                    
                    st.markdown(f'<a href="{url}" target="_blank" style="background:#25D366;color:white;display:block;text-align:center;padding:12px;border-radius:10px;text-decoration:none;font-weight:bold;">إرسال عبر واتساب 🚚</a>', unsafe_allow_html=True)
                    st.session_state.cart = []
                else: st.error("يرجى ملء البيانات!")
