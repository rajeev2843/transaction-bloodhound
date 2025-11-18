import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils import (
    generate_mock_vendors,
    calculate_vendor_risk_score,
    get_risk_level,
    get_risk_color,
    check_compliance_breaches,
    mock_gstn_api_call,
    mock_mca_api_call,
    process_tally_data
)

st.set_page_config(
    page_title="Transaction Bloodhound - GST Compliance Monitor",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

if 'vendors' not in st.session_state:
    st.session_state.vendors = generate_mock_vendors(20)

if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = set()

def main():
    st.title("🔍 Transaction Bloodhound")
    st.markdown("### Real-Time Supply Chain Audit & GST Compliance Monitor")
    st.markdown("*Preventing ITC Fraud Before It Happens*")
    
    with st.sidebar:
        st.header("📍 Navigation")
        page = st.radio(
            "Select View",
            ["🏠 Dashboard", "📊 Vendor Risk Analysis", "🚨 Critical Alerts", 
             "👁️ Watchlist", "📤 Upload Tally Data", "🔍 Vendor Details"]
        )
        
        st.divider()
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh", use_container_width=True):
                for vendor in st.session_state.vendors:
                    vendor['risk_score'], vendor['risk_factors'] = calculate_vendor_risk_score(vendor)
                    vendor['risk_level'] = get_risk_level(vendor['risk_score'])
                st.success("✅ Updated!")
                st.rerun()
        
        with col2:
            if st.button("🆕 New Vendor", use_container_width=True):
                new_vendor = generate_mock_vendors(1)[0]
                st.session_state.vendors.insert(0, new_vendor)
                st.success(f"✅ Added!")
                st.rerun()
        
        vendors_df = pd.DataFrame(st.session_state.vendors)
        st.divider()
        st.markdown("### 📈 Quick Stats")
        critical_count = len(vendors_df[vendors_df['risk_level'] == 'Critical'])
        high_risk_count = len(vendors_df[vendors_df['risk_level'] == 'High Risk'])
        
        st.metric("Total Vendors", len(vendors_df))
        st.metric("🔴 Critical", critical_count)
        st.metric("🟠 High Risk", high_risk_count)
        
        st.divider()
        st.markdown("**💡 Demo Version**")
        st.caption("Built for ICAI Aurathon 2025")
    
    if "Dashboard" in page:
        show_dashboard()
    elif "Vendor Risk" in page:
        show_vendor_risk_analysis()
    elif "Critical Alerts" in page:
        show_critical_alerts()
    elif "Watchlist" in page:
        show_watchlist()
    elif "Upload Tally" in page:
        show_upload_tally_data()
    elif "Vendor Details" in page:
        show_vendor_details()

def show_dashboard():
    vendors_df = pd.DataFrame(st.session_state.vendors)
    
    critical_vendors = vendors_df[vendors_df['risk_level'] == 'Critical']
    high_risk_vendors = vendors_df[vendors_df['risk_level'] == 'High Risk']
    total_itc_at_risk = vendors_df[vendors_df['risk_level'].isin(['Critical', 'High Risk'])]['itc_amount'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Vendors", len(vendors_df))
    with col2:
        st.metric("🚨 Critical Alerts", len(critical_vendors), 
                 delta=f"{len(critical_vendors)}", delta_color="inverse")
    with col3:
        st.metric("⚠️ High Risk", len(high_risk_vendors),
                 delta=f"{len(high_risk_vendors)}", delta_color="inverse")
    with col4:
        st.metric("💰 ITC at Risk", f"₹{total_itc_at_risk/100000:.1f}L",
                 delta=f"₹{total_itc_at_risk/100000:.1f}L", delta_color="inverse")
    
    st.divider()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Vendor Risk Distribution")
        risk_counts = vendors_df['risk_level'].value_counts().reset_index()
        risk_counts.columns = ['Risk Level', 'Count']
        
        color_map = {
            'Critical': '#FF4444',
            'High Risk': '#FFA500',
            'Medium Risk': '#FFD700',
            'Low Risk': '#90EE90'
        }
        
        fig = px.bar(risk_counts, x='Risk Level', y='Count',
                    color='Risk Level',
                    color_discrete_map=color_map,
                    text='Count')
        fig.update_traces(textposition='outside')
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Risk Score Distribution")
        fig = go.Figure(data=[go.Pie(
            labels=['Critical (90-100)', 'High (70-89)', 'Medium (40-69)', 'Low (0-39)'],
            values=[
                len(vendors_df[vendors_df['risk_score'] >= 90]),
                len(vendors_df[(vendors_df['risk_score'] >= 70) & (vendors_df['risk_score'] < 90)]),
                len(vendors_df[(vendors_df['risk_score'] >= 40) & (vendors_df['risk_score'] < 70)]),
                len(vendors_df[vendors_df['risk_score'] < 40])
            ],
            marker=dict(colors=['#FF4444', '#FFA500', '#FFD700', '#90EE90']),
            hole=0.4
        )])
        fig.update_layout(height=350, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    st.subheader("🔴 Critical Alerts - Immediate Action Required")
    
    if len(critical_vendors) > 0:
        for idx, vendor in critical_vendors.head(5).iterrows():
            with st.expander(f"⚠️ CRITICAL: {vendor['name']} (GSTIN: {vendor['gstin']}) - Risk Score: {vendor['risk_score']}", expanded=(idx==critical_vendors.index[0])):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Registration Age:** {vendor['registration_days']} days")
                    st.markdown(f"**ITC Amount:** ₹{vendor['itc_amount']:,.0f}")
                with col2:
                    st.markdown(f"**GSTR-3B Status:** {vendor['gstr3b_status']}")
                    st.markdown(f"**Transaction Count:** {vendor['transaction_count']}")
                with col3:
                    st.markdown(f"**Director Companies:** {vendor['director_companies']}")
                    st.markdown(f"**Address Type:** {vendor['address_type']}")
                
                st.markdown("**🔍 Risk Factors:**")
                for factor in vendor['risk_factors']:
                    st.markdown(f"- {factor}")
                
                st.markdown("**🛑 Recommended Actions:**")
                actions = get_recommended_actions(vendor)
                for action in actions[:3]:
                    st.error(f"🛑 {action}")
    else:
        st.success("✅ No critical alerts at this time")
    
    st.divider()
    st.subheader("📋 All Vendors Overview")
    
    display_df = vendors_df[['name', 'gstin', 'risk_level', 'risk_score', 'itc_amount', 
                             'registration_days', 'gstr3b_status', 'transaction_count']].copy()
    display_df.columns = ['Vendor Name', 'GSTIN', 'Risk Level', 'Risk Score', 'ITC Amount (₹)', 
                          'Reg. Age (days)', 'GSTR-3B Status', 'Transactions']
    display_df = display_df.sort_values('Risk Score', ascending=False)
    
    st.dataframe(display_df, use_container_width=True, height=400)

def show_vendor_risk_analysis():
    st.subheader("🎯 Detailed Vendor Risk Analysis")
    
    vendors_df = pd.DataFrame(st.session_state.vendors)
    
    risk_filter = st.multiselect(
        "Filter by Risk Level",
        options=['Critical', 'High Risk', 'Medium Risk', 'Low Risk'],
        default=['Critical', 'High Risk']
    )
    
    filtered_df = vendors_df[vendors_df['risk_level'].isin(risk_filter)] if risk_filter else vendors_df
    filtered_df = filtered_df.sort_values('risk_score', ascending=False)
    
    st.markdown(f"**Showing {len(filtered_df)} vendors**")
    st.divider()
    
    for idx, vendor in filtered_df.head(10).iterrows():
        risk_color = get_risk_color(vendor['risk_level'])
        
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {vendor['name']}")
            with col2:
                st.markdown(f"<h3 style='text-align: right; color: {risk_color};'>{vendor['risk_level']}</h3>", unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Risk Score", f"{vendor['risk_score']}/100")
            with col2:
                st.metric("ITC Exposure", f"₹{vendor['itc_amount']/1000:.0f}K")
            with col3:
                st.metric("Registration Age", f"{vendor['registration_days']} days")
            with col4:
                st.metric("Transactions", vendor['transaction_count'])
            
            with st.expander("📊 Detailed Risk Analysis"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Vendor Information**")
                    st.markdown(f"- **GSTIN:** {vendor['gstin']}")
                    st.markdown(f"- **Registered:** {vendor['registration_days']} days ago")
                    st.markdown(f"- **Address Type:** {vendor['address_type']}")
                    st.markdown(f"- **Director Companies:** {vendor['director_companies']}")
                
                with col2:
                    st.markdown("**Risk Factors Identified**")
                    for factor in vendor['risk_factors'][:5]:
                        st.markdown(f"- ⚠️ {factor}")
                
                breaches = check_compliance_breaches(vendor)
                if breaches:
                    st.markdown("**⚠️ Compliance Breaches**")
                    for breach in breaches:
                        st.warning(breach)
            
            st.divider()

def show_critical_alerts():
    st.subheader("🚨 Critical Alerts & Immediate Actions")
    
    vendors_df = pd.DataFrame(st.session_state.vendors)
    critical_vendors = vendors_df[vendors_df['risk_level'].isin(['Critical', 'High Risk'])].sort_values('risk_score', ascending=False)
    
    if len(critical_vendors) == 0:
        st.success("✅ No critical alerts at this time.")
        return
    
    st.markdown(f"**{len(critical_vendors)} Alerts Require Attention**")
    st.divider()
    
    for idx, vendor in critical_vendors.head(10).iterrows():
        alert_level = "🔴 CRITICAL ALERT" if vendor['risk_score'] >= 90 else "⚠️ HIGH RISK ALERT"
        
        with st.container():
            st.markdown(f"## {alert_level}")
            st.markdown(f"### {vendor['name']} (GSTIN: {vendor['gstin']})")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Risk Score", f"{vendor['risk_score']}/100")
            with col2:
                st.metric("ITC at Risk", f"₹{vendor['itc_amount']/100000:.2f}L")
            with col3:
                st.metric("Days Since Registration", vendor['registration_days'])
            
            st.markdown("**🔍 Risk Analysis:**")
            for factor in vendor['risk_factors']:
                st.markdown(f"- ⚠️ {factor}")
            
            st.markdown("**🛑 IMMEDIATE ACTIONS REQUIRED:**")
            actions = get_recommended_actions(vendor)
            for action in actions[:4]:
                st.error(action)
            
            with st.expander("🔍 Live API Verification Results"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**GSTN API Response**")
                    st.json(mock_gstn_api_call(vendor['gstin']))
                with col2:
                    st.markdown("**MCA API Response**")
                    st.json(mock_mca_api_call(vendor['gstin']))
            
            st.divider()

def show_watchlist():
    st.subheader("👁️ Vendor Watchlist - Enhanced Monitoring")
    
    vendors_df = pd.DataFrame(st.session_state.vendors)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Add Vendor to Watchlist")
        vendor_names = vendors_df['name'].tolist()
        selected_vendor_name = st.selectbox("Select Vendor", vendor_names)
        
        if st.button("➕ Add to Watchlist", use_container_width=True):
            selected_vendor = vendors_df[vendors_df['name'] == selected_vendor_name].iloc[0]
            st.session_state.watchlist.add(selected_vendor['gstin'])
            st.success(f"✅ Added to watchlist")
            st.rerun()
    
    with col2:
        st.metric("Vendors on Watchlist", len(st.session_state.watchlist))
        
        if st.button("🗑️ Clear Watchlist", use_container_width=True):
            st.session_state.watchlist.clear()
            st.rerun()
    
    st.divider()
    
    if len(st.session_state.watchlist) == 0:
        st.info("📝 No vendors on watchlist.")
        return
    
    watchlist_vendors = vendors_df[vendors_df['gstin'].isin(st.session_state.watchlist)]
    
    for idx, vendor in watchlist_vendors.iterrows():
        with st.container():
            st.markdown(f"### {vendor['name']}")
            st.markdown(f"**Risk Level:** {vendor['risk_level']} | **Score:** {vendor['risk_score']}/100")
            
            if st.button("🗑️ Remove", key=f"remove_{vendor['gstin']}"):
                st.session_state.watchlist.discard(vendor['gstin'])
                st.rerun()
            
            st.divider()

def show_upload_tally_data():
    st.subheader("📤 Upload Tally Purchase Ledger Data")
    
    st.markdown("""
    Upload your Tally export (CSV/Excel) with vendor transactions.
    Required columns: Vendor Name, GSTIN, Transaction Amount
    """)
    
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ Found {len(df)} transactions")
            st.dataframe(df.head(10), use_container_width=True)
            
            if st.button("🔍 Process & Analyze"):
                with st.spinner("Processing..."):
                    new_count, updated_count = process_tally_data(df)
                    st.success(f"✅ {new_count} new, {updated_count} updated")
                    st.balloons()
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.divider()
    st.markdown("### 📥 Download Sample Template")
    
    sample_data = {
        'Vendor Name': ['ABC Suppliers', 'XYZ Traders'],
        'GSTIN': ['27AABCU9603R1ZX', '29ABCDE1234F1Z5'],
        'Transaction Amount': [150000, 85000],
        'Tax Amount': [27000, 15300]
    }
    
    sample_df = pd.DataFrame(sample_data)
    csv = sample_df.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="📄 Download CSV Template",
        data=csv,
        file_name="tally_template.csv",
        mime="text/csv"
    )

def show_vendor_details():
    st.subheader("🔍 Detailed Vendor Information")
    
    vendors_df = pd.DataFrame(st.session_state.vendors)
    vendor_names = vendors_df['name'].tolist()
    selected_vendor = st.selectbox("Select Vendor", vendor_names)
    
    vendor = vendors_df[vendors_df['name'] == selected_vendor].iloc[0]
    risk_color = get_risk_color(vendor['risk_level'])
    
    st.markdown(f"## {vendor['name']}")
    st.markdown(f"**GSTIN:** {vendor['gstin']}")
    st.markdown(f"**Risk Level:** {vendor['risk_level']} | **Score:** {vendor['risk_score']}/100")
    
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("ITC Exposure", f"₹{vendor['itc_amount']/100000:.2f}L")
    with col2:
        st.metric("Transactions", vendor['transaction_count'])
    with col3:
        st.metric("Registration Age", f"{vendor['registration_days']} days")
    with col4:
        st.metric("Director Companies", vendor['director_companies'])
    
    st.divider()
    
    st.markdown("### 🎯 Risk Assessment")
    st.progress(vendor['risk_score'] / 100)
    
    st.markdown("**Risk Factors:**")
    for factor in vendor['risk_factors']:
        st.markdown(f"- ⚠️ {factor}")
    
    st.markdown("### 🛑 Recommended Actions")
    for action in get_recommended_actions(vendor):
        st.info(action)

def get_recommended_actions(vendor):
    actions = []
    
    if vendor['risk_score'] >= 90:
        actions.append("BLOCK ALL PAYMENTS - Do not process further transactions")
    
    if vendor['registration_days'] < 30:
        actions.append("NEW VENDOR - Conduct enhanced due diligence")
    
    if vendor['months_not_filed'] > 2:
        actions.append(f"FILING RISK - {vendor['months_not_filed']} months non-filing")
    
    if vendor['director_companies'] > 20:
        actions.append("SHELL COMPANY RISK - Multiple director companies")
    
    if not actions:
        actions.append("Continue monitoring")
    
    return actions

if __name__ == "__main__":
    main()
