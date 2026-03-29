import streamlit as st
import pandas as pd
import urllib.parse

# --- إعدادات الصفحة ---
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

# الرابط المباشر للجدول بصيغة CSV لضمان استقرار القراءة
SHEET_BASE = "https://docs.google.com/spreadsheets/d/15R1XMLD-8FGG-WIsXM1PZ0JLTceGIJyjNIHgb_uNOZk/gviz/tq?tqx=out:csv"

def load_sheet(sheet_name):
    try:
        url = f"{SHEET_BASE}&sheet={sheet_name}"
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

# تحميل البيانات
prods_df = load_sheet("products")
drivers_df = load_sheet("drivers")

if 'cart' not in st.session_state: st.session_state.cart = {}

st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .product-box { background: white; padding: 20px; border-radius: 20px; border: 1px solid #eee; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
    .price-tag { color: #006341; font-weight: bold; font-size: 1.4rem; margin: 10px 0; }
    .stButton > button { border-radius: 30px !important; border: 2px solid #006341 !important; color: #006341 !important; font-weight: bold !important; }
    .stButton > button:hover { background-color: #006341 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)

# التحقق من وجود بيانات
if prods_df.empty:
    st.warning("⚠️ يرجى التأكد من إضافة منتجات في صفحة 'products' بجدول جوجل.")
    st.stop()

col_main, col_cart = st.columns([3, 1.5])

with col_main:
    # فلترة التصنيفات
    all_cats = ["الكل"] + (prods_df['cat'].unique().tolist() if 'cat' in prods_df.columns else [])
    tabs = st.tabs(all_cats)
    
    for i, tab in enumerate(tabs):
        with tab:
            current_cat = all_cats[i]
            filtered = prods_df if current_cat == "الكل" else prods_df[prods_df['cat'] == current_cat]
            
            # عرض المنتجات في شبكة (Grid)
            for idx in range(0, len(filtered), 3):
                cols = st.columns(3)
                for j, (_, row) in enumerate(filtered.iloc[idx:idx+3].iterrows()):
                    with cols[j]:
                        st.markdown('<div class="product-box">', unsafe_allow_html=True)
                        
                        # محاولة عرض الصورة أو وضع أيقونة بديلة
                        img_url = row['img'] if not pd.isna(row.get('img')) else ""
                        if img_url and str(img_url).startswith("http"):
                            st.image(img_url, use_container_width=True)
                        else:
                            st.markdown("<h1 style='font-size:80px;'>📦</h1>", unsafe_allow_html=True)
                        
                        st.subheader(row['name'])
                        st.markdown(f'<p class="price-tag">{row["price"]} دج</p>', unsafe_allow_html=True)
                        
                        q = st.number_input("الكمية", 0.5, 50.0, 1.0, 0.5, key=f"q_{row['name']}_{idx+j}")
                        if st.button("إضافة 🛒", key=f"btn_{row['name']}_{idx+j}"):
                            if row['name'] in st.session_state.cart:
                                st.session_state.cart[row['name']]['qty'] += q
                            else:
                                st.session_state.cart[row['name']] = {'price': row['price'], 'qty': q}
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

with col_cart:
    st.markdown("### 🧺 سلتك")
    total = 0
    items_to_send = []
    
    if not st.session_state.cart:
        st.info("السلة فارغة حالياً")
    else:
        for name, info in list(st.session_state.cart.items()):
            subtotal = info['price'] * info['qty']
            total += subtotal
            c1, c2 = st.columns([4, 1])
            c1.write(f"**{name}**\n{info['qty']} كغ = {int(subtotal)} دج")
            if c2.button("❌", key=f"del_{name}"):
                del st.session_state.cart[name]; st.rerun()
            items_to_send.append(f"{name} ({info['qty']} كغ)")
            st.divider()
        
        st.markdown(f"## المجموع: {int(total)} دج")
        
        with st.form("checkout_form"):
            u_name = st.text_input("الاسم الكامل")
            u_addr = st.text_input("العنوان (الحي/المدينة)")
            
            # اختيار الموصل من الجدول
            d_names = drivers_df['name'].tolist() if not drivers_df.empty else []
            sel_d = st.selectbox("اختر موصل التوصيل", d_names) if d_names else None
            
            if st.form_submit_button("✅ إتمام الطلب"):
                if u_name and u_addr and sel_d:
                    d_phone = drivers_df[drivers_df['name'] == sel_d]['phone'].iloc[0]
                    msg = f"السلام عليكم، طلب جديد:\n\n👤 الزبون: {u_name}\n📍 العنوان: {u_addr}\n🛍️ المشتريات: {' + '.join(items_to_send)}\n💰 المجموع: {int(total)} دج"
                    
                    st.success("تم تجهيز رسالتك!")
                    st.markdown(f'<a href="https://wa.me/{d_phone}?text={urllib.parse.quote(msg)}" target="_blank" style="background:#006341;color:white;display:block;text-align:center;padding:15px;border-radius:15px;text-decoration:none;font-weight:bold;font-size:1.1rem;">🚀 اضغط هنا للإرسال عبر واتساب</a>', unsafe_allow_html=True)
                else:
                    st.error("يرجى إدخال كافة البيانات واختيار الموصل")
