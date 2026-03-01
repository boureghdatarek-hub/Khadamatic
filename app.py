import streamlit as st
import json, os, urllib.parse, pandas as pd
import base64

# 1. إعدادات الصفحة والتنسيق (متوافق مع الهاتف والكمبيوتر)
st.set_page_config(page_title="SM KhadamaTic", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .main-title { color: #006341; text-align: center; font-size: clamp(24px, 5vw, 40px); font-weight: bold; border-bottom: 4px solid #006341; padding: 10px; margin-bottom: 20px; background: white; border-radius: 0 0 15px 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .product-card { border: 1px solid #EEE; padding: 15px; border-radius: 15px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.08); background: white; margin-bottom: 20px; transition: 0.3s; }
    .product-card:hover { transform: translateY(-5px); }
    .stButton > button { background-color: #006341 !important; color: white !important; font-weight: bold; width: 100%; border-radius: 10px; height: 50px; border: none; font-size: 18px; }
    .cart-section { background: #fff; padding: 20px; border-radius: 15px; border: 1px solid #ddd; position: sticky; top: 20px; }
    .stTabs [data-baseweb="tab-list"] { gap: 5px; }
    .stTabs [data-baseweb="tab"] { background-color: #e9ecef; border-radius: 8px 8px 0 0; padding: 10px 20px; font-weight: bold; color: #495057; }
    .stTabs [aria-selected="true"] { background-color: #006341 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# 2. إدارة البيانات
DB_FILE = "sm_database.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                keys = ["products", "categories", "drivers", "sellers", "orders", "settings"]
                for k in keys:
                    if k not in d: d[k] = [] if k != "settings" else {"phone": "213770000000"}
                return d
        except: pass
    return {"products": [], "categories": ["خضروات", "فواكه", "تمور", "عروض"], "drivers": [], "sellers": [], "orders": [], "settings": {"phone": "213770000000"}}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if 'db' not in st.session_state: st.session_state.db = load_data()
if 'cart' not in st.session_state: st.session_state.cart = {}

is_admin = st.query_params.get("view") == "tarek_king"

# --- [ واجهة الزبائن ] ---
if not is_admin:
    st.markdown("<div class='main-title'>SM KhadamaTic 🛒</div>", unsafe_allow_html=True)
    col_prods, col_cart = st.columns([2.5, 1])

    with col_prods:
        # شريط الأقسام
        cat_choice = st.tabs(["الكل"] + st.session_state.db['categories'])
        for idx, tab in enumerate(cat_choice):
            with tab:
                current_cat = (["الكل"] + st.session_state.db['categories'])[idx]
                filtered = [p for p in st.session_state.db['products'] if current_cat == "الكل" or p.get('category') == current_cat]
                
                if not filtered:
                    st.info("سيدي، لا توجد منتجات في هذا القسم حالياً.")
                
                # عرض المنتجات في شبكة (Grid)
                for i in range(0, len(filtered), 2):
                    cols = st.columns(2)
                    for j, p in enumerate(filtered[i:i+2]):
                        with cols[j]:
                            st.markdown("<div class='product-card'>", unsafe_allow_html=True)
                            if p.get('image'):
                                st.image(f"data:image/png;base64,{p['image']}", use_container_width=True)
                            st.markdown(f"<h3>{p['name']}</h3><h2 style='color:#006341;'>{p['price']} دج</h2>", unsafe_allow_html=True)
                            if st.button(f"إضافة للسلة 🛒", key=f"btn_{p['name']}_{i+j}"):
                                st.session_state.cart[p['name']] = st.session_state.cart.get(p['name'], 0) + 1
                                st.toast(f"تمت إضافة {p['name']} ✅")
                            st.markdown("</div>", unsafe_allow_html=True)

    with col_cart:
        st.markdown("<div class='cart-section'>", unsafe_allow_html=True)
        st.subheader("🧺 سلة المشتريات")
        total = 0
        order_msg = ""
        for name, qty in list(st.session_state.cart.items()):
            if qty > 0:
                p_data = next((x for x in st.session_state.db['products'] if x['name'] == name), None)
                if p_data:
                    subtotal = qty * p_data['price']
                    total += subtotal
                    st.write(f"**{name}**")
                    c1, c2, c3 = st.columns([1,1,1])
                    if c1.button("➖", key=f"minus_{name}"):
                        st.session_state.cart[name] -= 1
                        st.rerun()
                    c2.write(f"{qty}")
                    if c3.button("➕", key=f"plus_{name}"):
                        st.session_state.cart[name] += 1
                        st.rerun()
                    order_msg += f"- {name} ({qty} × {p_data['price']} = {subtotal} دج)\n"
        
        if total > 0:
            st.divider()
            st.markdown(f"### الإجمالي: {total} دج")
            user_name = st.text_input("اسم الزبون:", placeholder="ادخل اسمك هنا")
            user_addr = st.text_input("العنوان:", placeholder="عنوان التوصيل")
            
            if st.button("تأكيد الطلب عبر واتساب 📲"):
                if user_name and user_addr:
                    phone = st.session_state.db['settings'].get('phone', '213770000000')
                    final_msg = urllib.parse.quote(f"طلب جديد من: {user_name}\nالعنوان: {user_addr}\n\n{order_msg}\n💰 الإجمالي: {total} دج")
                    st.markdown(f'<meta http-equiv="refresh" content="0;url=https://wa.me/{phone}?text={final_msg}">', unsafe_allow_html=True)
                else:
                    st.error("يرجى إدخال الاسم والعنوان")
        else:
            st.write("السلة فارغة حالياً.")
        st.markdown("</div>", unsafe_allow_html=True)

# --- [ لوحة الإدارة ] ---
else:
    st.markdown("<div class='main-title'>⚙️ لوحة التحكم الملكية</div>", unsafe_allow_html=True)
    t1, t2, t3, t4, t5 = st.tabs(["📦 المنتجات", "🚚 الموصلين", "👥 البائعين", "📊 السجلات", "🔧 الإعدادات"])

    with t1:
        st.subheader("إضافة منتج جديد")
        with st.form("p_form", clear_on_submit=True):
            n = st.text_input("اسم المنتج")
            p = st.number_input("السعر (دج)", 0)
            c = st.selectbox("القسم", st.session_state.db['categories'])
            img = st.file_uploader("الصورة", type=['png','jpg','jpeg'])
            if st.form_submit_button("حفظ المنتج ✅"):
                b64 = base64.b64encode(img.getvalue()).decode() if img else ""
                st.session_state.db['products'].append({"name":n, "price":p, "category":c, "image":b64})
                save_data(st.session_state.db); st.rerun()
        
        st.divider()
        for i, prod in enumerate(st.session_state.db['products']):
            c1, c2, c3 = st.columns([1,3,1])
            if prod.get('image'): c1.image(f"data:image/png;base64,{prod['image']}", width=60)
            c2.write(f"**{prod['name']}** - {prod['price']} دج ({prod.get('category')})")
            if c3.button("حذف", key=f"del_p_{i}"):
                st.session_state.db['products'].pop(i); save_data(st.session_state.db); st.rerun()

    with t2:
        st.subheader("إدارة الموصلين")
        with st.form("d_form", clear_on_submit=True):
            dn = st.text_input("اسم الموصل")
            if st.form_submit_button("إضافة"):
                st.session_state.db['drivers'].append({"name": dn})
                save_data(st.session_state.db); st.rerun()
        for i, d in enumerate(st.session_state.db['drivers']):
            col1, col2 = st.columns([4,1])
            col1.write(f"🚚 {d['name']}")
            if col2.button("حذف", key=f"del_d_{i}"):
                st.session_state.db['drivers'].pop(i); save_data(st.session_state.db); st.rerun()

    with t3:
        st.subheader("إدارة البائعين")
        with st.form("s_form", clear_on_submit=True):
            sn = st.text_input("اسم البائع")
            if st.form_submit_button("إضافة"):
                st.session_state.db['sellers'].append({"name": sn})
                save_data(st.session_state.db); st.rerun()
        for i, s in enumerate(st.session_state.db['sellers']):
            col1, col2 = st.columns([4,1])
            col1.write(f"👤 {s['name']}")
            if col2.button("حذف", key=f"del_s_{i}"):
                st.session_state.db['sellers'].pop(i); save_data(st.session_state.db); st.rerun()

    with t4:
        st.subheader("📊 المبيعات")
        if st.session_state.db.get('orders'):
            st.dataframe(pd.DataFrame(st.session_state.db['orders']), use_container_width=True)
        else:
            st.info("لا توجد سجلات حالياً.")

    with t5:
        st.subheader("🔧 الإعدادات")
        ph = st.text_input("رقم الواتساب (مثال: 213770000000):", value=st.session_state.db['settings']['phone'])
        new_cats = st.text_area("الأقسام (قسم في كل سطر):", value="\n".join(st.session_state.db['categories']))
        if st.button("حفظ الإعدادات 💾"):
            st.session_state.db['settings']['phone'] = ph
            st.session_state.db['categories'] = [x.strip() for x in new_cats.split("\n") if x.strip()]
            save_data(st.session_state.db); st.success("تم الحفظ!")
