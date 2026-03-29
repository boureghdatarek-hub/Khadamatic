import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime
# سنستخدم مكتبة بسيطة للربط المباشر
from gspread_streamlit import get_as_dataframe, set_with_dataframe
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. إعداد الاتصال بجوجل شيت للكتابة ---
def save_order_to_sheets(order_data):
    try:
        # إعداد الصلاحيات (يجب رفع ملف json مع الكود أو استبداله بـ st.secrets)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        client = gspread.authorize(creds)
        
        # فتح الملف والتبويب
        sheet = client.open_by_key("15R1XMLD-8FGG-WIsXM1PZ0JLTceGIJyjNIHgb_uNOZk").worksheet("orders")
        
        # إضافة السطر الجديد
        sheet.append_row(order_data)
        return True
    except Exception as e:
        st.error(f"خطأ في الحفظ: {e}")
        return False

# --- 2. التنسيق وإصلاح حجم الصور (CSS صارم) ---
st.markdown("""
<style>
    [data-testid="stImage"] img {
        width: 100% !important;
        height: 150px !important; /* ارتفاع موحد وإلزامي */
        object-fit: contain !important;
        background-color: #f9f9f9;
        border-radius: 10px;
    }
    .product-card {
        border: 1px solid #eee;
        padding: 10px;
        border-radius: 15px;
        text-align: center;
        background: white;
    }
</style>
""", unsafe_allow_html=True)

# (نفس كود جلب بيانات المنتجات السابق ...)

# --- 3. تعديل منطقة تأكيد الطلب ---
if st.session_state.cart:
    st.divider()
    with st.expander("📝 بيانات التوصيل (سيتم الحفظ في الإكسيل)", expanded=True):
        u_name = st.text_input("الاسم الكامل")
        u_addr = st.text_input("عنوان التوصيل")
        selected_dr = st.selectbox("اختر الموصل", ["tarek", "admin"]) # أو اجلبهم من شيت الموصلين
        
        if st.button("🚀 إرسال الطلب وحفظه"):
            if u_name and u_addr:
                # تحضير البيانات للشيت
                products_str = ", ".join([f"{n} ({i['qty']})" for n, i in st.session_state.cart.items()])
                total_price = sum(i['price'] * i['qty'] for i in st.session_state.cart.values())
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                order_row = [u_name, u_addr, products_str, total_price, selected_dr, now]
                
                # 1. الحفظ في الإكسيل
                success = save_order_to_sheets(order_row)
                
                if success:
                    st.success("✅ تم تسجيل الطلب في الإكسيل بنجاح!")
                    
                    # 2. تحضير رسالة الواتساب
                    msg = f"طلب جديد: {u_name}\nالعنوان: {u_addr}\nالمنتجات: {products_str}\nالمجموع: {total_price} دج"
                    wa_url = f"https://wa.me/213xxxxxxxxx?text={urllib.parse.quote(msg)}"
                    
                    st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none; color:white; background:#25D366; padding:10px; border-radius:5px; display:block; text-align:center;">إرسال نسخة عبر الواتساب الآن</a>', unsafe_allow_html=True)
                    
                    # تنظيف السلة بعد الحفظ
                    # st.session_state.cart = {} 
                else:
                    st.error("فشل الحفظ في الإكسيل، يرجى التأكد من الصلاحيات.")
            else:
                st.warning("يرجى ملء الاسم والعنوان.")
