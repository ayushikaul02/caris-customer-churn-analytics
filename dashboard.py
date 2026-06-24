import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime
import os
import json

# Page config
st.set_page_config(
    page_title="CARIS - Customer Churn Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: white;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1a365d;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #718096;
        margin-top: 5px;
    }
    .metric-icon {
        font-size: 2rem;
        margin-bottom: 5px;
    }
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 40px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .login-title {
        text-align: center;
        font-size: 2rem;
        color: #1a365d;
        margin-bottom: 30px;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 10px;
    }
    .stButton > button:hover {
        transform: scale(1.02);
    }
    .recommendation-card {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 4px solid;
    }
    .risk-critical { background: #fdedec; border-color: #e74c3c; }
    .risk-high { background: #fdedec; border-color: #e74c3c; }
    .risk-medium { background: #fef9e7; border-color: #f39c12; }
    .risk-low { background: #ebf5fb; border-color: #3498db; }
</style>
""", unsafe_allow_html=True)

# ==================== API CONFIG ====================
API_URL = os.getenv("API_URL", "https://caris-api.onrender.com")

# ==================== SESSION STATE ====================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'token' not in st.session_state:
    st.session_state.token = ""
if 'username' not in st.session_state:
    st.session_state.username = ""

# ==================== LOGIN ====================
if not st.session_state.logged_in:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🔐 CARIS Login</div>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="admin")
        password = st.text_input("Password", type="password", placeholder="admin123")
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
            except Exception as e:
                st.error(f"❌ Could not connect to server: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==================== HEADER ====================
st.markdown('<div class="main-header">📊 CARIS - Customer Churn Analytics</div>', unsafe_allow_html=True)

# ==================== SIDEBAR ====================
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
        st.session_state.token = ""
        st.rerun()
    
    st.caption(f"🕐 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.caption("🚀 CARIS v1.0.0")

# ==================== API HELPERS ====================
headers = {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}

@st.cache_data(ttl=300)
def fetch_data(endpoint, method="GET", data=None):
    try:
        if method == "GET":
            response = requests.get(f"{API_URL}{endpoint}", headers=headers, timeout=10)
        else:
            response = requests.post(f"{API_URL}{endpoint}", headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"⚠️ API Error: {e}")
        return None

# ==================== DATA LOADING ====================
with st.spinner("Loading data..."):
    customers_data = fetch_data("/api/customers?limit=100")
    metrics = fetch_data("/api/dashboard/metrics")
    churn_data = fetch_data("/api/analytics/churn")
    segments = fetch_data("/api/analytics/customer-segments", method="POST")

# ==================== OVERVIEW PAGE ====================
if page == "🏠 Overview":
    st.markdown("## 📊 Executive Dashboard")
    
    if metrics:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">👥</div>
                <div class="metric-value">{metrics.get('customer_kpis', {}).get('total_customers', 0)}</div>
                <div class="metric-label">Total Customers</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">✅</div>
                <div class="metric-value">{metrics.get('customer_kpis', {}).get('active_customers', 0)}</div>
                <div class="metric-label">Active Customers</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            churn_rate = metrics.get('churn_kpis', {}).get('churn_rate', 0) * 100
            color = "#e74c3c" if churn_rate > 15 else "#f39c12" if churn_rate > 10 else "#27ae60"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📉</div>
                <div class="metric-value" style="color:{color}">{churn_rate:.1f}%</div>
                <div class="metric-label">Churn Rate</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            revenue = metrics.get('revenue_kpis', {}).get('total_revenue', 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">💰</div>
                <div class="metric-value">${revenue:,.0f}</div>
                <div class="metric-label">Total Revenue</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Customer Segments")
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
            st.subheader("📊 Status Distribution")
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

# ==================== CUSTOMERS PAGE ====================
elif page == "👥 Customers":
    st.markdown("## 👥 Customer Management")
    
    if customers_data:
        df = pd.DataFrame(customers_data)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            segment_filter = st.selectbox("Segment", ["All"] + list(df['customer_segment'].unique()))
        with col2:
            status_filter = st.selectbox("Status", ["All"] + list(df['status'].unique()))
        with col3:
            search = st.text_input("Search", placeholder="Name or Email...")
        
        filtered_df = df.copy()
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

# ==================== ANALYTICS PAGE ====================
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
                title="Churn Rate by Segment",
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
            fig = px.pie(
                values=list(risk_data.values()),
                names=list(risk_data.keys()),
                title="Risk Distribution",
                color=list(risk_data.keys()),
                color_discrete_map={'Low Risk': '#27ae60', 'High Risk': '#e74c3c'}
            )
            st.plotly_chart(fig, use_container_width=True)

# ==================== RETENTION PAGE ====================
elif page == "🎯 Retention":
    st.markdown("## 🎯 Retention Recommendations")
    
    recs = fetch_data("/api/retention/recommendations", method="POST")
    
    if recs:
        risk_filter = st.selectbox("Filter by Risk Level", ["All", "Critical", "High", "Medium", "Low"])
        if risk_filter != "All":
            recs = [r for r in recs if r.get('risk_level') == risk_filter]
        
        for rec in recs[:10]:
            risk = rec.get('risk_level', 'Unknown')
            risk_class = f"risk-{risk.lower()}" if risk.lower() in ['critical', 'high', 'medium', 'low'] else ""
            bg_color = "#fdedec" if risk in ['Critical', 'High'] else "#fef9e7" if risk == 'Medium' else "#ebf5fb"
            border_color = "#e74c3c" if risk in ['Critical', 'High'] else "#f39c12" if risk == 'Medium' else "#3498db"
            recs_list = rec.get('recommendations', [])
            rec_text = ', '.join(recs_list[:3]) if recs_list else "No recommendations"
            
            st.markdown(f"""
            <div style="background:{bg_color}; padding:15px; border-radius:10px; border-left:4px solid {border_color}; margin-bottom:10px;">
                <strong>👤 {rec.get('customer_name', 'Unknown')}</strong>
                <span style="float:right; font-weight:bold; color:{border_color};">{risk}</span><br>
                <span style="font-size:0.9rem; color:#555;">{rec_text}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recommendations available")

# ==================== REPORTS PAGE ====================
elif page == "📊 Reports":
    st.markdown("## 📊 Generate Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Generate Monthly Report"):
            report = fetch_data("/api/reports/monthly")
            if report:
                st.json(report)
    
    with col2:
        if st.button("📊 Generate Excel Report"):
            excel = fetch_data("/api/reports/excel")
            if excel:
                st.success(f"✅ Report generated: {excel.get('filepath', '')}")

# ==================== FOOTER ====================
st.markdown("---")
st.caption("© 2026 CARIS - Customer Churn Analytics & Retention Intelligence System")