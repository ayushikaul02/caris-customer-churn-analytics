import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import time

# Page configuration
st.set_page_config(
    page_title="CARIS - Customer Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1a365d;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1a365d;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #718096;
    }
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 40px;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .login-title {
        text-align: center;
        font-size: 2rem;
        color: #1a365d;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# API Base URL
API_URL = "http://localhost:8000"

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'token' not in st.session_state:
    st.session_state.token = ""

# -------------------- LOGIN PAGE --------------------
if not st.session_state.logged_in:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🔐 CARIS Login</div>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            try:
                response = requests.post(
                    f"{API_URL}/api/auth/login",
                    json={"username": username, "password": password}
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.token = data.get("access_token")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
            except:
                st.error("❌ Could not connect to server. Make sure API is running.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# -------------------- MAIN DASHBOARD --------------------
# Header
st.markdown(f'<div class="main-header">📊 CARIS - Customer Churn Analytics</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/data-configuration.png", width=80)
    st.title("Navigation")
    
    page = st.radio(
        "Select Dashboard",
        ["🏠 Overview", "👥 Customers", "📈 Analytics", "🎯 Retention", "📊 Reports"]
    )
    
    st.markdown("---")
    st.caption(f"👤 Logged in as: {st.session_state.username}")
    
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.token = ""
        st.rerun()
    
    st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.caption("CARIS v1.0.0")

# API Headers with Token
headers = {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}

# Function to fetch data from API
@st.cache_data(ttl=300)
def fetch_customers():
    try:
        response = requests.get(f"{API_URL}/api/customers?limit=100", headers=headers, timeout=5)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        return pd.DataFrame()
    except:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_dashboard_metrics():
    try:
        response = requests.get(f"{API_URL}/api/dashboard/metrics", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}

@st.cache_data(ttl=300)
def fetch_churn_analysis():
    try:
        response = requests.get(f"{API_URL}/api/analytics/churn", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}

@st.cache_data(ttl=300)
def fetch_segments():
    try:
        response = requests.post(f"{API_URL}/api/analytics/customer-segments", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}

# Load data
with st.spinner("Loading data..."):
    df_customers = fetch_customers()
    metrics = fetch_dashboard_metrics()
    churn_data = fetch_churn_analysis()
    segments = fetch_segments()

# -------------------- OVERVIEW PAGE --------------------
if page == "🏠 Overview":
    st.markdown("## 📊 Executive Dashboard")
    
    if metrics:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics.get('customer_kpis', {}).get('total_customers', 0)}</div>
                <div class="metric-label">Total Customers</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics.get('customer_kpis', {}).get('active_customers', 0)}</div>
                <div class="metric-label">Active Customers</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            churn_rate = metrics.get('churn_kpis', {}).get('churn_rate', 0) * 100
            color = "#e74c3c" if churn_rate > 15 else "#f39c12" if churn_rate > 10 else "#27ae60"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color:{color}">{churn_rate:.1f}%</div>
                <div class="metric-label">Churn Rate</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            revenue = metrics.get('revenue_kpis', {}).get('total_revenue', 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">${revenue:,.0f}</div>
                <div class="metric-label">Total Revenue</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Revenue by Segment")
            if segments and 'segments' in segments:
                seg_data = segments['segments']
                fig = px.pie(
                    values=list(seg_data.values()),
                    names=list(seg_data.keys()),
                    title="Customer Segments Distribution",
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Customer Status Distribution")
            if metrics and 'segment_kpis' in metrics:
                status_data = metrics['segment_kpis'].get('status_distribution', {})
                if status_data:
                    fig = px.bar(
                        x=list(status_data.keys()),
                        y=list(status_data.values()),
                        title="Customer Status",
                        color=list(status_data.keys()),
                        color_discrete_sequence=px.colors.qualitative.Set2
                    )
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Could not connect to API. Make sure the server is running.")

# -------------------- CUSTOMERS PAGE --------------------
elif page == "👥 Customers":
    st.markdown("## 👥 Customer Management")
    
    if not df_customers.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            segment_filter = st.selectbox("Filter by Segment", ["All"] + list(df_customers['customer_segment'].unique()))
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All"] + list(df_customers['status'].unique()))
        with col3:
            search = st.text_input("Search Customer", placeholder="Name or Email...")
        
        filtered_df = df_customers.copy()
        if segment_filter != "All":
            filtered_df = filtered_df[filtered_df['customer_segment'] == segment_filter]
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['status'] == status_filter]
        if search:
            filtered_df = filtered_df[
                filtered_df['name'].str.contains(search, case=False) |
                filtered_df['email'].str.contains(search, case=False)
            ]
        
        st.markdown(f"**Showing {len(filtered_df)} customers**")
        st.dataframe(
            filtered_df[['customer_id', 'name', 'email', 'customer_segment', 'status', 'total_spent']],
            use_container_width=True,
            height=400
        )
    else:
        st.warning("No customer data available.")

# -------------------- ANALYTICS PAGE --------------------
elif page == "📈 Analytics":
    st.markdown("## 📈 Churn & Revenue Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Churn by Segment")
        if churn_data and 'churn_by_segment' in churn_data:
            churn_seg = churn_data['churn_by_segment']
            fig = px.bar(
                x=list(churn_seg.keys()),
                y=list(churn_seg.values()),
                title="Churn Rate by Customer Segment",
                labels={'x': 'Segment', 'y': 'Churn Rate'},
                color=list(churn_seg.keys()),
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Risk Distribution")
        if metrics and 'churn_kpis' in metrics:
            high_risk = metrics['churn_kpis'].get('high_risk_customers', 0)
            total = metrics.get('customer_kpis', {}).get('total_customers', 0)
            risk_data = {'Low Risk': total - high_risk, 'High Risk': high_risk}
            if sum(risk_data.values()) > 0:
                fig = px.pie(
                    values=list(risk_data.values()),
                    names=list(risk_data.keys()),
                    title="Customer Risk Distribution",
                    color=list(risk_data.keys()),
                    color_discrete_map={'Low Risk': '#27ae60', 'High Risk': '#e74c3c'}
                )
                st.plotly_chart(fig, use_container_width=True)

# -------------------- RETENTION PAGE --------------------
elif page == "🎯 Retention":
    st.markdown("## 🎯 Retention Recommendations")
    
    try:
        response = requests.post(f"{API_URL}/api/retention/recommendations", headers=headers, timeout=5)
        if response.status_code == 200:
            recommendations = response.json()
            risk_filter = st.selectbox("Filter by Risk Level", ["All", "Critical", "High", "Medium", "Low"])
            
            if risk_filter != "All":
                recommendations = [r for r in recommendations if r.get('risk_level') == risk_filter]
            
            for rec in recommendations[:10]:
                risk = rec.get('risk_level', 'Unknown')
                bg_color = "#fdedec" if risk in ['Critical', 'High'] else "#fef9e7" if risk == 'Medium' else "#ebf5fb"
                border_color = "#e74c3c" if risk in ['Critical', 'High'] else "#f39c12" if risk == 'Medium' else "#3498db"
                recs = rec.get('recommendations', [])
                rec_text = ', '.join(recs[:3]) if recs else "No recommendations"
                
                st.markdown(f"""
                <div style="background:{bg_color}; padding:15px; border-radius:10px; border-left:4px solid {border_color}; margin-bottom:10px;">
                    <strong>👤 {rec.get('customer_name', 'Unknown')}</strong>
                    <span style="float:right;"><strong>{risk}</strong></span><br>
                    <span style="font-size:0.9rem;">{rec_text}</span>
                </div>
                """, unsafe_allow_html=True)
    except:
        st.error("⚠️ Could not connect to API.")

# -------------------- REPORTS PAGE --------------------
elif page == "📊 Reports":
    st.markdown("## 📊 Generate Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Generate Monthly Report"):
            try:
                response = requests.get(f"{API_URL}/api/reports/monthly", headers=headers, timeout=5)
                if response.status_code == 200:
                    st.json(response.json())
            except:
                st.error("⚠️ Could not connect to API.")
    
    with col2:
        if st.button("📊 Generate Excel Report"):
            try:
                response = requests.get(f"{API_URL}/api/reports/excel", headers=headers, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"✅ Report generated: {data.get('filepath', '')}")
            except:
                st.error("⚠️ Could not connect to API.")

st.markdown("---")
st.caption("© 2026 CARIS - Customer Churn Analytics & Retention Intelligence System")