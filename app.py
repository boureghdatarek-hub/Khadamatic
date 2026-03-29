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
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {"products": [], "drivers": [], "sellers": [], "orders": [], "categories": ["خضر", "فواكه", "عروض"]}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

if 'db' not in st.session_state: st.session_state.db = load_db()
if 'cart' not in st.session_state: st.session_state.cart = []
if 'selected_cat' not in st.session_state: st.session_state.selected_cat = "الكل"

# --- 3. تحديد الصلاحيات (الرابط السري) ---
# لفتح الإدارة يجب إضافة ?admin=true في نهاية الرابط
is_admin_mode = st.query_params.get("admin") == "true"

# --- 4. لوحة التحكم (تظهر فقط عند استخدام الرابط السري + كلمة السر) ---
if is_admin_mode:
    st.sidebar.title("🔐 دخول الإدارة")
    admin_password = st.sidebar.text_input("أدخل كلمة المرور السرية", type="password")
    
    if admin_password == "tarek2026":
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

        with tabs[3]: # السجلات
            st.subheader("📊 سجل الطلبات")
            if st.session_state.db["orders"]:
                df_orders = pd.DataFrame(st.session_state.db["orders"])
                st.dataframe(df_orders, use_container_width=True)
                if st.button("🗑️ مسح السجلات تماماً"):
                    st.session_state.db["orders"] = []; save_db(st.session_state.db); st.rerun()
            else: st.info("لا توجد طلبات.")
    else:
        st.sidebar.warning("يرجى إدخال كلمة المرور للوصول للإدارة")
        # عرض الواجهة العادية للزبائن حتى لو استخدم الرابط السري (لحماية الشكل)
        st.info("أنت في وضع الإدارة السري. أدخل كلمة المرور في الجانب.")

# --- 5. واجهة الزبائن (تظهر للجميع دائماً) ---
if not is_admin_mode or (is_admin_mode and admin_password != "tarek2026"):
    st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)
    
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
                driver_names = [d['name'] for d in drivers]
                sel_d = st.selectbox("🚚 اختر الموصل المتاح:", driver_names) if drivers else "لا يوجد موصل"
                
                if st.form_submit_button("✅ إرسال الطلب"):
                    if u_name and u_phone and drivers:
                        d_info = next(d for d in drivers if d["name"] == sel_d)
                        dtls = ", ".join([f"{n} ({inf['qty']}كغ)" for n, inf in sum_dict.items()])
                        st.session_state.db["orders"].append({
                            "name": u_name, "phone": u_phone, "total": int(total), 
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"), "details": dtls
                        })
                        save_db(st.session_state.db)
                        msg = f"طلب جديد من: {u_name}\nالهاتف: {u_phone}\nالعنوان: {u_addr}\nالمنتجات: {dtls}\nالمجموع: {int(total)} دج"
                        encoded_msg = urllib.parse.quote(msg)
                        st.success("تم تسجيل طلبك بنجاح!")
                        st.markdown(f'<a href="https://wa.me/{d_info["phone"]}?text={encoded_msg}" target="_blank" style="background:#006341;color:white;display:block;text-align:center;padding:12px;border-radius:10px;text-decoration:none;font-weight:bold;">مراسلة الموصل عبر واتساب 🚚</a>', unsafe_allow_html=True)
                        st.session_state.cart = []
                    else: st.error("يرجى ملء كافة البيانات وتوفر موصل")
