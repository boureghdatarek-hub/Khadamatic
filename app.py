import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import base64
import urllib.parse
from datetime import datetime

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

# رابط الجدول الخاص بك
SHEET_URL = "https://docs.google.com/spreadsheets/d/15R1XMLD-8FGG-WIsXM1PZ0JLTceGIJyjNIHgb_uNOZk/edit?usp=sharing"

# الاتصال بـ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data(worksheet):
    try:
        return conn.read(spreadsheet=SHEET_URL, worksheet=worksheet)
    except:
        # إذا كانت الصفحة فارغة، ننشئ أعمدة افتراضية
        if worksheet == "products": return pd.DataFrame(columns=["name", "price", "cat", "img"])
        if worksheet == "drivers": return pd.DataFrame(columns=["name", "phone", "status"])
        if worksheet == "orders": return pd.DataFrame(columns=["الزبون", "الهاتف", "المنتجات", "المجموع", "التاريخ"])

# تحميل البيانات في الـ session_state
if 'products_df' not in st.session_state: st.session_state.products_df = load_data("products")
if 'drivers_df' not in st.session_state: st.session_state.drivers_df = load_data("drivers")
if 'cart' not in st.session_state: st.session_state.cart = {}

# --- 2. التحقق من الإدارة ---
is_admin = st.query_params.get("admin") == "true"

if is_admin:
    pwd = st.sidebar.text_input("كلمة المرور", type="password")
    if pwd == "tarek2026":
        st.title("⚙️ إدارة SM KHADAMATIC")
        t1, t2, t3 = st.tabs(["📦 المنتجات", "🚚 الموصلين", "📊 السجلات"])
        
        with t1: # إضافة منتج وحفظه في جوجل
            with st.form("add_p", clear_on_submit=True):
                n = st.text_input("اسم المنتج")
                p = st.number_input("السعر", 0)
                cat = st.selectbox("التصنيف", ["خضر", "فواكه", "عروض"])
                img = st.file_uploader("الصورة")
                if st.form_submit_button("حفظ في جوجل ✅"):
                    img_data = base64.b64encode(img.read()).decode() if img else ""
                    new_p = pd.DataFrame([{"name": n, "price": p, "cat": cat, "img": img_data}])
                    updated_df = pd.concat([st.session_state.products_df, new_p], ignore_index=True)
                    conn.update(spreadsheet=SHEET_URL, worksheet="products", data=updated_df)
                    st.session_state.products_df = updated_df
                    st.success("تم الحفظ في Google Sheets!"); st.rerun()

        with t2: # إدارة الموصلين
            with st.form("add_d"):
                dn = st.text_input("اسم الموصل"); dp = st.text_input("الواتساب (213...)")
                if st.form_submit_button("إضافة موصل 🚚"):
                    new_d = pd.DataFrame([{"name": dn, "phone": dp, "status": "متاح"}])
                    updated_df = pd.concat([st.session_state.drivers_df, new_d], ignore_index=True)
                    conn.update(spreadsheet=SHEET_URL, worksheet="drivers", data=updated_df)
                    st.session_state.drivers_df = updated_df
                    st.rerun()

# --- 3. واجهة الزبائن ---
if not is_admin or (is_admin and pwd != "tarek2026"):
    st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)
    
    col_main, col_cart = st.columns([3, 1.8])
    
    with col_main:
        df = st.session_state.products_df
        if not df.empty:
            for i in range(0, len(df), 3):
                grid = st.columns(3)
                for j, row in df.iloc[i:i+3].iterrows():
                    with grid[j % 3]:
                        st.markdown(f'<div style="border:1px solid #ddd; padding:10px; border-radius:15px; text-align:center;">', unsafe_allow_html=True)
                        if row['img']: st.markdown(f'<img src="data:image/png;base64,{row["img"]}" style="width:100%; height:100px; object-fit:contain;">', unsafe_allow_html=True)
                        st.write(f"**{row['name']}**")
                        st.write(f"{row['price']} دج")
                        qty = st.number_input("الكمية", 0.5, 20.0, 1.0, 0.5, key=f"q_{j}")
                        if st.button("إضافة 🛒", key=f"b_{j}"):
                            if row['name'] in st.session_state.cart: st.session_state.cart[row['name']]['qty'] += qty
                            else: st.session_state.cart[row['name']] = {'price': row['price'], 'qty': qty}
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

    with col_cart:
        st.subheader("🛒 السلة")
        total = 0
        summary = []
        for name, info in st.session_state.cart.items():
            sub = info['price'] * info['qty']
            total += sub
            st.write(f"**{name}**: {info['qty']} كغ")
            summary.append(f"{name} ({info['qty']} كغ)")
        
        if total > 0:
            st.write(f"### المجموع: {int(total)} دج")
            with st.form("checkout"):
                un = st.text_input("الاسم"); up = st.text_input("الهاتف")
                drivers = st.session_state.db["drivers"] if 'db' in st.session_state else [] # fallback
                # استخدام الموصلين من جوجل شيت
                d_list = st.session_state.drivers_df['name'].tolist() if not st.session_state.drivers_df.empty else []
                sel_d = st.selectbox("الموصل", d_list)
                
                if st.form_submit_button("تأكيد الطلب 🚀"):
                    d_phone = st.session_state.drivers_df[st.session_state.drivers_df['name']==sel_d]['phone'].iloc[0]
                    items_txt = " + ".join(summary)
                    msg = f"طلب من: {un}\n🛍️: {items_txt}\n💰: {int(total)} دج"
                    
                    # حفظ الطلب في جوجل شيت
                    new_order = pd.DataFrame([{"الزبون": un, "الهاتف": up, "المنتجات": items_txt, "المجموع": total, "التاريخ": datetime.now()}])
                    conn.update(spreadsheet=SHEET_URL, worksheet="orders", data=pd.concat([load_data("orders"), new_order]))
                    
                    st.markdown(f'<a href="https://wa.me/{d_phone}?text={urllib.parse.quote(msg)}" target="_blank" style="background:green;color:white;display:block;text-align:center;padding:10px;border-radius:10px;text-decoration:none;">واتساب الموصل</a>', unsafe_allow_html=True)
                    st.session_state.cart = {}
