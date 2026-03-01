import streamlit as st
import json, os, urllib.parse, pandas as pd
from datetime import datetime
from io import BytesIO
import base64

# 1. إعدادات الصفحة
st.set_page_config(page_title="SM KhadamaTic - Command Center", layout="wide")

# 2. التنسيق (Style) - METRO مع دعم الصور
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: #333; }
    .main-title { color: #006341; text-align: center; font-size: 40px; font-weight: bold; border-bottom: 3px solid #006341; padding-bottom: 10px; margin-bottom: 25px; }
    .product-card {
        background-color: #FFFFFF; padding: 15px; border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); text-align: center;
        border: 1px solid #EEE; margin-bottom: 20px;
    }
    .product-img { width: 100%; height: 150px; object-fit: cover; border-radius: 8px; margin-bottom: 10px; }
    div.stButton > button { 
        background-color: #006341 !important; color: white !important; 
        font-weight: bold; border-radius: 6px; width: 100%; height: 40px; border: none;
    }
    [data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# 3. إدارة البيانات والصور
DB_FILE = "sm_database.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {"products": [], "categories": ["خضروات", "فواكه", "عروض"], "drivers": [], "sellers": [], "orders": [], "settings": {"phone": "213770000000"}}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

if 'db' not in st.session_state: st.session_state.db = load_data()
if 'cart' not in st.session_state: st.session_state.cart = {}

is_admin = st.query_params.get("view") == "tarek_king"

# دالة لتحويل الصورة لـ Base64 لتخزينها في الملف
def img_to_base64(img_file):
    return base64.b64encode(img_file.getvalue()).decode()

# --- [1] واجهة المتجر (للزبائن) ---
if not is_admin:
    st.markdown("<div class='main-title'>SM KhadamaTic</div>", unsafe_allow_html=True)
    col_main, col_cart = st.columns([2.5, 1])
    
    with col_main:
        cat_select = st.selectbox("📂 الأقسام:", ["الكل"] + st.session_state.db['categories'])
        prods = [p for p in st.session_state.db['products'] if cat_select == "الكل" or p.get('category') == cat_select]
        
        for i in range(0, len(prods), 3):
            cols = st.columns(3)
            for j, p in enumerate(prods[i:i+3]):
                with cols[j]:
                    img_html = f"<img src='data:image/png;base64,{p['image']}' class='product-img'>" if 'image' in p and p['image'] else "<div style='height:150px; background:#f0f0f0; border-radius:8px; display:flex; align-items:center; justify-content:center;'>لا توجد صورة</div>"
                    st.markdown(f"""
                    <div class='product-card'>
                        {img_html}
                        <h4 style='margin:5px 0;'>{p['name']}</h4>
                        <h3 style='color:#006341; margin:0;'>{p['price']} دج</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"أضف للسلة 🛒", key=f"s_{i+j}"):
                        st.session_state.cart[p['name']] = st.session_state.cart.get(p['name'], 0) + 1
                        st.rerun()

    with col_cart:
        st.subheader("🛒 السلة")
        total = 0
        summary = ""
        for n, q in list(st.session_state.cart.items()):
            if q > 0:
                p_info = next(x for x in st.session_state.db['products'] if x['name'] == n)
                total += q * p_info['price']
                st.write(f"✅ **{n}** (x{q})")
                summary += f"- {n} (x{q})\n"
        if total > 0:
            st.divider()
            st.markdown(f"#### الإجمالي: {total} دج")
            u_name = st.text_input("الاسم:")
            if st.button("تأكيد وطلب 📲"):
                target = st.session_state.db.get('settings', {}).get('phone', '213770000000')
                msg = urllib.parse.quote(f"طلب جديد:\nالزبون: {u_name}\nالطلبات:\n{summary}💰 الإجمالي: {total} دج")
                st.markdown(f'<meta http-equiv="refresh" content="0;url=https://wa.me/{target}?text={msg}">', unsafe_allow_html=True)

# --- [2] لوحة الإدارة (التحكم المطلق بالصور) ---
else:
    st.markdown("<h1 style='text-align:center;'>⚙️ لوحة الإدارة</h1>", unsafe_allow_html=True)
    t1, t2, t3, t4, t5 = st.tabs(["📦 المنتجات", "🚚 الموصلين", "👥 البائعين", "📊 السجلات", "🔧 الإعدادات"])

    with t1:
        st.subheader("إضافة منتج جديد مع صورة")
        with st.form("p_add", clear_on_submit=True):
            n = st.text_input("اسم المنتج")
            p = st.number_input("السعر", 0)
            c = st.selectbox("القسم", st.session_state.db['categories'])
            img_file = st.file_uploader("اختر صورة المنتج (PNG/JPG)", type=['png', 'jpg', 'jpeg'])
            if st.form_submit_button("حفظ المنتج ✅"):
                if n:
                    img_base64 = img_to_base64(img_file) if img_file else ""
                    st.session_state.db['products'].append({"name": n, "price": p, "category": c, "image": img_base64})
                    save_data(st.session_state.db); st.rerun()
        
        st.divider()
        st.subheader("إدارة المنتجات")
        for i, prod in enumerate(st.session_state.db['products']):
            c1, c2, c3 = st.columns([1, 3, 1])
            if 'image' in prod and prod['image']:
                c1.image(f"data:image/png;base64,{prod['image']}", width=80)
            c2.write(f"**{prod['name']}** - {prod['price']} دج")
            if c3.button("حذف 🗑️", key=f"d_{i}"):
                st.session_state.db['products'].pop(i); save_data(st.session_state.db); st.rerun()

    # (بقية التبويبات تظل كما هي لضمان استقرار الموصلين والبائعين والسجلات)
    with t4:
        if st.session_state.db['orders']:
            df = pd.DataFrame(st.session_state.db['orders'])
            st.dataframe(df)
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 تحميل السجل (CSV)", data=csv, file_name="Report.csv")
