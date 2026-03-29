import streamlit as st
import pandas as pd
import urllib.parse

# --- فرض التنسيق الأبيض ومنع الخانات السوداء ---
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

st.markdown("""
<style>
    /* فرض خلفية بيضاء لكل الموقع */
    .stApp { background-color: white !important; }
    
    /* تنسيق خانات الإدخال (البحث، الكمية، الاسم) لتكون بيضاء دائماً بنص أسود */
    input, select, textarea, div[data-baseweb="input"] {
        background-color: #f2f2f2 !important;
        color: black !important;
        border: 1px solid #ddd !important;
    }

    /* إصلاح النصوص لتكون سوداء وواضحة */
    h1, h2, h3, p, span, label, .stMarkdown {
        color: #1a1a1a !important;
    }

    /* تنسيق كرت المنتج للهاتف */
    .product-card {
        background: #ffffff;
        padding: 10px;
        border-radius: 15px;
        border: 1px solid #eee;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    /* تصغير حجم خانة البحث */
    div[data-testid="stTextInput"] { margin-top: -20px; }
    
    /* تنسيق زر الواتساب */
    .whatsapp-btn {
        background-color: #25D366;
        color: white !important;
        display: block;
        text-align: center;
        padding: 12px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        margin-top: 10px;
    }

    /* إخفاء شعار Streamlit المتطفل */
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- جلب البيانات ---
SHEET_ID = "15R1XMLD-8FGG-WIsXM1PZ0JLTceGIJyjNIHgb_uNOZk"

@st.cache_data(ttl=60) # تحديث البيانات كل دقيقة
def get_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&sheet={sheet_name}"
    try:
        return pd.read_csv(url).dropna(how='all')
    except:
        return pd.DataFrame()

prods_df = get_data("products")
drivers_df = get_data("drivers")

if 'cart' not in st.session_state: st.session_state.cart = {}

# العنوان
st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)

# البحث
search = st.text_input("", placeholder="🔍 ابحث عن منتج هنا...", label_visibility="collapsed")

# عرض الأقسام
if not prods_df.empty:
    cats = ["الكل"] + prods_df['cat'].unique().tolist()
    tabs = st.tabs(cats)
    
    for i, tab in enumerate(tabs):
        with tab:
            current_cat = cats[i]
            filtered = prods_df if current_cat == "الكل" else prods_df[prods_df['cat'] == current_cat]
            if search:
                filtered = filtered[filtered['name'].str.contains(search, case=False, na=False)]
            
            # عرض المنتجات (2 في كل سطر للهاتف)
            for idx in range(0, len(filtered), 2):
                cols = st.columns(2)
                for j, (_, row) in enumerate(filtered.iloc[idx:idx+2].iterrows()):
                    with cols[j]:
                        st.markdown('<div class="product-card">', unsafe_allow_html=True)
                        if not pd.isna(row.get('img')):
                            st.image(row['img'], use_container_width=True)
                        st.markdown(f"<b>{row['name']}</b>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color:green;'>{row['price']} دج</p>", unsafe_allow_html=True)
                        
                        q = st.number_input("الكمية", 0.5, 50.0, 1.0, 0.5, key=f"q_{row['name']}_{idx+j}", label_visibility="collapsed")
                        if st.button("🛒 أضف", key=f"b_{row['name']}_{idx+j}"):
                            st.session_state.cart[row['name']] = {'price': row['price'], 'qty': q}
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

# سلة التسوق
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
            del st.session_state.cart[name]; st.rerun()
        summary.append(f"{name} ({info['qty']} كغ)")
    
    st.markdown(f"**المجموع الإجمالي: {int(total)} دج**")
    
    # معلومات الزبون
    with st.expander("✅ تأكيد الطلب"):
        u_name = st.text_input("الاسم الكامل")
        u_addr = st.text_input("عنوان التوصيل")
        d_list = drivers_df['name'].tolist() if not drivers_df.empty else ["توصيل عام"]
        sel_d = st.selectbox("اختر الموصل", d_list)
        
        if st.button("🚀 إرسال الطلب الآن"):
            if u_name and u_addr:
                try:
                    phone = drivers_df[drivers_df['name'] == sel_d]['phone'].iloc[0]
                except:
                    phone = "213XXXXXXXXX" # رقمك الافتراضي
                
                msg = f"طلب جديد من: {u_name}\nالعنوان: {u_addr}\nالمنتجات: {' + '.join(summary)}\nالمجموع: {int(total)} دج"
                url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{url}" class="whatsapp-btn" target="_blank">فتح واتساب لإرسال الطلب</a>', unsafe_allow_html=True)
            else:
                st.warning("يرجى ملء الاسم والعنوان")
