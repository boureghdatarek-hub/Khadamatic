import streamlit as st
import json, os, base64
import urllib.parse
from datetime import datetime

# --- 1. إعدادات الصفحة والتنسيق (CSS) ---
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

st.markdown("""
<style>
    .product-img { width: 100%; height: 150px; object-fit: contain; background-color: white; margin-bottom: 10px; }
    .product-card { background: white; padding: 15px; border-radius: 12px; border: 1px solid #eee; text-align: center; margin-bottom: 20px; }
    .price-text { color: #006341; font-weight: bold; font-size: 1.2rem; }
    .stButton > button { border-radius: 20px; border: 1px solid #006341; background-color: white; color: #006341; }
    .stButton > button:hover { background-color: #006341; color: white; }
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
if 'quantities' not in st.session_state: st.session_state.quantities = {}

# --- 3. تحديد الصلاحيات ---
is_admin = st.query_params.get("view") == "tarek_king"

# --- لوحة التحكم ---
if is_admin:
    st.title("⚙️ لوحة التحكم - SM KHADAMATIC")
    tabs = st.tabs(["📦 المنتجات", "🚚 الموصلين", "👥 البائعين", "📊 السجلات"])

    with tabs[0]:
        st.subheader("إضافة منتج جديد")
        with st.form("admin_p_form", clear_on_submit=True):
            n = st.text_input("اسم المنتج")
            p = st.number_input("السعر", 0)
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
            c2.write(f"**{pr['name']}** | {pr['price']} دج | البائع: {pr['seller']}")
            if c3.button("حذف", key=f"del_p_{i}"):
                st.session_state.db["products"].pop(i); save_db(st.session_state.db); st.rerun()

    with tabs[1]:
        st.subheader("إدارة الموصلين")
        with st.form("add_driver_form"):
            dn = st.text_input("اسم الموصل"); dp = st.text_input("رقم الهاتف")
            if st.form_submit_button("إضافة 🚚"):
                st.session_state.db["drivers"].append({"name": dn, "phone": dp, "status": "متاح"})
                save_db(st.session_state.db); st.rerun()
        for i, d in enumerate(st.session_state.db["drivers"]):
            c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
            c1.write(f"🚚 {d['name']}")
            color = "green" if d.get('status') == "متاح" else "red"
            c2.markdown(f"<span style='color:{color}'>{d.get('status', 'متاح')}</span>", unsafe_allow_html=True)
            if c3.button("تبديل الحالة", key=f"tog_{i}"):
                st.session_state.db["drivers"][i]["status"] = "مشغول" if d.get('status') == "متاح" else "متاح"
                save_db(st.session_state.db); st.rerun()
            if c4.button("حذف", key=f"ddel_{i}"):
                st.session_state.db["drivers"].pop(i); save_db(st.session_state.db); st.rerun()

    with tabs[2]:
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
    
    with tabs[3]:
        st.subheader("📊 السجلات")
        st.write(st.session_state.db["orders"])

# --- 4. واجهة الزبائن ---
else:
    st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)
    cat_list = ["الكل"] + st.session_state.db["categories"]
    cat_cols = st.columns(len(cat_list))
    for i, category in enumerate(cat_list):
        if cat_cols[i].button(category, key=f"cat_btn_{category}", use_container_width=True):
            st.session_state.selected_cat = category; st.rerun()

    st.divider()
    col_main, col_cart = st.columns([3, 1.8]) 
    
    with col_main:
        prods = st.session_state.db["products"]
        if st.session_state.selected_cat != "الكل": prods = [p for p in prods if p.get("cat") == st.session_state.selected_cat]
        for i in range(0, len(prods), 3):
            grid_cols = st.columns(3)
            for j, p in enumerate(prods[i:i+3]):
                with grid_cols[j]:
                    st.markdown('<div class="product-card">', unsafe_allow_html=True)
                    if p.get("img"): st.markdown(f'<img src="data:image/png;base64,{p["img"]}" class="product-img">', unsafe_allow_html=True)
                    st.subheader(p['name']); st.markdown(f'<p class="price-text">{p["price"]} دج</p>', unsafe_allow_html=True)
                    if st.button("إضافة للسلة 🛒", key=f"btn_add_{i+j}"):
                        st.session_state.cart.append(p); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    with col_cart:
        st.subheader("🛒 سلتك المجمعة")
        total = 0
        if not st.session_state.cart: 
            st.write("السلة فارغة")
        else:
            summary_dict = {}
            for idx, item in enumerate(st.session_state.cart):
                name = item['name']
                price = item['price']
                # حساب الكمية (افتراضياً 1 إذا لم تحدد)
                qty_val = 1.0
                
                if name in summary_dict:
                    summary_dict[name]['qty'] += qty_val
                    summary_dict[name]['total_price'] += price
                else:
                    summary_dict[name] = {'qty': qty_val, 'total_price': price, 'seller': item['seller']}
                total += price

            for name, info in summary_dict.items():
                c1, c2, c3 = st.columns([2, 1.5, 0.5])
                c1.write(f"**{name}** ({info['total_price']} دج)")
                c2.write(f"الكمية: {int(info['qty'])} كغ")
                if c3.button("❌", key=f"del_{name}"):
                    st.session_state.cart = [x for x in st.session_state.cart if x['name'] != name]
                    st.rerun()
            
            st.divider()
            st.write(f"### المجموع: {total} دج")

            # --- هنا التعديل الجوهري باستخدام Form لضمان قراءة البيانات ---
            with st.form("order_submission_form", clear_on_submit=False):
                c_name = st.text_input("اسمك")
                c_phone = st.text_input("هاتفك")
                c_addr = st.text_area("العنوان")
                
                drivers = [d for d in st.session_state.db["drivers"] if d.get("status") == "متاح"]
                sel_driver = None
                if drivers:
                    sel_driver = st.selectbox("الموصل", [d["name"] for d in drivers])
                
                submit_order = st.form_submit_button("✅ تأكيد وإرسال الطلب")

                if submit_order:
                    if c_name and c_phone and c_addr:
                        if drivers:
                            d_info = next(d for d in drivers if d["name"] == sel_driver)
                            msg = f"طلب جديد: {c_name}\nالهاتف: {c_phone}\nالعنوان: {c_addr}\nالمجموع: {total} دج\nالمنتجات:\n"
                            for n, inf in summary_dict.items():
                                msg += f"- {n} {int(inf['qty'])} كغ\n"
                            
                            encoded_msg = urllib.parse.quote(msg)
                            st.success("✅ تم تجهيز روابط الواتساب!")
                            
                            # عرض أزرار التواصل
                            st.markdown(f'<a href="https://wa.me/{d_info["phone"]}?text={encoded_msg}" target="_blank" style="background-color: #006341; color: white; padding: 12px; text-decoration: none; display: block; text-align: center; border-radius: 8px; margin-bottom: 10px; font-weight: bold;">إرسال للموصل 🚚</a>', unsafe_allow_html=True)
                            
                            sellers_in_cart = list(set([inf['seller'] for inf in summary_dict.values()]))
                            for s_name in sellers_in_cart:
                                s_info = next((s for s in st.session_state.db["sellers"] if s["name"] == s_name), None)
                                if s_info:
                                    st.markdown(f'<a href="https://wa.me/{s_info["phone"]}?text={encoded_msg}" target="_blank" style="background-color: #25D366; color: white; padding: 12px; text-decoration: none; display: block; text-align: center; border-radius: 8px; margin-bottom: 5px; font-weight: bold;">إرسال للبائع ({s_name}) 👤</a>', unsafe_allow_html=True)
                            
                            # حفظ الطلب في السجل
                            st.session_state.db["orders"].append({"name": c_name, "total": total, "date": str(datetime.now())})
                            save_db(st.session_state.db)
                        else:
                            st.error("⚠️ لا يوجد موصل متاح حالياً")
                    else:
                        st.error("⚠️ يرجى ملء الاسم والهاتف والعنوان")