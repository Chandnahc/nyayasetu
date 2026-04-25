import os
import streamlit as st
import pandas as pd
from pathlib import Path
from extractor import process_judgment
from database import (
    init_db, save_judgment, save_extracted_items, save_action_plans,
    get_extracted_items, get_action_plans, verify_item, verify_action,
    get_all_judgments, get_verified_actions_all
)

# ─────────────────────────────────────────────
# APP CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="NyayaSetu",
    page_icon="⚖️",
    layout="wide"
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
init_db()

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2rem; font-weight: 600;
        color: #1a1a2e; margin-bottom: 0;
    }
    .subtitle {
        font-size: 1rem; color: #666;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.1rem; font-weight: 600;
        color: #1a1a2e; border-left: 4px solid #0F6E56;
        padding-left: 10px; margin: 1.5rem 0 1rem;
    }
    .confidence-high   { color: #0F6E56; font-weight: 600; }
    .confidence-medium { color: #BA7517; font-weight: 600; }
    .confidence-low    { color: #A32D2D; font-weight: 600; }
    .action-card {
        background: #f8f9fa; border-radius: 8px;
        padding: 1rem; margin: 0.5rem 0;
        border-left: 4px solid #0F6E56;
    }
    .priority-high   { border-left-color: #E24B4A !important; }
    .priority-medium { border-left-color: #BA7517 !important; }
    .priority-low    { border-left-color: #0F6E56 !important; }
    .stButton > button {
        border-radius: 6px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div style="text-align:center; padding: 8px 0;">
    <div style="font-size: 2.5rem;">⚖️</div>
    <div style="font-size: 0.65rem; font-weight: 600; color: #555; letter-spacing: 0.05em;">
        GOVERNMENT OF KARNATAKA
    </div>
</div>
""", unsafe_allow_html=True)
    st.markdown("## ⚖️ NyayaSetu")
    st.markdown("*Court Judgment AI Assistant*")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["📤 Upload Judgment", "🔍 Review & Verify", "📊 Dashboard"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("**Centre for e-Governance**")
    st.markdown("Government of Karnataka")
    st.caption("AI for Bharat · PAN IIT Summit 2026")


# ═════════════════════════════════════════════
# PAGE 1 — UPLOAD JUDGMENT
# ═════════════════════════════════════════════
if page == "📤 Upload Judgment":

    st.markdown('<p class="main-title">⚖️ NyayaSetu</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AI-Powered Court Judgment to Action Plan System · Government of Karnataka</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        all_j = get_all_judgments()
        st.metric("Total Judgments", len(all_j))
    with col2:
        verified = get_verified_actions_all()
        st.metric("Verified Actions", len(verified))
    with col3:
        pending = [j for j in all_j if j[3] == "pending"]
        st.metric("Pending Review", len(pending))
    
    # ── HOW IT WORKS BANNER ──
    st.markdown('<p class="section-header">How It Works</p>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info("📤 **1. Upload**\n\nUpload any Karnataka High Court judgment PDF — digital or scanned")
    with col2:
        st.info("🤖 **2. AI Analyses**\n\nGemini AI extracts case details, directives, deadlines and generates an action plan")
    with col3:
        st.info("✅ **3. Officer Verifies**\n\nEvery AI decision is reviewed and approved by a human officer before use")
    with col4:
        st.info("📊 **4. Dashboard**\n\nVerified actions shown department-wise with deadlines, priority and CSV export")
    st.markdown('<p class="section-header">Upload a Court Judgment PDF</p>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload court judgment (PDF)",
        type=["pdf"],
        help="Supports both digital and scanned PDFs from Karnataka High Court"
    )

    if uploaded_file:
        st.info(f"📄 File received: **{uploaded_file.name}** ({round(uploaded_file.size/1024, 1)} KB)")

        col_a, col_b = st.columns([1, 3])
        with col_a:
            process_btn = st.button("🤖 Analyse with AI", type="primary", use_container_width=True)

        if process_btn:
            # Save PDF to uploads folder
            pdf_path = UPLOAD_DIR / uploaded_file.name
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            progress_bar = st.progress(0, text="⏳ Starting analysis...")
            try:
                progress_bar.progress(10, text="📄 Step 1/4 — Reading PDF pages...")
                from extractor import extract_text_from_pdf
                raw_text = extract_text_from_pdf(str(pdf_path))

                progress_bar.progress(35, text="🔍 Step 2/4 — Extracting case details with Gemini AI...")
                from extractor import extract_case_details
                case_details = extract_case_details(raw_text)

                progress_bar.progress(65, text="📋 Step 3/4 — Generating action plan with Gemini AI...")
                import time
                time.sleep(3)
                from extractor import generate_action_plan
                action_plans = generate_action_plan(raw_text, case_details)

                progress_bar.progress(90, text="💾 Step 4/4 — Saving to database...")

                # Save to database
                judgment_id = save_judgment(uploaded_file.name)
                save_extracted_items(judgment_id, case_details)
                save_action_plans(judgment_id, action_plans)

                st.session_state["last_judgment_id"] = judgment_id
                st.session_state["last_filename"] = uploaded_file.name

                st.success("✅ Analysis complete! Switch to **Review & Verify** to check the results.")
                progress_bar.progress(100, text="✅ Analysis complete!")

                # Preview extracted details
                st.markdown('<p class="section-header">Extracted Case Details (Preview)</p>', unsafe_allow_html=True)
                preview_fields = ["case_number", "court_name", "order_date", "petitioner", "respondent"]
                for field in preview_fields:
                    if field in case_details:
                        data = case_details[field]
                        conf = data.get("confidence", "low")
                        conf_class = f"confidence-{conf}"
                        st.markdown(
                            f"**{field.replace('_', ' ').title()}:** {data.get('value', 'N/A')} "
                            f"<span class='{conf_class}'>({conf} confidence)</span>",
                            unsafe_allow_html=True
                        )

                st.markdown('<p class="section-header">Generated Action Plan (Preview)</p>', unsafe_allow_html=True)
                for i, action in enumerate(action_plans[:3]):
                    priority = action.get("priority", "Medium")
                    p_class = f"priority-{priority.lower()}"
                    st.markdown(f"""
                    <div class="action-card {p_class}">
                        <strong>{action.get('action_type', 'Action')}</strong> · 
                        <em>{action.get('department', 'N/A')}</em> · 
                        Priority: {priority}<br/>
                        {action.get('description', '')}
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                st.info("Make sure your GEMINI_API_KEY in the .env file is correct.")


# ═════════════════════════════════════════════
# PAGE 2 — REVIEW & VERIFY
# ═════════════════════════════════════════════
elif page == "🔍 Review & Verify":

    st.markdown('<p class="main-title">🔍 Review & Verify</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Human-in-the-loop verification · Only verified records move to the dashboard</p>', unsafe_allow_html=True)

    all_judgments = get_all_judgments()
    if not all_judgments:
        st.warning("No judgments uploaded yet. Go to **Upload Judgment** first.")
        st.stop()

    # Let officer pick which judgment to review
    judgment_options = {f"{j[1]} (uploaded {j[2]})": j[0] for j in all_judgments}
    selected_label = st.selectbox("Select a judgment to review:", list(judgment_options.keys()))
    judgment_id = judgment_options[selected_label]

    tab1, tab2 = st.tabs(["📋 Extracted Details", "📌 Action Plan"])

    # ── TAB 1: Extracted Details ──
    with tab1:
        st.markdown('<p class="section-header">AI-Extracted Case Information</p>', unsafe_allow_html=True)
        st.caption("Review each field. Edit the value if needed, then click Approve.")

        items = get_extracted_items(judgment_id)
        if not items:
            st.info("No extracted items found for this judgment.")
        else:
            for item in items:
                item_id, _, field_name, ai_value, verified_value, confidence, review_status = item

                with st.expander(
                    f"{'✅' if review_status == 'approved' else '⏳'} "
                    f"{field_name.replace('_', ' ').title()} — "
                    f"confidence: {confidence}",
                    expanded=(review_status != "approved")
                ):
                    conf_color = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(confidence, "⚪")
                    st.markdown(f"{conf_color} **AI extracted value:**")
                    st.info(ai_value or "Not found")

                    if review_status == "approved":
                        st.success(f"✅ Verified value: {verified_value}")
                    else:
                        edited = st.text_area(
                            "Edit if needed, then approve:",
                            value=ai_value or "",
                            key=f"edit_{item_id}",
                            height=80
                        )
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            if st.button("✅ Approve", key=f"approve_{item_id}", type="primary"):
                                verify_item(item_id, edited)
                                st.rerun()
                        with col2:
                            if st.button("❌ Mark as Not Found", key=f"reject_{item_id}"):
                                verify_item(item_id, "Not applicable")
                                st.rerun()

    # ── TAB 2: Action Plan ──
    with tab2:
        st.markdown('<p class="section-header">AI-Generated Action Plan</p>', unsafe_allow_html=True)
        st.caption("Verify each action item. Only approved items appear in the dashboard.")

        actions = get_action_plans(judgment_id)
        if not actions:
            st.info("No action plan found for this judgment.")
        else:
            for action in actions:
                action_id, _, action_type, description, deadline, department, priority, verified = action

                priority_colors = {"High": "#E24B4A", "Medium": "#BA7517", "Low": "#0F6E56"}
                border_color = priority_colors.get(priority, "#888")

                with st.expander(
                    f"{'✅' if verified else '⏳'} {action_type} — {department} — Priority: {priority}",
                    expanded=(not verified)
                ):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Action Type:** {action_type}")
                        st.markdown(f"**Department:** {department}")
                    with col2:
                        st.markdown(f"**Deadline:** {deadline}")
                        st.markdown(f"**Priority:** :{('red' if priority == 'High' else 'orange' if priority == 'Medium' else 'green')}[{priority}]")

                    st.markdown(f"**Description:** {description}")

                    if verified:
                        st.success("✅ This action has been verified and added to the dashboard.")
                    else:
                        if st.button("✅ Verify & Add to Dashboard", key=f"vaction_{action_id}", type="primary"):
                            verify_action(action_id)
                            st.rerun()


# ═════════════════════════════════════════════
# PAGE 3 — DASHBOARD
# ═════════════════════════════════════════════
elif page == "📊 Dashboard":

    st.markdown('<p class="main-title">📊 Action Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Verified action plans · Department-wise view · Government of Karnataka</p>', unsafe_allow_html=True)

    all_actions = get_verified_actions_all()

    if not all_actions:
        st.warning("No verified actions yet. Upload a judgment and verify the action plan first.")
        st.stop()

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    total = len(all_actions)
    high_p = sum(1 for a in all_actions if a[6] == "High")
    depts  = len(set(a[5] for a in all_actions))
    comply = sum(1 for a in all_actions if "Comply" in str(a[2]))

    with col1: st.metric("Total Actions", total)
    with col2: st.metric("High Priority", high_p, delta="Urgent" if high_p > 0 else None, delta_color="inverse")
    with col3: st.metric("Departments Involved", depts)
    with col4: st.metric("Compliance Required", comply)

    st.markdown("---")

    # Filters
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        dept_filter = st.selectbox(
            "Filter by department:",
            ["All"] + sorted(list(set(a[5] for a in all_actions)))
        )
    with col_f2:
        priority_filter = st.selectbox(
            "Filter by priority:",
            ["All", "High", "Medium", "Low"]
        )

    # Apply filters
    filtered = all_actions
    if dept_filter != "All":
        filtered = [a for a in filtered if a[5] == dept_filter]
    if priority_filter != "All":
        filtered = [a for a in filtered if a[6] == priority_filter]

    st.markdown(f'<p class="section-header">Verified Action Items ({len(filtered)})</p>', unsafe_allow_html=True)

    # Action cards
    for action in filtered:
        action_id, judgment_id, action_type, description, deadline, department, priority, verified, filename = action

        priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(priority, "⚪")
        action_emoji   = {"Comply": "✅", "Consider Appeal": "⚠️", "Monitor": "👁️", "File Response": "📝"}.get(action_type, "📌")

        with st.container():
            st.markdown(f"""
            <div class="action-card priority-{priority.lower()}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:1rem; font-weight:600;">{action_emoji} {action_type}</span>
                    <span>{priority_emoji} {priority} Priority</span>
                </div>
                <div style="margin-top:6px; color:#444;">{description}</div>
                <div style="margin-top:8px; font-size:0.85rem; color:#666;">
                    🏛️ <strong>{department}</strong> &nbsp;|&nbsp;
                    📅 Deadline: <strong>{deadline}</strong> &nbsp;|&nbsp;
                    📄 Source: {filename}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Export to CSV
    st.markdown('<p class="section-header">Export Verified Actions</p>', unsafe_allow_html=True)
    df = pd.DataFrame(filtered, columns=[
        "id", "judgment_id", "Action Type", "Description",
        "Deadline", "Department", "Priority", "Verified", "Source File"
    ])
    df_export = df[["Action Type", "Description", "Deadline", "Department", "Priority", "Source File"]]

    csv = df_export.to_csv(index=False)
    st.download_button(
        label="⬇️ Download as CSV",
        data=csv,
        file_name="nyayasetu_action_plan.csv",
        mime="text/csv"
    )

    # Table view
    with st.expander("📋 View as Table"):
        st.dataframe(df_export, use_container_width=True)
