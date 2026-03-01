import streamlit as st
import json
import os
import urllib.parse
import pandas as pd
from datetime import datetime
from io import BytesIO

# 1. إعدادات الصفحة الاحترافية (SM KhadamaTic)
st.set_page_config(page_title="SM KhadamaTic", layout="wide")

# 2. التنسيق (Style) - محاكاة METRO مريح للعين ومتوافق مع الهاتف
st.markdown("""
<style>
    .stApp { background-color: #F8F9FA; color: #333; }
    .main-title { color: #006341; text-align: center; font-size: clamp(24px, 5vw, 40px); font-weight: bold; margin: 20px 0; }
    .product-card {
        background-color: white; padding: 15px; border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center;
        border: 1px solid #EEE; margin-bottom: 15px;
    }
    .price-text { color: #006341; font-weight: bold; font-size: 1.2em; }
    div.stButton > button { 
        background-color: #006341 !important; color: white !important; 
        border-radius: 8px; width: 100%; font-weight: bold; height: 45px;
    }
    /* إخفاء القائمة الجانبية تماماً عن الزبائن */
    [data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# 3. إدارة البيانات
DB_FILE = "khadamatict_db.json"
ADMIN_KEY = "tarek_admin" # الكلمة السرية للرابط

def load_data():
    base = {"products": [], "categories": ["خضروات", "فواكه", "عروض"], 
            "delivery_fees": {"باتنة": 200, "الجزائر": 500}, "orders": []}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return base
    return base

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if 'db' not in st.session_state: st.session_state.db = load_data()
if 'cart' not in st.session_state: st.session_state.cart = {}

# التحقق من "رابط الإدارة السري"
query_params = st.query_params
is_admin = query_params.get("view") == ADMIN_KEY

# --- واجهة المتجر (للزوار) ---
if not is_admin:
    st.markdown("<div class='main-title'>SM KhadamaTic</div>", unsafe_allow_html=True)
    
    col_main, col_cart = st.columns([2, 1])
    
    with col_main:
        selected_cat = st.selectbox("اختر القسم:", ["الكل"] + st.session_state.db['categories'])
        prods = [p for p in st.session_state.db['products'] if selected_cat == "الكل" or p.get('category') == selected_cat]
        
        # شبكة المنتجات (تلقائية التوزيع للموبايل والكمبيوتر)
        rows = [prods[i:i + 2] for i in range(0, len(prods), 2)]
        for row in rows:
            cols = st.columns(2)
            for idx, p in enumerate(row):
                with cols[idx]:
                    st.markdown(f"""
                    <div class='product-card'>
                        <h4>{p['name']}</h4>
                        <p class='price-text'>{p['price']} دج</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"أضف للسلة 🛒", key=f"add_{p['name']}"):
                        st.session_state.cart[p['name']] = st.session_state.cart.get(p['name'], 0) + 1
                        st.rerun()

    with col_cart:
        st.subheader("🛒 سلة الطلبات")
        total_items = 0
        order_details = ""
        for n, q in list(st.session_state.cart.items()):
            if q > 0:
                p_info = next(x for x in st.session_state.db['products'] if x['name'] == n)
                total_items += q * p_info['price']
                st.write(f"✅ {n} (x{q})")
                order_details += f"- {n} (x{q}) = {q*p_info['price']} دج\n"
                if st.button(f"حذف {n}", key=f"del_{n}"):
                    st.session_state.cart[n] = 0
                    st.rerun()
        
        if total_items > 0:
            st.divider()
            reg = st.selectbox("منطقة التوصيل:", list(st.session_state.db['delivery_fees'].keys()))
            fee = st.session_state.db['delivery_fees'][reg]
            grand_total = total_items + fee
            st.markdown(f"### الإجمالي: {grand_total} دج")
            
            # معلومات الزبون
            u_name = st.text_input("الاسم الكامل:")
            u_phone = st.text_input("رقم الهاتف:")
            u_address = st.text_area("العنوان بالتفصيل:")
            
            if st.button("إرسال الطلب عبر واتساب 📲"):
                if u_name and u_phone and u_address:
                    # حفظ في السجل
                    new_order = {
                        "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "الزبون": u_name, "الهاتف": u_phone, "العنوان": u_address,
                        "المنطقة": reg, "المجموع": grand_total, "الطلبات": order_details
                    }
                    st.session_state.db['orders'].append(new_order)
                    save_data(st.session_state.db)
                    
                    # رابط الواتساب
                    full_msg = f"📢 *طلب جديد من SM KhadamaTic*\n\n👤 الزبون: {u_name}\n📞 الهاتف: {u_phone}\n📍 العنوان: {u_address}\n🚚 المنطقة: {reg}\n\n📦 الطلبات:\n{order_details}\n💰 *الإجمالي النهائي: {grand_total} دج*"
                    wa_url = f"https://wa.me/213770000000?text={urllib.parse.quote(full_msg)}"
                    st.markdown(f'<meta http-equiv="refresh" content="0;url={wa_url}">', unsafe_allow_html=True)
                    st.success("جاري تحويلك للواتساب...")
                else:
                    st.warning("مولاي، يرجى ملء كل المعلومات أولاً!")

# --- لوحة التحكم (مخفية - تظهر فقط بالرابط السري) ---
else:
    st.title("🛠 لوحة تحكم مولاي طارق")
    tab1, tab2, tab3 = st.tabs(["📦 المنتجات", "📍 التوصيل", "📊 سجل المبيعات"])
    
    with tab1:
        with st.form("p_form"):
            n = st.text_input("اسم المنتج")
            p = st.number_input("السعر", min_value=0)
            c = st.selectbox("القسم", st.session_state.db['categories'])
            if st.form_submit_button("إضافة"):
                st.session_state.db['products'].append({"name": n, "price": p, "category": c})
                save_data(st.session_state.db)
                st.rerun()

    with tab3:
        if st.session_state.db['orders']:
            df = pd.DataFrame(st.session_state.db['orders'])
            st.dataframe(df)
            
            # زر التصدير لإكسل (Export to Excel)
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Orders')
            
            st.download_button(
                label="📥 تحميل السجل كملف Excel",
                data=output.getvalue(),
                file_name=f"orders_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("لا توجد طلبات في السجل بعد.")
