import streamlit as st
import pandas as pd
import urllib.parse

# 1. إجبار الموقع على الـ Light Mode ومنع الانهيار
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

st.markdown("""
<style>
    /* إجبار الخلفية البيضاء والنصوص السوداء (إيقاف Dark Mode) */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: white !important;
        color: black !important;
    }
    /* تنسيق كرت المنتج للهاتف */
    .product-card {
        background: #ffffff;
        padding: 10px;
        border-radius: 12px;
        border: 1px solid #f0f0f0;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    h1, h2, h3, p, span, label { color: black !important; }
    .price-text { color: #006341 !important; font-weight: bold; font-size: 1rem; }
    
    /* تصغير العناصر للهاتف */
    @media (max-width: 640px) {
        .block-container { padding: 0.5rem !important; }
        h1 { font-size: 1.5rem !important; }
        div[data-testid="column"] { width: 50% !important; flex: 1 1 45% !important; }
    }
    
    /* إخفاء عناصر Streamlit الزائدة */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 2. جلب البيانات
SHEET_ID = "15R1XMLD-8FGG-WIsXM1PZ0JLTceGIJyjNIHgb_uNOZk"

@st.cache_data(ttl=60)
def get_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        return pd.read_csv(url).dropna(how='all')
    except:
        return pd.DataFrame()

prods_df = get_data("products")
drivers_df = get_data("drivers")

if 'cart' not in st.session_state: st.session_state.cart = {}

# 3. واجهة المستخدم
st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)

search = st.text_input("", placeholder="🔍 ابحث عن منتج...", label_visibility="collapsed")

if not prods_df.empty:
    # حل مشكلة الانهيار: استخدام قائمة بسيطة بدلاً من الـ Tabs المعقدة للهاتف
    cats = ["الكل"] + prods_df['cat'].unique().tolist()
    selected_cat = st.selectbox("اختر القسم:", cats)
    
    filtered = prods_df if selected_cat == "الكل" else prods_df[prods_df['cat'] == selected_cat]
    if search:
        filtered = filtered[filtered['name'].str.contains(search, case=False, na=False)]

    # عرض المنتجات (2 في كل سطر)
    for idx in range(0, len(filtered), 2):
        cols = st.columns(2)
        for j, (_, row) in enumerate(filtered.iloc[idx:idx+2].iterrows()):
            with cols[j]:
                st.markdown('<div class="product-card">', unsafe_allow_html=True)
                if not pd.isna(row.get('img')) and str(row['img']).startswith("http"):
                    st.image(row['img'], use_container_width=True)
                
                st.markdown(f"**{row['name']}**")
                st.markdown(f'<p class="price-text">{row["price"]} دج</p>', unsafe_allow_html=True)
                
                # حل خطأ التكرار: إضافة اسم القسم للمفتاح (Key)
                q = st.number_input("الكمية", 0.5, 50.0, 1.0, 0.5, key=f"q_{row['name']}_{selected_cat}_{idx+j}", label_visibility="collapsed")
                if st.button("🛒 أضف", key=f"btn_{row['name']}_{selected_cat}_{idx+j}"):
                    st.session_state.cart[row['name']] = {'price': row['price'], 'qty': q}
                    st.toast(f"تمت إضافة {row['name']}")
                st.markdown('</div>', unsafe_allow_html=True)

# 4. السلة (تظهر فقط إذا كانت غير فارغة)
if st.session_state.cart:
    st.markdown("---")
    st.markdown("### 🧺 سلة المشتريات")
    total = 0
    summary = []
    for name, info in list(st.session_state.cart.items()):
        sub = info['price'] * info['qty']
        total += sub
        c1, c2 = st.columns([4, 1])
        c1.write(f"• {name} ({info['qty']} كغ) = {int(sub)} دج")
        if c2.button("❌", key=f"del_{name}"):
            del st.session_state.cart[name]
            st.rerun()
        summary.append(f"{name} ({info['qty']} كغ)")

    st.markdown(f"**💰 المجموع: {int(total)} دج**")
    
    with st.form("order"):
        u_name = st.text_input("الاسم")
        u_addr = st.text_input("العنوان")
        d_list = drivers_df['name'].tolist() if not drivers_df.empty else ["توصيل عام"]
        sel_d = st.selectbox("الموصل", d_list)
        
        if st.form_submit_button("إرسال الطلب (WhatsApp)"):
            if u_name and u_addr:
                phone = drivers_df[drivers_df['name']==sel_d]['phone'].iloc[0] if not drivers_df.empty else "213XXXXXXXXX"
                msg = f"طلب جديد من: {u_name}\nالعنوان: {u_addr}\nالمنتجات: {' + '.join(summary)}\nالمجموع: {int(total)} دج"
                st.markdown(f'<a href="https://wa.me/{phone}?text={urllib.parse.quote(msg)}" target="_blank" style="background:green;color:white;display:block;text-align:center;padding:12px;border-radius:8px;text-decoration:none;">✅ تأكيد الإرسال الآن</a>', unsafe_allow_html=True)
