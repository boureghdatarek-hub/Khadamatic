import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# --- إعداد الصفحة (نظام ليلي افتراضي) ---
st.set_page_config(page_title="KhadamaTic Pro", layout="wide")

# --- الثيم الليلي (Dark Theme CSS) ---
st.markdown("""
<style>
    /* تغيير الخلفية العامة */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* تنسيق العناوين */
    h1, h2, h3 {
        color: #4CAF50 !important;
        text-align: center;
    }
    
    /* تنسيق الكروت (المنتجات) */
    .product-card {
        background-color: #1C2128;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #333;
        text-align: center;
        margin-bottom: 10px;
    }
    
    /* تنسيق أزرار الطلب */
    div.stButton > button {
        background-color: #2E7D32 !important;
        color: white !important;
        border-radius: 8px !important;
        width: 100%;
    }
    
    /* تنسيق النصوص والقوائم */
    .stSelectbox, .stTextInput, .stTextArea {
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# --- محاكاة العرض ---
st.markdown("<h1>🌿 KhadamaTic | خَدَماتِك 🌿</h1>", unsafe_allow_html=True)
st.markdown("---")

# عرض توضيحي لشكل الثيم الليلي
col1, col2 = st.columns(2)
with col1:
    st.markdown("<div class='product-card'><h3>منتج تجريبي</h3><p>السعر: 500 دج</p></div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='product-card'><h3>منتج تجريبي 2</h3><p>السعر: 800 دج</p></div>", unsafe_allow_html=True)
