import streamlit as st
import pandas as pd
import urllib.parse

# 1. Page Configuration & Theme Lock (Light Mode)
st.set_page_config(page_title="SM KHADAMATIC", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: white !important; color: black !important; }
    h1, h2, h3, p, span, label, .stTabs button p { color: black !important; font-weight: bold !important; }
    
    /* Make Tabs look like clear buttons */
    div[data-baseweb="tab-list"] { background-color: #f0f2f6; border-radius: 12px; padding: 5px; gap: 10px; }
    div[data-baseweb="tab"] { border-radius: 8px !important; }
    
    .product-card {
        background: white; padding: 12px; border-radius: 15px;
        border: 1px solid #eee; text-align: center; margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .price-text { color: #006341 !important; font-size: 1.2rem; margin-bottom: 10px; }
    
    /* Fix for mobile input visibility */
    input { background-color: #f0f2f6 !important; color: black !important; }
</style>
""", unsafe_allow_html=True)

# 2. Data Fetching
SHEET_ID = "15R1XMLD-8FGG-WIsXM1PZ0JLTceGIJyjNIHgb_uNOZk"

@st.cache_data(ttl=5) # Cache for 5 seconds to keep it fast but updated
def get_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(url)
        return df.dropna(how='all')
    except:
        return pd.DataFrame()

# Initialize everything
prods_df = get_data("products")
drivers_df = get_data("drivers")

# --- CRITICAL: PERSISTENT CART LOGIC ---
if 'cart' not in st.session_state:
    st.session_state.cart = {}

# 3. Main Interface
st.markdown("<h1 style='text-align:center; color:#006341;'>🛒 SM KHADAMATIC</h1>", unsafe_allow_html=True)

# Search Bar
search = st.text_input("", placeholder="🔍 Search for a product...", key="global_search", label_visibility="collapsed")

if not prods_df.empty:
    # Categories Tabs
    categories = ["الكل"] + prods_df['cat'].unique().tolist()
    tabs = st.tabs(categories)
    
    for i, tab in enumerate(tabs):
        with tab:
            current_cat = categories[i]
            filtered = prods_df if current_cat == "الكل" else prods_df[prods_df['cat'] == current_cat]
            if search:
                filtered = filtered[filtered['name'].str.contains(search, case=False, na=False)]
            
            # Display Products in a 2-column grid
            for idx in range(0, len(filtered), 2):
                cols = st.columns(2)
                for j, (_, row) in enumerate(filtered.iloc[idx:idx+2].iterrows()):
                    with cols[j]:
                        st.markdown('<div class="product-card">', unsafe_allow_html=True)
                        
                        # Product Image
                        img_url = row['img'] if not pd.isna(row.get('img')) else ""
                        if img_url and str(img_url).startswith("http"):
                            st.image(img_url, use_container_width=True)
                        else:
                            st.markdown("<h2 style='margin:0;'>📦</h2>", unsafe_allow_html=True)
                        
                        st.write(f"**{row['name']}**")
                        st.markdown(f'<p class="price-text">{row["price"]} دج</p>', unsafe_allow_html=True)
                        
                        # Unique Keys for inputs and buttons
                        item_id = f"{row['name']}_{current_cat}_{idx}_{j}".replace(" ", "_")
                        
                        qty = st.number_input("الكمية", 0.5, 100.0, 1.0, 0.5, key=f"q_{item_id}", label_visibility="collapsed")
                        
                        if st.button("🛒 Add to Cart", key=f"btn_{item_id}"):
                            name = row['name']
                            price = row['price']
                            # Update Cart Logic
                            if name in st.session_state.cart:
                                st.session_state.cart[name]['qty'] += qty
                            else:
                                st.session_state.cart[name] = {'price': price, 'qty': qty}
                            st.toast(f"Added {name} to cart!")
                            st.rerun() # Force UI update to show cart
                        
                        st.markdown('</div>', unsafe_allow_html=True)

# 4. Shopping Cart (Persistent)
if st.session_state.cart:
    st.markdown("---")
    st.subheader("🧺 Your Shopping Cart")
    
    total_price = 0
    items_list_txt = []
    
    for name, info in list(st.session_state.cart.items()):
        subtotal = info['price'] * info['qty']
        total_price += subtotal
        
        c1, c2 = st.columns([4, 1])
        c1.write(f"**{name}** ({info['qty']} kg) = {int(subtotal)} DZD")
        
        if c2.button("❌", key=f"del_{name}"):
            del st.session_state.cart[name]
            st.rerun()
            
        items_list_txt.append(f"{name} ({info['qty']} kg)")

    st.markdown(f"### Total: {int(total_price)} DZD")
    
    # WhatsApp Order Form
    with st.form("whatsapp_order"):
        u_name = st.text_input("Full Name")
        u_addr = st.text_input("Delivery Address")
        d_list = drivers_df['name'].tolist() if not drivers_df.empty else ["Standard"]
        selected_driver = st.selectbox("Choose Driver", d_list)
        
        if st.form_submit_button("Send Order via WhatsApp ✅"):
            if u_name and u_addr:
                # Find driver phone
                try:
                    phone = drivers_df[drivers_df['name'] == selected_driver]['phone'].iloc[0]
                except:
                    phone = "213" # Fallback

                msg = f"New Order:\nName: {u_name}\nAddress: {u_addr}\nProducts: {' + '.join(items_list_txt)}\nTotal: {int(total_price)} DZD"
                st.markdown(f'<a href="https://wa.me/{phone}?text={urllib.parse.quote(msg)}" target="_blank" style="background:#25D366;color:white;display:block;text-align:center;padding:15px;border-radius:12px;text-decoration:none;font-weight:bold;">🚀 Click to Send on WhatsApp</a>', unsafe_allow_html=True)
            else:
                st.error("Please fill in your name and address.")
