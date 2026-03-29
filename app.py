import streamlit as st
import pandas as pd
import urllib.parse

# --- إعدادات الصفحة المتقدمة للهاتف ---
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

# CSS مكثف لضغط الواجهة وتصغير الخطوط
st.markdown("""
<style>
    /* تقليل الفراغات العلوية والسفلية */
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
    header { visibility: hidden; }
    
    /* تنسيق كرت المنتج للهاتف */
    .product-card {
        background: white;
        padding: 8px;
        border-radius: 10px;
        border: 1px solid #eee;
        text-align: center;
        margin-bottom: 8px;
    }
    
    /* تصغير النصوص */
    h1 { font-size: 1.4rem !important; margin-bottom: 5px !important; }
    .stMarkdown p { font-size: 0.85rem !important; margin-bottom: 2px !important; }
    .price-text { color: #006341; font-weight: bold; font-size: 0.9rem !important; }
    
    /* تعديل شكل أزرار التصنيفات (Tabs) */
    .stTabs [data-baseweb="tab-list"] { gap: 5px; }
    .stTabs [data-baseweb="tab"] { 
        padding: 5px 10px !important; 
        font-size: 0.8rem !important;
        border-radius: 20px !important;
    }
    
    /* تصغير خانات إدخال الأرقام */
    div[data-testid="stNumberInput"] label { display: none; }
    div[data-testid="stNumberInput"] input { font-size: 0.8rem !important; padding: 5px !important; }
    
    /* جعل زر الإضافة أصغر */
    .stButton button { 
        padding: 2px 10px !important; 
        font-size: 0.8rem !important; 
        min-height: 30px !important;
        border-radius: 15px !important;
    }

    /* إخفاء شعار Streamlit في الأسفل */
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

SHEET_ID = "15R1XMLD-8FGG-WIsXM1PZ0JLTceGIJyjNIHgb_uNOZk"

def get_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(url)
        return df.dropna(how='all')
    except:
        return pd.DataFrame()

# تحميل البيانات
prods_df = get_data("products")
drivers_df = get_data("drivers")

if 'cart' not in st.session_state: st.session_state.cart = {}

# العنوان
st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)

# البحث (تصغير الخانة)
search = st.text_input("", placeholder="🔍 ابحث هنا...", label_visibility="collapsed")

# التصنيفات
if not prods_df.empty:
    cats = ["الكل"] + prods_df['cat'].unique().tolist()
    tabs = st.tabs(cats)
    
    for i, tab in enumerate(tabs):
        with tab:
            current_cat = cats[i]
            filtered = prods_df if current_cat == "الكل" else prods_df[prods_df['cat'] == current_cat]
            if search:
                filtered = filtered[filtered['name'].str.contains(search, case=False, na=False)]
            
            # العرض في أعمدة صغيرة (2 في كل سطر للهاتف)
            for idx in range(0, len(filtered), 2):
                cols = st.columns(2)
                for j, (_, row) in enumerate(filtered.iloc[idx:idx+2].iterrows()):
                    with cols[j]:
                        st.markdown('<div class="product-card">', unsafe_allow_html=True)
                        
                        # الصورة بحجم محدد جداً
                        img_url = row['img'] if not pd.isna(row.get('img')) else ""
                        if img_url and str(img_url).startswith("http"):
                            st.image(img_url, use_container_width=True)
                        else:
                            st.markdown("<h2 style='margin:0;'>📦</h2>", unsafe_allow_html=True)
                        
                        st.markdown(f"**{row['name']}**")
                        st.markdown(f'<p class="price-text">{row["price"]} دج</p>', unsafe_allow_html=True)
                        
                        # خانة الكمية وزر الإضافة في نفس السطر أو تحت بعض بشكل مضغوط
                        q = st.number_input("الكمية", 0.5, 20.0, 1.0, 0.5, key=f"q_{row['name']}_{idx+j}", label_visibility="collapsed")
                        if st.button("🛒 أضف", key=f"b_{row['name']}_{idx+j}"):
                            st.session_state.cart[row['name']] = {'price': row['price'], 'qty': q}
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

# السلة في الأسفل بشكل أنيق
if st.session_state.cart:
    st.divider()
    with st.expander(f"🧺 سلتك ({len(st.session_state.cart)})", expanded=True):
        total = 0
        items_list = []
        for name, info in list(st.session_state.cart.items()):
            sub = info['price'] * info['qty']
            total += sub
            c1, c2 = st.columns([4, 1])
            c1.write(f"{name} | {info['qty']} كغ | {int(sub)} دج")
            if c2.button("❌", key=f"del_{name}"):
                del st.session_state.cart[name]; st.rerun()
            items_list.append(f"{name} ({info['qty']} كغ)")
        
        st.markdown(f"**المجموع: {int(total)} دج**")
        
        # استمارة الطلب مصغرة
        with st.form("checkout"):
            u_name = st.text_input("الاسم", placeholder="اسمك الكامل")
            u_addr = st.text_input("العنوان", placeholder="عنوان التوصيل")
            d_names = drivers_df['name'].tolist() if not drivers_df.empty else ["افتراضي"]
            sel_d = st.selectbox("الموصل", d_names)
            
            if st.form_submit_button("إرسال طلب واتساب ✅"):
                if u_name and not drivers_df.empty:
                    # جلب رقم هاتف الموصل المختار
                    try:
                        d_phone = drivers_df[drivers_df['name'] == sel_d]['phone'].iloc[0]
                    except:
                        d_phone = "213XXXXXXXXX" # رقم احتياطي
                    
                    msg = f"طلب جديد من {u_name}\nالعنوان: {u_addr}\nالمنتجات: {' + '.join(items_list)}\nالمجموع: {int(total)} دج"
                    st.markdown(f'<a href="https://wa.me/{d_phone}?text={urllib.parse.quote(msg)}" target="_blank" style="background:#25D366;color:white;display:block;text-align:center;padding:12px;border-radius:10px;text-decoration:none;font-weight:bold;">🚀 اضغط هنا للإرسال</a>', unsafe_allow_html=True)
