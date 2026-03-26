"""
Streamlit Dashboard for Agentic Feedback System
Provides monitoring, analytics, configuration, and manual override capabilities
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from config import DATA_PATHS, CLASSIFICATION_CONFIG, PRIORITY_CONFIG
from utils.logger import logger
import json

st.set_page_config(
    page_title="Agentic Feedback System",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>🎫 Intelligent Feedback Dashboard</h1><p>Multi-Agent Classification System with Real-Time Monitoring</p></div>', unsafe_allow_html=True)

# Sidebar for configuration and controls
with st.sidebar:
    st.header("⚙️ System Configuration")
    
    # Configuration Panel
    with st.expander("📝 Edit Classification Config", expanded=False):
        st.write("**Bug Keywords:**")
        bug_keywords_text = st.text_area(
            "Bug Keywords (comma-separated)",
            value=", ".join(CLASSIFICATION_CONFIG["bug_keywords"]),
            height=80,
            key="bug_keywords"
        )
        
        st.write("**Feature Keywords:**")
        feature_keywords_text = st.text_area(
            "Feature Keywords (comma-separated)",
            value=", ".join(CLASSIFICATION_CONFIG["feature_keywords"]),
            height=80,
            key="feature_keywords"
        )
        
        st.write("**Rating Thresholds:**")
        praise_threshold = st.slider(
            "Praise Rating Threshold",
            1, 5,
            CLASSIFICATION_CONFIG["praise_rating_threshold"],
            key="praise_threshold"
        )
        
        complaint_threshold = st.slider(
            "Complaint Rating Threshold",
            1, 5,
            CLASSIFICATION_CONFIG["complaint_rating_threshold"],
            key="complaint_threshold"
        )
        
        if st.button("💾 Save Configuration", type="primary"):
            st.success("✅ Configuration saved! (Demo mode - changes not persisted)")
    
    with st.expander("🎯 Priority Rules", expanded=False):
        st.write("**Critical Keywords:**")
        critical_keywords_text = st.text_area(
            "Critical Keywords (comma-separated)",
            value=", ".join(PRIORITY_CONFIG["critical_keywords"]),
            height=80,
            key="critical_keywords"
        )
        
        st.json({
            "Bug Priority": PRIORITY_CONFIG["bug_priority"],
            "Feature Priority": PRIORITY_CONFIG["feature_priority"],
            "Praise Priority": PRIORITY_CONFIG["praise_priority"]
        })
    
    st.markdown("---")
    st.header("🔄 Actions")
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()
    
    if st.button("📊 Reprocess All", use_container_width=True):
        st.info("Run `python main.py` to reprocess feedback")
    
    st.markdown("---")
    st.caption("💡 Tip: Use the tabs above to navigate between different views")

# Create tabs for different sections
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard", 
    "📈 Analytics", 
    "✏️ Manual Override",
    "📝 Processing Log",
    "🎯 Performance Metrics"
])
# Load data
try:
    tickets_path = DATA_PATHS["output_tickets"]
    
    if not os.path.exists(tickets_path):
        st.warning("⚠️ No tickets found. Run `python main.py` first to generate tickets.")
        st.info("The system will process feedback from app store reviews and support emails.")
        st.stop()
    
    tickets = pd.read_csv(tickets_path)
    
    # Load processing log if available
    processing_log = None
    if os.path.exists("outputs/processing_log.csv"):
        processing_log = pd.read_csv("outputs/processing_log.csv")
    
    # Load metrics if available
    metrics = None
    if os.path.exists("outputs/metrics.csv"):
        metrics = pd.read_csv("outputs/metrics.csv")
    
    # TAB 1: Dashboard Overview
    with tab1:
        st.header("📊 Dashboard Overview")
        
        # Key Metrics Row
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("📋 Total Tickets", len(tickets))
        
        with col2:
            critical_count = len(tickets[tickets["priority"] == "Critical"])
            st.metric("🔴 Critical", critical_count)
        
        with col3:
            bug_count = len(tickets[tickets["category"] == "Bug"])
            st.metric("🐛 Bugs", bug_count)
        
        with col4:
            open_count = len(tickets[tickets["status"] == "Open"])
            st.metric("📂 Open", open_count)
        
        with col5:
            if 'confidence' in tickets.columns:
                avg_confidence = tickets['confidence'].mean()
                st.metric("🎯 Avg Confidence", f"{avg_confidence:.2f}")
        
        st.markdown("---")
        
        # Filters
        st.subheader("🔍 Filter & Monitor")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            category_filter = st.multiselect(
                "Category",
                options=tickets["category"].unique(),
                default=tickets["category"].unique()
            )
        
        with col2:
            priority_filter = st.multiselect(
                "Priority",
                options=tickets["priority"].unique(),
                default=tickets["priority"].unique()
            )
        
        with col3:
            status_filter = st.multiselect(
                "Status",
                options=tickets["status"].unique(),
                default=tickets["status"].unique()
            )
        
        # Apply filters
        filtered_tickets = tickets[
            (tickets["category"].isin(category_filter)) &
            (tickets["priority"].isin(priority_filter)) &
            (tickets["status"].isin(status_filter))
        ]
        
        st.info(f"📊 Showing {len(filtered_tickets)} of {len(tickets)} tickets")
        
        # Display tickets
        st.dataframe(
            filtered_tickets,
            use_container_width=True,
            height=400
        )
    
    # TAB 2: Analytics
    with tab2:
        st.header("📈 Analytics & Visualizations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Category Distribution")
            category_counts = tickets["category"].value_counts()
            st.bar_chart(category_counts)
            
            st.subheader("📉 Source Type Distribution")
            if 'source_type' in tickets.columns:
                source_counts = tickets["source_type"].value_counts()
                st.bar_chart(source_counts)
        
        with col2:
            st.subheader("🎯 Priority Distribution")
            priority_counts = tickets["priority"].value_counts()
            st.bar_chart(priority_counts)
            
            st.subheader("💭 Sentiment Distribution")
            if 'sentiment' in tickets.columns:
                sentiment_counts = tickets["sentiment"].value_counts()
                st.bar_chart(sentiment_counts)
        
        st.markdown("---")
        
        # Confidence Analysis
        if 'confidence' in tickets.columns:
            st.subheader("🎯 Confidence Score Analysis")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Average Confidence", f"{tickets['confidence'].mean():.3f}")
            with col2:
                st.metric("⬇️ Minimum Confidence", f"{tickets['confidence'].min():.3f}")
            with col3:
                st.metric("⬆️ Maximum Confidence", f"{tickets['confidence'].max():.3f}")
            
            # Confidence distribution chart
            st.line_chart(tickets['confidence'].sort_values().reset_index(drop=True))
    
    # TAB 3: Manual Override
    with tab3:
        st.header("✏️ Manual Override System")
        
        st.write("Select a ticket to manually adjust its classification")
        
        ticket_ids = tickets["ticket_id"].tolist()
        selected_ticket = st.selectbox("🎫 Ticket ID", ticket_ids)
        
        if selected_ticket:
            current_ticket = tickets[tickets["ticket_id"] == selected_ticket].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📄 Current Values")
                st.info(f"**Category:** {current_ticket['category']}")
                st.info(f"**Priority:** {current_ticket['priority']}")
                st.info(f"**Status:** {current_ticket['status']}")
                if 'confidence' in current_ticket:
                    st.info(f"**Confidence:** {current_ticket['confidence']:.3f}")
                
                st.write("**Description:**")
                st.text_area("", current_ticket['description'], height=150, disabled=True, key="current_desc")
            
            with col2:
                st.subheader("✏️ Override Values")
                new_category = st.selectbox(
                    "New Category",
                    ["Bug", "Feature Request", "Praise", "Complaint", "Spam"],
                    index=["Bug", "Feature Request", "Praise", "Complaint", "Spam"].index(current_ticket['category']) if current_ticket['category'] in ["Bug", "Feature Request", "Praise", "Complaint", "Spam"] else 0
                )
                new_priority = st.selectbox(
                    "New Priority",
                    ["Critical", "High", "Medium", "Low"],
                    index=["Critical", "High", "Medium", "Low"].index(current_ticket['priority'])
                )
                new_status = st.selectbox(
                    "New Status",
                    ["Open", "In Progress", "Resolved", "Closed"],
                    index=0
                )
                
                override_reason = st.text_area("Reason for Override", height=100)
            
            if st.button("💾 Save Override", type="primary", use_container_width=True):
                # Update the ticket
                tickets.loc[tickets["ticket_id"] == selected_ticket, "category"] = new_category
                tickets.loc[tickets["ticket_id"] == selected_ticket, "priority"] = new_priority
                tickets.loc[tickets["ticket_id"] == selected_ticket, "status"] = new_status
                
                # Save back to CSV
                tickets.to_csv(tickets_path, index=False)
                logger.info(f"Manual override applied to ticket {selected_ticket}: {new_category}/{new_priority}/{new_status}")
                st.success(f"✅ Ticket {selected_ticket} updated successfully!")
                st.balloons()
                st.rerun()
    
    # TAB 4: Processing Log
    with tab4:
        st.header("📝 Processing Log")
        
        if processing_log is not None:
            st.write(f"📊 Total log entries: {len(processing_log)}")
            
            # Filter options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter_log = st.multiselect(
                    "Status",
                    options=processing_log["status"].unique(),
                    default=processing_log["status"].unique(),
                    key="log_status"
                )
            
            with col2:
                category_filter_log = st.multiselect(
                    "Category",
                    options=processing_log["category"].unique(),
                    default=processing_log["category"].unique(),
                    key="log_category"
                )
            
            with col3:
                source_filter_log = st.multiselect(
                    "Source Type",
                    options=processing_log["source_type"].unique(),
                    default=processing_log["source_type"].unique(),
                    key="log_source"
                )
            
            # Apply filters
            filtered_log = processing_log[
                (processing_log["status"].isin(status_filter_log)) &
                (processing_log["category"].isin(category_filter_log)) &
                (processing_log["source_type"].isin(source_filter_log))
            ]
            
            st.dataframe(
                filtered_log,
                use_container_width=True,
                height=500
            )
            
            # Download button
            csv = filtered_log.to_csv(index=False)
            st.download_button(
                label="📥 Download Processing Log",
                data=csv,
                file_name="filtered_processing_log.csv",
                mime="text/csv"
            )
        else:
            st.warning("⚠️ No processing log found. Run processing to generate logs.")
    
    # TAB 5: Performance Metrics
    with tab5:
        st.header("🎯 Performance Metrics")
        
        if metrics is not None and len(metrics) > 0:
            latest_metrics = metrics.iloc[-1]
            
            # Performance Overview
            st.subheader("⚡ Processing Performance")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🔢 Total Processed", int(latest_metrics['total_processed']))
                st.metric("✅ Successful", int(latest_metrics['successful_classifications']))
            
            with col2:
                st.metric("❌ Failed", int(latest_metrics['failed_classifications']))
                success_rate = (latest_metrics['successful_classifications'] / max(latest_metrics['total_processed'], 1)) * 100
                st.metric("📊 Success Rate", f"{success_rate:.1f}%")
            
            with col3:
                st.metric("⚡ Throughput", f"{latest_metrics['throughput_items_per_second']:.2f} items/sec")
                st.metric("⏱️ Avg Time", f"{latest_metrics['avg_processing_time_ms']:.0f}ms")
            
            with col4:
                st.metric("🎯 Avg Confidence", f"{latest_metrics['avg_confidence']:.3f}")
                st.metric("📈 Confidence Range", f"{latest_metrics['min_confidence']:.2f}-{latest_metrics['max_confidence']:.2f}")
            
            st.markdown("---")
            
            # Category and Priority Stats
            st.subheader("📊 Classification Statistics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**Category Breakdown:**")
                st.metric("🐛 Bugs", int(latest_metrics['bugs_detected']))
                st.metric("✨ Features", int(latest_metrics['features_detected']))
                st.metric("👍 Praise", int(latest_metrics['praise_detected']))
                st.metric("😟 Complaints", int(latest_metrics['complaints_detected']))
            
            with col2:
                st.write("**Priority Breakdown:**")
                st.metric("🔴 Critical", int(latest_metrics['critical_priority']))
                st.metric("🟠 High", int(latest_metrics['high_priority']))
                st.metric("🟡 Medium", int(latest_metrics['medium_priority']))
                st.metric("🟢 Low", int(latest_metrics['low_priority']))
            
            with col3:
                st.write("**Sentiment Analysis:**")
                st.metric("😊 Positive", int(latest_metrics['positive_sentiment']))
                st.metric("😞 Negative", int(latest_metrics['negative_sentiment']))
                st.metric("😐 Neutral", int(latest_metrics['neutral_sentiment']))
            
            st.markdown("---")
            
            # Historical metrics if available
            if len(metrics) > 1:
                st.subheader("📈 Historical Trends")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Confidence Over Time:**")
                    st.line_chart(metrics[['avg_confidence']])
                
                with col2:
                    st.write("**Throughput Over Time:**")
                    st.line_chart(metrics[['throughput_items_per_second']])
            
            # Download metrics
            st.markdown("---")
            csv = metrics.to_csv(index=False)
            st.download_button(
                label="📥 Download Metrics",
                data=csv,
                file_name="performance_metrics.csv",
                mime="text/csv"
            )
        else:
            st.warning("⚠️ No metrics found. Run processing to generate metrics.")
    
    # Footer with Recent Activity
    st.markdown("---")
    st.subheader("📜 Recent Activity Log")
    
    if os.path.exists("logs/app.log"):
        with open("logs/app.log", "r") as f:
            lines = f.readlines()
            recent_logs = lines[-15:] if len(lines) > 15 else lines
            st.text_area("Log Output", "".join(recent_logs), height=150)
    else:
        st.info("No logs available yet")

except Exception as e:
    st.error(f"❌ Error loading dashboard: {str(e)}")
    st.info("Check logs/app.log for details")
    logger.error(f"Dashboard error: {e}", exc_info=True)
