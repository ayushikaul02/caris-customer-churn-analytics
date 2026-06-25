import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import json

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="CARIS - Enterprise Churn Analytics", page_icon="📊", layout="wide", initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown(
    """
<style>
    /* Main Header */
    .main-header {
        font-size: 2.2rem;
        color: white;
        text-align: center;
        padding: 1.2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        margin-bottom: 2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
    }

    /* Business Impact Cards */
    .impact-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        text-align: center;
        transition: all 0.3s ease;
    }
    .impact-card:hover {
        transform: translateY(-5px);
        border-color: rgba(102, 126, 234, 0.3);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.15);
    }
    .impact-value {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .impact-label {
        color: rgba(255,255,255,0.6);
        font-size: 0.9rem;
        margin-top: 0.3rem;
    }
    .impact-sub {
        color: rgba(255,255,255,0.3);
        font-size: 0.75rem;
        margin-top: 0.2rem;
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(255,255,255,0.03);
        padding: 1.2rem;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.05);
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        background: rgba(255,255,255,0.06);
        border-color: rgba(102, 126, 234, 0.2);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: white;
    }
    .metric-label {
        color: rgba(255,255,255,0.5);
        font-size: 0.8rem;
        margin-top: 0.2rem;
    }

    /* Login Container */
    .login-container {
        max-width: 420px;
        margin: 80px auto;
        padding: 40px;
        background: rgba(255,255,255,0.03);
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.06);
        backdrop-filter: blur(10px);
    }
    .login-title {
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        color: white;
        margin-bottom: 30px;
    }
    .login-title span {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Recommendations */
    .rec-card {
        padding: 15px 20px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 4px solid;
        transition: all 0.3s ease;
    }
    .rec-card:hover {
        transform: translateX(5px);
    }
    .rec-critical { background: rgba(239, 68, 68, 0.1); border-color: #ef4444; }
    .rec-high { background: rgba(239, 68, 68, 0.08); border-color: #ef4444; }
    .rec-medium { background: rgba(245, 158, 11, 0.08); border-color: #f59e0b; }
    .rec-low { background: rgba(16, 185, 129, 0.08); border-color: #10b981; }

    /* Section Headers */
    .section-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: white;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-title .line {
        flex: 1;
        height: 1px;
        background: rgba(255,255,255,0.06);
    }

    /* Sidebar */
    .sidebar-content {
        padding: 10px 0;
    }
    .sidebar-user {
        padding: 12px;
        background: rgba(255,255,255,0.03);
        border-radius: 8px;
        margin-bottom: 15px;
        text-align: center;
    }
    .sidebar-user .name {
        color: white;
        font-weight: 600;
    }
    .sidebar-user .role {
        color: rgba(255,255,255,0.4);
        font-size: 0.8rem;
    }

    /* Button Styles */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 10px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
    }

    /* Dataframe */
    .stDataFrame {
        background: rgba(255,255,255,0.02);
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.05);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.03);
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        color: rgba(255,255,255,0.6);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==================== API CONFIG ====================
API_URL = os.getenv("API_URL", "https://caris-api.onrender.com")

# ==================== SESSION STATE ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "token" not in st.session_state:
    st.session_state.token = ""
if "username" not in st.session_state:
    st.session_state.username = ""

# ==================== LOGIN ====================
if not st.session_state.logged_in:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🔐 <span>CARIS</span></div>', unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username", placeholder="admin", label_visibility="collapsed")
        password = st.text_input("Password", type="password", placeholder="••••••••", label_visibility="collapsed")
        st.markdown("")
        submit = st.form_submit_button("Login")

        if submit:
            try:
                response = requests.post(
                    f"{API_URL}/api/auth/login", json={"username": username, "password": password}, timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.token = data.get("access_token")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
            except Exception as e:
                st.error(f"❌ Connection error: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==================== HEADER ====================
st.markdown(
    '<div class="main-header">📊 CARIS — Customer Churn Analytics & Retention Intelligence</div>', unsafe_allow_html=True
)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)

    st.image("https://img.icons8.com/color/96/000000/data-configuration.png", width=70)

    st.markdown(
        f"""
    <div class="sidebar-user">
        <div class="name">👤 {st.session_state.username}</div>
        <div class="role">Administrator</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    page = st.radio("Navigation", ["📊 Overview", "👥 Customers", "📈 Analytics", "🎯 Retention", "📋 Reports"], index=0)

    st.markdown("---")

    st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.caption("🚀 CARIS v2.0")

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.token = ""
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

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


# ==================== LOAD DATA ====================
with st.spinner("Loading data..."):
    customers_data = fetch_data("/api/customers?limit=100")
    metrics = fetch_data("/api/dashboard/metrics")
    churn_data = fetch_data("/api/analytics/churn")
    segments = fetch_data("/api/analytics/customer-segments", method="POST")


# ==================== CALCULATE BUSINESS METRICS ====================
def calculate_business_impact(metrics):
    """Calculate business impact metrics"""
    impact = {}

    if metrics:
        total_customers = metrics.get("customer_kpis", {}).get("total_customers", 0)
        churn_rate = metrics.get("churn_kpis", {}).get("churn_rate", 0)
        avg_revenue = metrics.get("revenue_kpis", {}).get("avg_revenue_per_customer", 0)
        high_risk = metrics.get("churn_kpis", {}).get("high_risk_customers", 0)

        # Revenue at risk
        revenue_at_risk = high_risk * avg_revenue

        # Potential savings (assuming 50% retention improvement)
        potential_savings = revenue_at_risk * 0.5

        impact["revenue_at_risk"] = revenue_at_risk
        impact["potential_savings"] = potential_savings
        impact["high_risk_count"] = high_risk
        impact["churn_rate"] = churn_rate
        impact["avg_revenue"] = avg_revenue

    return impact


business_impact = calculate_business_impact(metrics)

# ==================== PAGES ====================

# -------------------- OVERVIEW --------------------
if page == "📊 Overview":
    st.markdown("## 📊 Executive Dashboard")

    # Business Impact Row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
        <div class="impact-card">
            <div class="impact-value">${business_impact.get('revenue_at_risk', 0):,.0f}</div>
            <div class="impact-label">💰 Revenue at Risk</div>
            <div class="impact-sub">From {business_impact.get('high_risk_count', 0)} high-risk customers</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
        <div class="impact-card">
            <div class="impact-value" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;">${business_impact.get('potential_savings', 0):,.0f}</div>
            <div class="impact-label">🎯 Potential Savings</div>
            <div class="impact-sub">With 50% retention improvement</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
        <div class="impact-card">
            <div class="impact-value">{business_impact.get('churn_rate', 0)*100:.1f}%</div>
            <div class="impact-label">📉 Current Churn Rate</div>
            <div class="impact-sub">Industry avg: ~15-20%</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
        <div class="impact-card">
            <div class="impact-value">${business_impact.get('avg_revenue', 0):,.0f}</div>
            <div class="impact-label">💳 Avg Customer Value</div>
            <div class="impact-sub">Per customer lifetime</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # KPIs
    st.markdown(
        '<div class="section-title">📈 Key Performance Indicators <span class="line"></span></div>', unsafe_allow_html=True
    )

    if metrics:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                f"""
            <div class="metric-card">
                <div class="metric-value">{metrics.get('customer_kpis', {}).get('total_customers', 0):,}</div>
                <div class="metric-label">👥 Total Customers</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
            <div class="metric-card">
                <div class="metric-value">{metrics.get('customer_kpis', {}).get('active_customers', 0):,}</div>
                <div class="metric-label">✅ Active Customers</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col3:
            churn_rate = metrics.get("churn_kpis", {}).get("churn_rate", 0) * 100
            color = "#ef4444" if churn_rate > 15 else "#f59e0b" if churn_rate > 10 else "#10b981"
            st.markdown(
                f"""
            <div class="metric-card">
                <div class="metric-value" style="color:{color}">{churn_rate:.1f}%</div>
                <div class="metric-label">📉 Churn Rate</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col4:
            revenue = metrics.get("revenue_kpis", {}).get("total_revenue", 0)
            st.markdown(
                f"""
            <div class="metric-card">
                <div class="metric-value">${revenue:,.0f}</div>
                <div class="metric-label">💰 Total Revenue</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">📊 Customer Segments <span class="line"></span></div>', unsafe_allow_html=True)
        if segments and "segments" in segments:
            seg_data = segments["segments"]
            fig = px.pie(
                values=list(seg_data.values()),
                names=list(seg_data.keys()),
                title="",
                color_discrete_sequence=px.colors.sequential.Blues_r,
                hole=0.4,
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="rgba(255,255,255,0.7)",
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2),
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">📊 Customer Status <span class="line"></span></div>', unsafe_allow_html=True)
        if metrics and "segment_kpis" in metrics:
            status_data = metrics["segment_kpis"].get("status_distribution", {})
            if status_data:
                colors_map = {"active": "#10b981", "inactive": "#f59e0b", "churned": "#ef4444", "suspended": "#8b5cf6"}
                colors = [colors_map.get(k, "#6b7280") for k in status_data.keys()]
                fig = px.bar(
                    x=list(status_data.keys()),
                    y=list(status_data.values()),
                    title="",
                    color=list(status_data.keys()),
                    color_discrete_sequence=colors,
                    text_auto=True,
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="rgba(255,255,255,0.7)",
                    showlegend=False,
                    yaxis_title="",
                    xaxis_title="",
                )
                st.plotly_chart(fig, use_container_width=True)

# -------------------- CUSTOMERS --------------------
elif page == "👥 Customers":
    st.markdown("## 👥 Customer Management")

    if customers_data:
        df = pd.DataFrame(customers_data)

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            segment_filter = st.selectbox("Filter by Segment", ["All"] + list(df["customer_segment"].unique()))
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All"] + list(df["status"].unique()))
        with col3:
            search = st.text_input("Search", placeholder="Name or Email...")

        # Apply filters
        filtered_df = df.copy()
        if segment_filter != "All":
            filtered_df = filtered_df[filtered_df["customer_segment"] == segment_filter]
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df["status"] == status_filter]
        if search:
            filtered_df = filtered_df[
                filtered_df["name"].str.contains(search, case=False) | filtered_df["email"].str.contains(search, case=False)
            ]

        st.markdown(f"**Showing {len(filtered_df)} customers**")

        # Display table
        st.dataframe(
            filtered_df[["customer_id", "name", "email", "customer_segment", "status", "total_spent"]],
            use_container_width=True,
            height=400,
            column_config={"customer_id": "ID", "total_spent": st.column_config.NumberColumn("Total Spent", format="$%.2f")},
        )

        # Quick stats
        st.caption(
            f"📊 {len(filtered_df)} customers • {filtered_df['customer_segment'].nunique()} segments • ${filtered_df['total_spent'].sum():,.2f} total spend"
        )
    else:
        st.warning("No customer data available.")

# -------------------- ANALYTICS --------------------
elif page == "📈 Analytics":
    st.markdown("## 📈 Churn & Revenue Analytics")

    tab1, tab2, tab3 = st.tabs(["📉 Churn Analysis", "💰 Revenue Analysis", "🔬 Model Explainability"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Churn by Segment")
            if churn_data and "churn_by_segment" in churn_data:
                churn_seg = churn_data["churn_by_segment"]
                fig = px.bar(
                    x=list(churn_seg.keys()),
                    y=list(churn_seg.values()),
                    title="",
                    labels={"x": "Segment", "y": "Churn Rate"},
                    color=list(churn_seg.keys()),
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    text_auto=".1%",
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="rgba(255,255,255,0.7)",
                    showlegend=False,
                    yaxis_tickformat=".0%",
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Risk Distribution")
            if metrics and "churn_kpis" in metrics:
                high_risk = metrics["churn_kpis"].get("high_risk_customers", 0)
                total = metrics.get("customer_kpis", {}).get("total_customers", 0)
                risk_data = {"Low Risk": total - high_risk, "High Risk": high_risk}
                fig = px.pie(
                    values=list(risk_data.values()),
                    names=list(risk_data.keys()),
                    title="",
                    color=list(risk_data.keys()),
                    color_discrete_map={"Low Risk": "#10b981", "High Risk": "#ef4444"},
                    hole=0.4,
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="rgba(255,255,255,0.7)",
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2),
                )
                st.plotly_chart(fig, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Revenue by Segment")
            if metrics and "revenue_kpis" in metrics:
                if "segment_kpis" in metrics:
                    seg_rev = metrics.get("segment_kpis", {}).get("segment_distribution", {})
                    if seg_rev:
                        fig = px.pie(
                            values=list(seg_rev.values()),
                            names=list(seg_rev.keys()),
                            title="",
                            color_discrete_sequence=px.colors.sequential.Greens_r,
                            hole=0.4,
                        )
                        fig.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            font_color="rgba(255,255,255,0.7)",
                            showlegend=True,
                            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
                        )
                        st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Top Customers")
            if customers_data:
                df = pd.DataFrame(customers_data)
                top_customers = df.nlargest(10, "total_spent")
                fig = px.bar(
                    top_customers,
                    x="name",
                    y="total_spent",
                    title="",
                    labels={"name": "Customer", "total_spent": "Total Spend"},
                    color="total_spent",
                    color_continuous_scale="Blues",
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="rgba(255,255,255,0.7)",
                    showlegend=False,
                    xaxis_tickangle=-45,
                )
                st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.markdown("### 🔬 Model Explainability (SHAP Analysis)")
        st.caption("SHAP (SHapley Additive exPlanations) shows which features most influence churn prediction")

        col1, col2 = st.columns(2)

        with col1:
            # Check if SHAP images exist
            import os

            if os.path.exists("shap_feature_importance.png"):
                st.image("shap_feature_importance.png", caption="Feature Importance - SHAP Values", use_container_width=True)
            else:
                st.info("SHAP image not found. Run `python scripts/shap_analysis.py` to generate.")

        with col2:
            if os.path.exists("shap_feature_importance_bar.png"):
                st.image("shap_feature_importance_bar.png", caption="Feature Importance - Bar Chart", use_container_width=True)
            else:
                st.info("SHAP image not found. Run `python scripts/shap_analysis.py` to generate.")

        st.markdown("---")
        st.markdown("#### 📊 Key Insights from SHAP Analysis")
        st.markdown("""
        - **Total Spent** is the strongest predictor of churn
        - **Monthly Charge** significantly impacts retention
        - **Age** has moderate influence on churn behavior
        - Higher spending customers are more likely to stay
        - Newer customers are at higher risk of churning
        """)

# -------------------- RETENTION --------------------
elif page == "🎯 Retention":
    st.markdown("## 🎯 Retention Recommendations")

    recs = fetch_data("/api/retention/recommendations", method="POST")

    if recs:
        risk_filter = st.selectbox("Filter by Risk Level", ["All", "Critical", "High", "Medium", "Low"])

        if risk_filter != "All":
            recs = [r for r in recs if r.get("risk_level") == risk_filter]

        st.markdown(f"**Showing {len(recs)} recommendations**")

        for rec in recs[:10]:
            risk = rec.get("risk_level", "Unknown")
            risk_class = f"rec-{risk.lower()}" if risk.lower() in ["critical", "high", "medium", "low"] else ""
            recs_list = rec.get("recommendations", [])
            rec_text = ", ".join(recs_list[:3]) if recs_list else "No recommendations"

            st.markdown(
                f"""
            <div class="rec-card {risk_class}">
                <strong>👤 {rec.get('customer_name', 'Unknown')}</strong>
                <span style="float:right; font-size:0.8rem; color:rgba(255,255,255,0.4);">
                    {risk}
                </span><br>
                <span style="font-size:0.9rem; color:rgba(255,255,255,0.6);">
                    {rec_text}
                </span>
            </div>
            """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No recommendations available")

# -------------------- REPORTS --------------------
elif page == "📋 Reports":
    st.markdown("## 📋 Reports")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📄 Monthly Report")
        if st.button("Generate Monthly Report"):
            report = fetch_data("/api/reports/monthly")
            if report:
                st.json(report)

    with col2:
        st.markdown("### 📊 Excel Report")
        if st.button("Generate Excel Report"):
            excel = fetch_data("/api/reports/excel")
            if excel:
                st.success(f"✅ Report generated")
                st.info(f"📁 {excel.get('filepath', '')}")

# ==================== FOOTER ====================
st.markdown("---")
st.caption("© 2026 CARIS — Enterprise Customer Churn Analytics & Retention Intelligence System")
