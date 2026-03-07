import streamlit as st
import json, os, base64
import urllib.parse
import pandas as pd
from datetime import datetime
import io

# --- 1. إعدادات الصفحة والتنسيق (CSS المحسن للهاتف والـ Dark Mode) ---
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

<style>
    /* 1. Global Background & Text Reset */
    .stApp { background-color: #ffffff !important; }
    
    /* 2. Force all text in the Cart and Form to be DARK */
    .stMarkdown, p, span, label, div { 
        color: #1a1a1a !important; 
    }

    /* 3. Fix Input Fields (Name, Phone, Address) */
    /* This ensures inputs have a light background and dark text */
    input, textarea, [data-baseweb="select"] {
        background-color: #f0f2f6 !important;
        color: #000000 !important;
        border: 1px solid #006341 !important;
    }

    /* 4. Fix Selectbox (Delivery Man Name) */
    /* This forces the dropdown text to be black so you can see 'Salim' or 'Tarek' */
    div[data-baseweb="select"] * {
        color: #000000 !important;
    }

    /* 5. Mobile Specific Fixes */
    @media (max-width: 640px) {
        .product-card { background: #f9f9f9 !important; border: 1px solid #eee; }
        h1, h2, h3 { color: #006341 !important; }
        
        /* Ensures the 'Total Amount' (المجموع) is visible */
        .stMarkdown h3 { color: #1a1a1a !important; }
    }

    /* 6. Button Style */
    .stButton > button {
        background-color: #006341 !important;
        color: white !important;
        border-radius: 10px !important;
    }
</style>
# --- 2. إدارة قاعدة البيانات ---
DB_FILE = "sm_khadamat_db.json"
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {"products": [], "drivers": [], "sellers": [], "orders": [], "categories": ["خضر", "فواكه", "عروض"]}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

if 'db' not in st.session_state: st.session_state.db = load_db()
if 'cart' not in st.session_state: st.session_state.cart = []
if 'selected_cat' not in st.session_state: st.session_state.selected_cat = "الكل"

# --- 3. تحديد الصلاحيات ---
is_admin = st.query_params.get("view") == "tarek_king"

# --- 4. لوحة التحكم (Admin) ---
if is_admin:
    st.title("⚙️ لوحة التحكم - SM KHADAMATIC")
    tabs = st.tabs(["📦 المنتجات", "🚚 الموصلين", "👥 البائعين", "📊 السجلات"])

    with tabs[0]: # إدارة المنتجات
        st.subheader("إضافة منتج جديد")
        with st.form("admin_p_form", clear_on_submit=True):
            n = st.text_input("اسم المنتج")
            p = st.number_input("السعر للكيلو", 0)
            cat = st.selectbox("التصنيف", st.session_state.db["categories"])
            s_list = [s['name'] for s in st.session_state.db['sellers']]
            sel = st.selectbox("البائع التابع له", s_list if s_list else ["لا يوجد بائع"])
            img_file = st.file_uploader("صورة المنتج", type=['png','jpg','jpeg'])
            if st.form_submit_button("حفظ المنتج ✅"):
                img_data = base64.b64encode(img_file.read()).decode() if img_file else ""
                st.session_state.db["products"].append({"name": n, "price": p, "cat": cat, "seller": sel, "img": img_data})
                save_db(st.session_state.db); st.rerun()
        
        st.divider()
        for i, pr in enumerate(st.session_state.db["products"]):
            c1, c2, c3 = st.columns([1, 4, 1])
            if pr.get("img"): c1.image(base64.b64decode(pr["img"]), width=50)
            c2.write(f"**{pr['name']}** | {pr['price']} دج | {pr['cat']}")
            if c3.button("حذف", key=f"del_p_{i}"):
                st.session_state.db["products"].pop(i); save_db(st.session_state.db); st.rerun()

    with tabs[1]: # إدارة الموصلين
        st.subheader("إدارة الموصلين")
        with st.form("add_driver_form"):
            dn = st.text_input("اسم الموصل"); dp = st.text_input("رقم الهاتف (مثال: 213xxxxxxxxx)")
            if st.form_submit_button("إضافة 🚚"):
                st.session_state.db["drivers"].append({"name": dn, "phone": dp, "status": "متاح"})
                save_db(st.session_state.db); st.rerun()
        for i, d in enumerate(st.session_state.db["drivers"]):
            c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
            c1.write(f"🚚 {d['name']}")
            color = "green" if d.get('status') == "متاح" else "red"
            c2.markdown(f"<span style='color:{color}'>{d.get('status', 'متاح')}</span>", unsafe_allow_html=True)
            if c3.button("🔄", key=f"tog_{i}"):
                st.session_state.db["drivers"][i]["status"] = "مشغول" if d.get('status') == "متاح" else "متاح"
                save_db(st.session_state.db); st.rerun()
            if c4.button("🗑️", key=f"ddel_{i}"):
                st.session_state.db["drivers"].pop(i); save_db(st.session_state.db); st.rerun()

    with tabs[2]: # إدارة البائعين
        st.subheader("إدارة البائعين")
        with st.form("add_seller_form"):
            sn = st.text_input("اسم البائع"); sp = st.text_input("رقم الهاتف")
            if st.form_submit_button("إضافة بائع 👥"):
                st.session_state.db["sellers"].append({"name": sn, "phone": sp})
                save_db(st.session_state.db); st.rerun()
        for i, s in enumerate(st.session_state.db["sellers"]):
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.write(f"👤 {s['name']}"); c2.write(f"📞 {s['phone']}")
            if c3.button("حذف", key=f"sdel_{i}"):
                st.session_state.db["sellers"].pop(i); save_db(st.session_state.db); st.rerun()

    with tabs[3]: # السجلات والتقارير
        st.subheader("📊 سجل الطلبات والتقارير")
        if st.session_state.db["orders"]:
            df_orders = pd.DataFrame(st.session_state.db["orders"])
            
            # معالجة الكميات للتجميع
            all_items = []
            if 'details' in df_orders.columns:
                for detail in df_orders['details'].fillna(""):
                    parts = str(detail).split(", ")
                    for p in parts:
                        if "(" in p:
                            try:
                                name_part = p.split(" (")[0]
                                qty_part = float(p.split("(")[1].replace("كغ)", ""))
                                all_items.append({"المنتج": name_part, "الكمية الكلية": qty_part})
                            except: pass

            # أزرار تحميل Excel
            if all_items:
                df_summary = pd.DataFrame(all_items).groupby("المنتج").sum().reset_index()
                c_ex1, c_ex2 = st.columns(2)
                with c_ex1:
                    try:
                        buf1 = io.BytesIO()
                        with pd.ExcelWriter(buf1, engine='xlsxwriter') as wr: df_orders.to_excel(wr, index=False)
                        st.download_button("📥 سجل الطلبات (Excel)", buf1.getvalue(), "orders.xlsx")
                    except: st.error("يرجى إضافة xlsxwriter لملف requirements.txt")
                with c_ex2:
                    try:
                        buf2 = io.BytesIO()
                        with pd.ExcelWriter(buf2, engine='xlsxwriter') as wr: df_summary.to_excel(wr, index=False)
                        st.download_button("📊 المشتريات المجتمعة (Excel)", buf2.getvalue(), "summary.xlsx")
                    except: pass

            st.dataframe(df_orders, use_container_width=True)
            if st.button("🗑️ مسح السجلات تماماً"):
                st.session_state.db["orders"] = []; save_db(st.session_state.db); st.rerun()
        else:
            st.info("لا توجد طلبات مسجلة بعد.")

# --- 5. واجهة الزبائن ---
else:
    st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)
    
    # البحث والتصنيفات
    search_q = st.text_input("🔍 ابحث عن منتج...", "").lower()
    cat_list = ["الكل"] + st.session_state.db["categories"]
    c_btns = st.columns(len(cat_list))
    for i, cat in enumerate(cat_list):
        if c_btns[i].button(cat, key=f"c_{cat}", use_container_width=True):
            st.session_state.selected_cat = cat; st.rerun()

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
                    if p.get("img"): st.markdown(f'<img src="data:image/png;base64,{p["img"]}" class="product-img">', unsafe_allow_html=True)
                    st.subheader(p['name'])
                    st.markdown(f'<p class="price-text">{p["price"]} دج</p>', unsafe_allow_html=True)
                    q = st.number_input("الكمية", 0.1, 100.0, 1.0, 0.5, key=f"q_{p['name']}_{i+j}")
                    if st.button("إضافة 🛒", key=f"a_{p['name']}_{i+j}"):
                        st.session_state.cart.append({"name": p['name'], "price": p['price']*q, "qty": q, "seller": p['seller']})
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    with col_cart:
        st.subheader("🛒 سلتك")
        total = 0
        if not st.session_state.cart: st.info("السلة فارغة")
        else:
            sum_dict = {}
            for item in st.session_state.cart:
                n = item['name']
                if n in sum_dict:
                    sum_dict[n]['qty'] += item['qty']; sum_dict[n]['tp'] += item['price']
                else: sum_dict[n] = {'qty': item['qty'], 'tp': item['price'], 's': item['seller']}
                total += item['price']

            for n, info in sum_dict.items():
                c1, c2, c3 = st.columns([2, 1, 0.5])
                c1.write(f"**{n}**"); c2.write(f"{info['qty']} كغ")
                if c3.button("❌", key=f"r_{n}"):
                    st.session_state.cart = [x for x in st.session_state.cart if x['name'] != n]; st.rerun()
            
            st.divider()
            st.write(f"### المجموع: {int(total)} دج")
            
            with st.form("order_form"):
                u_name = st.text_input("الاسم")
                u_phone = st.text_input("الهاتف")
                u_addr = st.text_area("العنوان بالتفصيل")
                drivers = [d for d in st.session_state.db["drivers"] if d.get("status") == "متاح"]
                # ابحث عن هذا السطر في كودك وحدثه:
                sel_d = st.selectbox("✨ اختر الموصل المتاح:", [f"🚚 {d['name']}" for d in drivers]) if drivers else "لا يوجد موصل حالياً"
                
                if st.form_submit_button("✅ إرسال الطلب"):
                    if u_name and u_phone and drivers:
                        d_info = next(d for d in drivers if d["name"] == sel_d)
                        dtls = ", ".join([f"{n} ({inf['qty']}كغ)" for n, inf in sum_dict.items()])
                        st.session_state.db["orders"].append({"name": u_name, "phone": u_phone, "total": int(total), "date": datetime.now().strftime("%Y-%m-%d %H:%M"), "details": dtls})
                        save_db(st.session_state.db)
                        
                        msg = f"طلب جديد من: {u_name}\nالهاتف: {u_phone}\nالعنوان: {u_addr}\nالمنتجات: {dtls}\nالمجموع: {int(total)} دج"
                        encoded_msg = urllib.parse.quote(msg)
                        
                        st.success("تم تسجيل طلبك بنجاح!")
                        st.markdown(f'<a href="https://wa.me/{d_info["phone"]}?text={encoded_msg}" target="_blank" style="background:#006341;color:white;display:block;text-align:center;padding:12px;border-radius:10px;text-decoration:none;font-weight:bold;">مراسلة الموصل عبر واتساب 🚚</a>', unsafe_allow_html=True)
                        st.session_state.cart = []
                    else: st.error("يرجى ملء كافة البيانات وتوفر موصل")



