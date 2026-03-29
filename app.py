import streamlit as st
import pandas as pd
import urllib.parse

# 1. إعدادات الصفحة والألوان
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: white !important; color: black !important; }
    /* إجبار لون النصوص والخلفيات في الهاتف */
    h1, h2, h3, p, span, label, .stTabs button p { color: black !important; font-weight: bold !important; }
    div[data-baseweb="tab-list"] { background-color: #f0f2f6; border-radius: 10px; padding: 5px; }
    div[data-baseweb="tab"] { background-color: transparent !important; }
    
    .product-card {
        background: white; padding: 10px; border-radius: 15px;
        border: 1px solid #eee; text-align: center; margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .price-text { color: #006341 !important; font-size: 1.1rem; }
    input { background-color: #f0f2f6 !important; color: black !important; }
</style>
""", unsafe_allow_html=True)

# 2. البيانات
SHEET_ID = "15R1XMLD-8FGG-WIsXM1PZ0JLTceGIJyjNIHgb_uNOZk"

@st.cache_data(ttl=10)
def get_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        return pd.read_csv(url).dropna(how='all')
    except: return pd.DataFrame()

prods_df = get_data("products")
drivers_df = get_data("drivers")

if 'cart' not in st.session_state: st.session_state.cart = {}

# 3. التحقق من وضع الإدارة (عبر الرابط ?admin=true)
is_admin = st.query_params.get("admin") == "true"

if is_admin:
    st.title("⚙️ لوحة التحكم")
    st.write("بيانات المنتجات الحالية في جوجل:")
    st.dataframe(prods_df, use_container_width=True)
    if st.button("العودة للمتجر"):
        st.query_params.clear()
        st.rerun()
else:
    # --- واجهة الزبائن ---
    st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)
    
    # خانات التصنيفات (Categories) عادت هنا
    if not prods_df.empty:
        search = st.text_input("", placeholder="🔍 ابحث عن منتج...", label_visibility="collapsed")
        
        categories = ["الكل"] + prods_df['cat'].unique().tolist()
        tabs = st.tabs(categories) # إعادة الخانات العلوية
        
        for i, tab in enumerate(tabs):
            with tab:
                current_cat = categories[i]
                filtered = prods_df if current_cat == "الكل" else prods_df[prods_df['cat'] == current_cat]
                if search:
                    filtered = filtered[filtered['name'].str.contains(search, case=False, na=False)]
                
                # عرض المنتجات
                for idx in range(0, len(filtered), 2):
                    cols = st.columns(2)
                    for j, (_, row) in enumerate(filtered.iloc[idx:idx+2].iterrows()):
                        with cols[j]:
                            st.markdown('<div class="product-card">', unsafe_allow_html=True)
                            if not pd.isna(row.get('img')) and str(row['img']).startswith("http"):
                                st.image(row['img'], use_container_width=True)
                            st.write(f"**{row['name']}**")
                            st.markdown(f'<p class="price-text">{row["price"]} دج</p>', unsafe_allow_html=True)
                            
                            # مفتاح فريد لمنع الانهيار
                            k = f"{row['name']}_{current_cat}_{idx}_{j}"
                            q = st.number_input("الكمية", 0.5, 50.0, 1.0, 0.5, key=f"q_{k}", label_visibility="collapsed")
                            if st.button("🛒 أضف", key=f"b_{k}"):
                                st.session_state.cart[row['name']] = {'price': row['price'], 'qty': q}
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)

    # 4. السلة
    if st.session_state.cart:
        st.divider()
        st.subheader("🧺 المشتريات")
        total = 0
        items_summary = []
        for name, info in list(st.session_state.cart.items()):
            sub = info['price'] * info['qty']
            total += sub
            c1, c2 = st.columns([4, 1])
            c1.write(f"**{name}** ({info['qty']} كغ)")
            if c2.button("❌", key=f"del_{name}"):
                del st.session_state.cart[name]; st.rerun()
            items_summary.append(f"{name} ({info['qty']} كغ)")

        st.markdown(f"### المجموع: {int(total)} دج")
        with st.form("checkout"):
            u_name = st.text_input("الاسم")
            u_addr = st.text_input("العنوان")
            d_list = drivers_df['name'].tolist() if not drivers_df.empty else ["عام"]
            sel_d = st.selectbox("الموصل", d_list)
            if st.form_submit_button("إرسال للواتساب ✅"):
                if u_name and u_addr:
                    phone = drivers_df[drivers_df['name']==sel_d]['phone'].iloc[0] if not drivers_df.empty else "213"
                    msg = f"طلب من: {u_name}\nالعنوان: {u_addr}\nالمنتجات: {' + '.join(items_summary)}\nالمجموع: {int(total)} دج"
                    st.markdown(f'<a href="https://wa.me/{phone}?text={urllib.parse.quote(msg)}" target="_blank" style="background:green;color:white;display:block;text-align:center;padding:12px;border-radius:10px;text-decoration:none;">تأكيد الإرسال</a>', unsafe_allow_html=True)
