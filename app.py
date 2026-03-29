import streamlit as st
import pandas as pd
import urllib.parse
import uuid

# --- 1. إعدادات المتصفح وفرض المظهر الفاتح ---
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

st.markdown("""
<style>
    /* فرض الخلفية البيضاء ومنع الوضع الليلي */
    .stApp { background-color: #FFFFFF !important; }
    
    /* جعل كل النصوص سوداء وواضحة */
    h1, h2, h3, p, span, label, .stMarkdown { color: #000000 !important; }

    /* تنظيف خانات الإدخال من السواد */
    input, select, textarea, div[data-baseweb="input"] {
        background-color: #F8F9FA !important;
        color: #000000 !important;
        border: 1px solid #DDDDDD !important;
        -webkit-text-fill-color: #000000 !important;
    }

    /* تنسيق بطاقة المنتج لتكون نظيفة */
    .product-box {
        background: #FFFFFF;
        padding: 10px;
        border-radius: 12px;
        border: 1px solid #EEEEEE;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        height: 100%; /* لتوحيد الارتفاع */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    /* --- توحيد حجم الصور --- */
    .product-box img {
        width: 100%;
        height: 120px; /* الارتفاع الموحد للصور */
        object-fit: contain; /* الحفاظ على أبعاد الصورة داخل الإطار */
        margin-bottom: 5px;
    }

    /* زر الواتساب الأخضر */
    .wa-button {
        background-color: #25D366;
        color: white !important;
        padding: 12px;
        text-align: center;
        display: block;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
    }
    
    /* إخفاء القوائم غير الضرورية */
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. دالة جلب البيانات مع معالجة الأخطاء ---
SHEET_ID = "15R1XMLD-8FGG-WIsXM1PZ0JLTceGIJyjNIHgb_uNOZk"

@st.cache_data(ttl=20) # تحديث البيانات كل 20 ثانية
def get_sheet_data(name):
    # استخدام رابط gviz للحصول على البيانات بشكل أدق
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={name}"
    try:
        return pd.read_csv(url).dropna(how='all')
    except:
        return pd.DataFrame()

# تحميل البيانات الأساسية
prods = get_sheet_data("products")
drivers = get_sheet_data("drivers")

if 'cart' not in st.session_state: st.session_state.cart = {}

# --- 3. واجهة التطبيق الرئيسية (الزبون) ---
st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)

# البحث
search_query = st.text_input("", placeholder="🔍 ابحث هنا...", label_visibility="collapsed")

if not prods.empty:
    # تحديد أسماء التبويبات بناءً على الأقسام
    categories = ["الكل"] + prods['cat'].unique().tolist()
    
    # إضافة تبويب الإدارة في النهاية
    all_tabs = categories + ["📋 الإدارة"]
    tabs = st.tabs(all_tabs)
    
    # --- حلقات عرض المنتجات في التبويبات (للزبون) ---
    for i, tab in enumerate(tabs[:-1]): # نتوقف قبل تبويب الإدارة
        with tab:
            current_c = categories[i]
            # تصفية البيانات حسب القسم والبحث
            df_view = prods if current_c == "الكل" else prods[prods['cat'] == current_c]
            if search_query:
                df_view = df_view[df_view['name'].str.contains(search_query, case=False, na=False)]
            
            # عرض المنتجات (2 في كل سطر للهاتف)
            for idx in range(0, len(df_view), 2):
                cols = st.columns(2)
                for j, (_, row) in enumerate(df_view.iloc[idx:idx+2].iterrows()):
                    with cols[j]:
                        st.markdown('<div class="product-box">', unsafe_allow_html=True)
                        if not pd.isna(row.get('img')):
                            # الصورة الموحدة الحجم عبر CSS
                            st.image(row['img'])
                        else:
                            st.markdown("<h2 style='margin:0; text-align:center;'>📦</h2>", unsafe_allow_html=True)
                        
                        st.markdown(f"<b>{row['name']}</b>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color:green; font-weight:bold; margin:0;'>{row['price']} دج</p>", unsafe_allow_html=True)
                        
                        # مفتاح فريد لمنع خطأ Duplicate Key
                        unique_id = f"{i}_{idx}_{j}_{row['name']}"
                        
                        q = st.number_input("الكمية", 0.5, 50.0, 1.0, 0.5, key=f"q_{unique_id}", label_visibility="collapsed")
                        
                        if st.button("🛒 أضف", key=f"btn_{unique_id}"):
                            p_name = row['name']
                            if p_name in st.session_state.cart:
                                st.session_state.cart[p_name]['qty'] += q
                            else:
                                st.session_state.cart[p_name] = {'price': row['price'], 'qty': q}
                            st.toast(f"✅ تم إضافة {p_name}")
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

    # --- 4. تبويب الإدارة (Orders) ---
    with tabs[-1]: # التبويب الأخير
        st.write("### 📜 سجل الطلبات المستلمة")
        
        # تحميل بيانات الطلبات (منع الكاش هنا لتحديث فوري)
        orders_df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=orders").dropna(how='all')
        
        if not orders_df.empty:
            # عرض الطلبات في جدول منظم، مع تلوين الأسطر
            st.dataframe(orders_df, use_container_width=True)
            if st.button("♻️ تحديث القائمة"):
                st.rerun()
        else:
            st.info("لم يتم العثور على طلبات في شيت orders. تأكد من وجود عناوين الأعمدة في جوجل شيت.")

# --- 5. سلة التسوق (بدون تغيير في المنطق) ---
if st.session_state.cart:
    st.markdown("---")
    st.markdown("### 🧺 سلة التسوق الخاصة بك")
    total_bill = 0
    items_summary = []
    
    for item_name, details in list(st.session_state.cart.items()):
        line_total = details['price'] * details['qty']
        total_bill += line_total
        c1, c2 = st.columns([5, 1])
        c1.write(f"• {item_name} ({details['qty']} كغ) = {int(line_total)} دج")
        if c2.button("🗑️", key=f"del_{item_name}"):
            del st.session_state.cart[item_name]; st.rerun()
        items_summary.append(f"{item_name} ({details['qty']} كغ)")
    
    st.markdown(f"#### المجموع الإجمالي: {int(total_bill)} دج")
    
    # نموذج إرسال الطلب (واتساب فقط)
    with st.expander("📝 إكمال معلومات التوصيل"):
        name_input = st.text_input("الاسم واللقب")
        addr_input = st.text_input("العنوان")
        
        driver_names = drivers['name'].tolist() if not drivers.empty else ["موصل 1"]
        selected_driver = st.selectbox("اختيار الموصل", driver_names)
        
        if st.button("✅ تأكيد وإرسال عبر واتساب"):
            if name_input and addr_input:
                try:
                    target_phone = drivers[drivers_df['name'] == selected_driver]['phone'].iloc[0]
                except:
                    target_phone = "213" # ضع رقمك كاحتياطي
                
                whatsapp_msg = f"طلب من: {name_input}\n📍 العنوان: {addr_input}\n🥦 المشتريات: {' + '.join(items_summary)}\n💰 المجموع: {int(total_bill)} دج"
                encoded_msg = urllib.parse.quote(whatsapp_msg)
                st.markdown(f'<a href="https://wa.me/{target_phone}?text={encoded_msg}" class="wa-button" target="_blank">اضغط هنا لإرسال الطلب للواتساب</a>', unsafe_allow_html=True)
            else:
                st.error("يرجى إدخال الاسم والعنوان لإتمام الطلب")
