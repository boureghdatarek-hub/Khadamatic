import streamlit as st
import json, os, base64
import urllib.parse
import pandas as pd
from datetime import datetime
import io

# --- 1. إعدادات الصفحة والتنسيق (CSS المحسن للهاتف والـ Dark Mode) ---
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

st.markdown("""
<style>
    /* تثبيت ألوان الخلفية والنصوص لمنع مشاكل الـ Dark Mode */
    .stApp {
        background-color: #f9f9f9;
        color: #333333;
    }
    
    /* تنسيق كروت المنتجات لتكون واضحة جداً في الهاتف */
    .product-card { 
        background: white !important; 
        padding: 15px; 
        border-radius: 15px; 
        border: 1px solid #ddd; 
        text-align: center; 
        margin-bottom: 20px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
    }
    
    .product-img { 
        width: 100%; 
        height: 150px; 
        object-fit: contain; 
        background-color: white; 
        margin-bottom: 10px; 
        border-radius: 10px;
    }

    /* تحسين شكل الأزرار لتكون أنيقة في الهاتف */
    .stButton > button { 
        border-radius: 25px !important; 
        border: 2px solid #006341 !important; 
        background-color: white !important; 
        color: #006341 !important; 
        font-weight: bold !important;
        width: 100%;
        transition: 0.3s;
    }
    
    .stButton > button:hover { 
        background-color: #006341 !important; 
        color: white !important; 
    }

    /* نصوص الأسعار */
    .price-text { 
        color: #006341 !important; 
        font-weight: bold; 
        font-size: 1.3rem; 
        margin: 10px 0;
    }

    /* تحسين العناوين لتظهر بوضوح في كل الأوضاع */
    h1, h2, h3, p, span, label {
        color: #1a1a1a !important;
    }

    /* تنسيق خاص لحقول الإدخال لتجنب اختفائها في الوضع الليلي */
    input, textarea, select {
        background-color: white !important;
        color: black !important;
        border: 1px solid #ccc !important;
    }
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

# --- 3. تحديد الصلاحيات ---
is_admin = st.query_params.get("view") == "tarek_king"

# --- 4. لوحة التحكم (Admin) ---
if is_admin:
    st.title("⚙️ لوحة التحكم - SM KHADAMATIC")
    tabs = st.tabs(["📦 المنتجات", "🚚 الموصلين", "👥 البائعين", "📊 السجلات"])

    with tabs[0]: # المنتجات
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
            c2.write(f"**{pr['name']}** | {pr['price']} دج | البائع: {pr['seller']}")
            if c3.button("حذف", key=f"del_p_{i}"):
                st.session_state.db["products"].pop(i); save_db(st.session_state.db); st.rerun()

    with tabs[1]: # الموصلين
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

    with tabs[2]: # البائعين
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

    with tabs[3]: # السجلات مع ميزة التجميع و Excel
        st.subheader("📊 سجل الطلبات المستلمة")
        if st.session_state.db["orders"]:
            df_orders = pd.DataFrame(st.session_state.db["orders"])
            
            # --- ميزة التقرير التجميعي Excel ---
            all_items = []
            for detail in df_orders['details']:
                # تفكيك النصوص مثل "تفاح (2كغ), بطاطا (3كغ)"
                parts = detail.split(", ")
                for p in parts:
                    if "(" in p:
                        name_part = p.split(" (")[0]
                        qty_part = float(p.split("(")[1].replace("كغ)", ""))
                        all_items.append({"المنتج": name_part, "الكمية الكلية": qty_part})
            
            df_summary = pd.DataFrame(all_items).groupby("المنتج").sum().reset_index()

            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                # تصدير السجل الكامل
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_orders.to_excel(writer, index=False, sheet_name='الطلبات')
                st.download_button("📥 تحميل سجل الطلبات (Excel)", buffer, "orders_report.xlsx", "application/vnd.ms-excel")
            
            with col_exp2:
                # تصدير المشتريات المجتمعة (طلبك الخاص)
                buffer_sum = io.BytesIO()
                with pd.ExcelWriter(buffer_sum, engine='xlsxwriter') as writer:
                    df_summary.to_excel(writer, index=False, sheet_name='المشتريات المجتمعة')
                st.download_button("📊 تحميل المشتريات المجتمعة (Excel)", buffer_sum, "summary_report.xlsx", "application/vnd.ms-excel")

            st.write("### تفاصيل الطلبات:")
            st.dataframe(df_orders.rename(columns={"name":"الاسم","phone":"الهاتف","total":"المجموع","date":"التاريخ","details":"المنتجات"}), use_container_width=True)
            
            if st.button("🗑️ مسح جميع السجلات"):
                st.session_state.db["orders"] = []
                save_db(st.session_state.db); st.rerun()
        else:
            st.info("لا توجد طلبات مسجلة حتى الآن.")

# --- 5. واجهة الزبائن ---
else:
    st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)
    
    # --- ميزة البحث السريع ---
    search_query = st.text_input("🔍 ابحث عن منتج (مثلاً: طماطم، تفاح...)", "").lower()

    cat_list = ["الكل"] + st.session_state.db["categories"]
    cat_cols = st.columns(len(cat_list))
    for i, category in enumerate(cat_list):
        if cat_cols[i].button(category, key=f"cat_btn_{category}", use_container_width=True):
            st.session_state.selected_cat = category; st.rerun()

    st.divider()
    col_main, col_cart = st.columns([3, 1.8]) 
    
    with col_main:
        prods = st.session_state.db["products"]
        # تصفية حسب القسم والبحث
        if st.session_state.selected_cat != "الكل": 
            prods = [p for p in prods if p.get("cat") == st.session_state.selected_cat]
        if search_query:
            prods = [p for p in prods if search_query in p['name'].lower()]

        for i in range(0, len(prods), 3):
            grid_cols = st.columns(3)
            for j, p in enumerate(prods[i:i+3]):
                with grid_cols[j]:
                    st.markdown('<div class="product-card">', unsafe_allow_html=True)
                    if p.get("img"): st.markdown(f'<img src="data:image/png;base64,{p["img"]}" class="product-img">', unsafe_allow_html=True)
                    st.subheader(p['name']); st.markdown(f'<p class="price-text">{p["price"]} دج / كغ</p>', unsafe_allow_html=True)
                    
                    # --- ميزة تحديد الكمية بدقة ---
                    q_val = st.number_input("الكمية (كغ)", 0.1, 50.0, 1.0, 0.1, key=f"qty_in_{p['name']}_{i+j}")
                    
                    if st.button("إضافة للسلة 🛒", key=f"btn_add_{p['name']}_{i+j}"):
                        # إضافة المنتج مع الكمية المختارة
                        st.session_state.cart.append({"name": p['name'], "price": p['price'] * q_val, "qty": q_val, "seller": p['seller']})
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    with col_cart:
        st.subheader("🛒 سلتك المجمعة")
        total = 0
        if not st.session_state.cart: 
            st.write("السلة فارغة")
        else:
            summary_dict = {}
            for item in st.session_state.cart:
                name = item['name']
                if name in summary_dict:
                    summary_dict[name]['qty'] += item['qty']
                    summary_dict[name]['total_price'] += item['price']
                else:
                    summary_dict[name] = {'qty': item['qty'], 'total_price': item['price'], 'seller': item['seller']}
                total += item['price']

            for name, info in summary_dict.items():
                c1, c2, c3 = st.columns([2, 1.5, 0.5])
                c1.write(f"**{name}**")
                c2.write(f"{info['qty']:.1f} كغ")
                if c3.button("❌", key=f"del_{name}"):
                    st.session_state.cart = [x for x in st.session_state.cart if x['name'] != name]
                    st.rerun()
            
            st.divider()
            st.write(f"### المجموع: {int(total)} دج")

            with st.form("order_submission_form"):
                c_name = st.text_input("اسمك")
                c_phone = st.text_input("رقم هاتفك")
                c_addr = st.text_area("عنوان التوصيل")
                drivers = [d for d in st.session_state.db["drivers"] if d.get("status") == "متاح"]
                sel_driver = st.selectbox("اختر الموصل", [d["name"] for d in drivers]) if drivers else "لا يوجد موصل"
                
                if st.form_submit_button("✅ تأكيد وإرسال الطلب"):
                    if c_name and c_phone and c_addr and drivers:
                        d_info = next(d for d in drivers if d["name"] == sel_driver)
                        details_text = ", ".join([f"{n} ({inf['qty']:.1f}كغ)" for n, inf in summary_dict.items()])
                        
                        st.session_state.db["orders"].append({
                            "name": c_name, "phone": c_phone, "total": int(total),
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"), "details": details_text
                        })
                        save_db(st.session_state.db)

                        msg = f"طلب جديد: {c_name}\nالهاتف: {c_phone}\nالعنوان: {c_addr}\nالمجموع: {int(total)} دج\nالمنتجات: {details_text}"
                        encoded_msg = urllib.parse.quote(msg)
                        
                        st.success("✅ تم تسجيل الطلب!")
                        st.markdown(f'<a href="https://wa.me/{d_info["phone"]}?text={encoded_msg}" target="_blank" style="background-color: #006341; color: white; padding: 12px; text-decoration: none; display: block; text-align: center; border-radius: 8px; margin-bottom: 10px; font-weight: bold;">إرسال للموصل 🚚</a>', unsafe_allow_html=True)
                        
                        sellers_in_cart = set([inf['seller'] for inf in summary_dict.values()])
                        for s_name in sellers_in_cart:
                            s_info = next((s for s in st.session_state.db["sellers"] if s["name"] == s_name), None)
                            if s_info:
                                st.markdown(f'<a href="https://wa.me/{s_info["phone"]}?text={encoded_msg}" target="_blank" style="background-color: #25D366; color: white; padding: 12px; text-decoration: none; display: block; text-align: center; border-radius: 8px; margin-bottom: 5px; font-weight: bold;">إرسال للبائع ({s_name}) 👤</a>', unsafe_allow_html=True)
                    else:
                        st.error("⚠️ تأكد من ملء البيانات وتوفر الموصلين")
