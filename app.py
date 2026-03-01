import streamlit as st
import json
import os
import urllib.parse
import pandas as pd
from datetime import datetime

# إعداد الصفحة
st.set_page_config(page_title="KhadamaTic Pro Max", layout="wide")

# --- 1. إدارة البيانات ---
DB_FILE = "khadamatict_pro_db.json"

def load_data():
    base = {
        "products": [], "delivery": [], "vendors": [], 
        "customers": [], "categories": ["خضروات", "فواكه", "عروض"],
        "orders": []
    }
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k in base: 
                    if k not in data: data[k] = base[k]
                return data
        except: pass
    return base

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if 'db' not in st.session_state: st.session_state.db = load_data()
if 'cart' not in st.session_state: st.session_state.cart = {}

# --- 2. التصميم CSS (ليلي مريح جداً) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117 !important; color: #E0E0E0 !important; }
    h1, h2, h3, label { color: #81C784 !important; }
    .card { 
        background: #1C2128; padding: 15px; border-radius: 12px; 
        border-left: 5px solid #4CAF50; margin-bottom: 10px; 
    }
    div.stButton > button { 
        background-color: #2E7D32 !important; color: white !important; 
        border-radius: 10px; font-weight: bold; width: 100%; transition: 0.3s;
    }
    div.stButton > button:hover { background-color: #43A047 !important; transform: scale(1.02); }
    .stDownloadButton > button { background-color: #1976D2 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>KhadamaTic | خَدَماتِك 🌿</h1>", unsafe_allow_html=True)
t1, t2, t3 = st.tabs(["🛒 المتجر والطلب", "📊 السجل والإحصائيات", "⚙️ الإدارة الإحترافية"])

# --- Tab 1: المتجر والطلب ---
with t1:
    cats = ["الكل"] + st.session_state.db['categories']
    c_cols = st.columns(len(cats))
    if 's_cat' not in st.session_state: st.session_state.s_cat = "الكل"
    for i, c in enumerate(cats):
        if c_cols[i].button(c, key=f"cat_{c}"): 
            st.session_state.s_cat = c; st.rerun()

    st.divider()
    col_p, col_c = st.columns([2.5, 1.5])
    
    with col_p:
        prods = [p for p in st.session_state.db['products'] if st.session_state.s_cat == "الكل" or p.get('category') == st.session_state.s_cat]
        cols = st.columns(3)
        for i, p in enumerate(prods):
            with cols[i % 3]:
                st.markdown(f"<div class='card' style='text-align:center;'><b>{p['name']}</b><br>{p['price']} دج</div>", unsafe_allow_html=True)
                if p.get('img'): st.image(p['img'], use_container_width=True)
                c1, c2, c3 = st.columns([1,1,1])
                if c1.button("➖", key=f"m_{i}"): st.session_state.cart[p['name']] = max(0, st.session_state.cart.get(p['name'], 0)-1); st.rerun()
                c2.markdown(f"<center><b>{st.session_state.cart.get(p['name'], 0)}</b></center>", unsafe_allow_html=True)
                if c3.button("➕", key=f"p_{i}"): st.session_state.cart[p['name']] = st.session_state.cart.get(p['name'], 0)+1; st.rerun()

    with col_c:
        st.subheader("📝 تفاصيل الفاتورة")
        cust_names = ["زبون جديد"] + [c['name'] for c in st.session_state.db['customers']]
        sel_c = st.selectbox("الزبون:", cust_names)
        
        d_p, d_a = "", ""
        if sel_c != "زبون جديد":
            cd = next(c for c in st.session_state.db['customers'] if c['name'] == sel_c)
            d_p, d_a = cd['phone'], cd['address']

        c_name = st.text_input("الاسم", value="" if sel_c=="زبون جديد" else sel_c)
        c_phone = st.text_input("الهاتف", value=d_p)
        c_addr = st.text_area("العنوان", value=d_a)
        
        col_fees = st.columns(2)
        ship_fees = col_fees[0].number_input("سعر التوصيل (دج)", min_value=0, value=0)
        discount = col_fees[1].number_input("خصم (دج)", min_value=0, value=0)
        
        sum_txt, subtotal = "", 0
        for k, v in st.session_state.cart.items():
            if v > 0:
                p_match = next(x for x in st.session_state.db['products'] if x['name'] == k)
                subtotal += v * p_match['price']
                st.write(f"✅ {k} x{v}")
                sum_txt += f"- {k}: {v}\n"
        
        grand_total = subtotal + ship_fees - discount
        st.markdown(f"### الإجمالي النهائي: {grand_total} دج")
        
        v_l = [f"{v['name']} ({v['phone']})" for v in st.session_state.db['vendors']]
        d_l = [f"{d['name']} ({d['phone']})" for d in st.session_state.db['delivery']]
        sv = st.selectbox("البائع:", v_l if v_l else ["أضف بائع"])
        sd = st.selectbox("الموصل:", d_l if d_l else ["أضف موصل"])

        if grand_total > 0 and c_name and v_l and d_l:
            if st.button("🚀 تأكيد وحفظ الطلب"):
                if not any(c['name'] == c_name for c in st.session_state.db['customers']):
                    st.session_state.db['customers'].append({"name": c_name, "phone": c_phone, "address": c_addr})
                
                new_order = {
                    "id": len(st.session_state.db['orders']) + 1,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "customer": c_name, "items": sum_txt, "total": grand_total,
                    "shipping": ship_fees, "discount": discount, "status": "قيد التجهيز 🟡"
                }
                st.session_state.db['orders'].append(new_order)
                save_data(st.session_state.db)
                st.success("تم الحفظ!")

            v_num = sv.split('(')[1][:-1].strip()
            v_num = v_num if v_num.startswith('213') else f"213{v_num.lstrip('0')}"
            full_msg = (f"📢 *طلب جديد*\n🏪 البائع: {sv.split(' ')[0]}\n📦 الطلبات:\n{sum_txt}"
                        f"🚚 التوصيل: {ship_fees} دج\n💰 الخصم: {discount} دج\n🛵 الموصل: {sd.split(' ')[0]}\n"
                        f"👤 الزبون: {c_name}\n📍 {c_addr}\n💰 *الإجمالي: {grand_total} دج*")
            
            wa_url = f"https://api.whatsapp.com/send?phone={v_num}&text={urllib.parse.quote(full_msg)}"
            st.link_button("📲 إرسال عبر واتساب", wa_url)

# --- Tab 2: السجل والإحصائيات ---
with t2:
    st.header("📊 لوحة الأداء")
    df_o = pd.DataFrame(st.session_state.db['orders'])
    if not df_o.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي المبيعات", f"{df_o['total'].sum()} دج")
        c2.metric("عدد الطلبات", len(df_o))
        c3.metric("إجمالي التوصيل", f"{df_o['shipping'].sum()} دج")
        
        st.subheader("📋 تتبع الحالات")
        for i, order in enumerate(st.session_state.db['orders']):
            with st.expander(f"طلب #{order['id']} - {order['customer']} ({order['status']})"):
                col_st = st.columns([2, 1])
                new_s = col_st[0].selectbox("الحالة:", ["قيد التجهيز 🟡", "تم الاستلام 🔵", "تم التوصيل 🟢"], key=f"st_{i}", index=["قيد التجهيز 🟡", "تم الاستلام 🔵", "تم التوصيل 🟢"].index(order['status']))
                if col_st[1].button("تحديث ✅", key=f"up_{i}"):
                    st.session_state.db['orders'][i]['status'] = new_s
                    save_data(st.session_state.db); st.rerun()
                st.write(f"المبلغ: {order['total']} دج | الأصناف: {order['items']}")
    else: st.info("لا يوجد بيانات.")

# --- Tab 3: الإدارة وتعديل البيانات ---
with t3:
    st.subheader("🛠 الإدارة العامة")
    col_a, col_b = st.columns([1.5, 2])
    with col_a:
        m = st.radio("إضافة جديد:", ["منتج", "موصل", "بائع", "صنف"], horizontal=True)
        with st.form("add_form", clear_on_submit=True):
            n = st.text_input("الاسم")
            if m == "منتج":
                p = st.number_input("السعر", min_value=0)
                img = st.text_input("رابط الصورة")
                cat = st.selectbox("الصنف", st.session_state.db['categories'])
            elif m == "صنف": pass
            else: ph = st.text_input("الهاتف")
            
            if st.form_submit_button("إضافة ✅"):
                if m == "منتج": st.session_state.db['products'].append({"name":n, "price":p, "img":img, "category":cat})
                elif m == "صنف": st.session_state.db['categories'].append(n)
                else: st.session_state.db["delivery" if m=="موصل" else "vendors"].append({"name":n, "phone":ph})
                save_data(st.session_state.db); st.rerun()

    with col_b:
        view = st.selectbox("عرض البيانات:", ["المنتجات", "الموصلين", "البائعين", "الزبائن", "الطلبات"])
        m_key = {"المنتجات":"products", "الموصلين":"delivery", "البائعين":"vendors", "الزبائن":"customers", "الطلبات":"orders"}
        data = st.session_state.db[m_key[view]]
        
        if data:
            st.download_button(f"📥 تصدير {view} لـ Excel", pd.DataFrame(data).to_csv(index=False).encode('utf-8-sig'), f"{view}.csv")
        
        st.markdown("---")
        for i, item in enumerate(data):
            with st.expander(f"⚙️ {item.get('name', item.get('customer', 'طلب'))}"):
                if view == "المنتجات":
                    new_n = st.text_input("الاسم", value=item['name'], key=f"en_{i}")
                    new_p = st.number_input("السعر", value=item['price'], key=f"ep_{i}")
                    if st.button("حفظ 💾", key=f"s_{i}"):
                        st.session_state.db['products'][i].update({"name": new_n, "price": new_p})
                        save_data(st.session_state.db); st.rerun()
                elif view in ["الموصلين", "البائعين", "الزبائن"]:
                    new_n = st.text_input("الاسم", value=item['name'], key=f"en_{i}")
                    new_ph = st.text_input("الهاتف", value=item['phone'], key=f"eph_{i}")
                    if st.button("حفظ 💾", key=f"s_{i}"):
                        st.session_state.db[m_key[view]][i].update({"name": new_n, "phone": new_ph})
                        save_data(st.session_state.db); st.rerun()
                if st.button("🗑 حذف", key=f"d_{i}"):
                    st.session_state.db[m_key[view]].pop(i)
                    save_data(st.session_state.db); st.rerun()