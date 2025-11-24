"""
Streamlit UI for Autonomous QA Agent
"""
import streamlit as st
import streamlit.components.v1 as components
import os
import json
import base64
import requests

BACKEND_URL = "http://16.171.153.209:8000"

# Page configuration
st.set_page_config(
    page_title="QA Automation Studio",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for unique styling
st.markdown("""
<style>
    /* Main app background - Unique animated gradient with pattern */
    .stApp {
        background: 
            radial-gradient(circle at 25% 25%, rgba(255, 255, 255, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 75% 75%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
            linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #f5576c, #4facfe, #00f2fe);
        background-size: 100% 100%, 100% 100%, 400% 400%;
        animation: gradientShift 20s ease infinite;
        min-height: 100vh;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 0%, 0% 0%, 0% 50%; }
        50% { background-position: 0% 0%, 0% 0%, 100% 50%; }
        100% { background-position: 0% 0%, 0% 0%, 0% 50%; }
    }
    
    /* Bubble animation */
    .bubbles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        overflow: hidden;
        z-index: 0;
        pointer-events: none;
    }
    
    .bubble {
        position: absolute;
        bottom: -100px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        opacity: 0.5;
        animation: bubble-float linear infinite;
        pointer-events: none;
    }
    
    @keyframes bubble-float {
        0% {
            transform: translateY(0) translateX(0);
            opacity: 0;
        }
        10% {
            opacity: 0.5;
        }
        90% {
            opacity: 0.5;
        }
        100% {
            transform: translateY(-100vh) translateX(var(--bubble-x, 0));
            opacity: 0;
        }
    }
    
    .bubble:nth-child(1) {
        width: 80px;
        height: 80px;
        left: 10%;
        animation-duration: 8s;
        animation-delay: 0s;
        --bubble-x: 20px;
    }
    
    .bubble:nth-child(2) {
        width: 60px;
        height: 60px;
        left: 20%;
        animation-duration: 10s;
        animation-delay: 2s;
        --bubble-x: -30px;
    }
    
    .bubble:nth-child(3) {
        width: 100px;
        height: 100px;
        left: 35%;
        animation-duration: 12s;
        animation-delay: 1s;
        --bubble-x: 40px;
    }
    
    .bubble:nth-child(4) {
        width: 70px;
        height: 70px;
        left: 50%;
        animation-duration: 9s;
        animation-delay: 3s;
        --bubble-x: -20px;
    }
    
    .bubble:nth-child(5) {
        width: 90px;
        height: 90px;
        left: 65%;
        animation-duration: 11s;
        animation-delay: 0.5s;
        --bubble-x: 35px;
    }
    
    .bubble:nth-child(6) {
        width: 50px;
        height: 50px;
        left: 80%;
        animation-duration: 13s;
        animation-delay: 2.5s;
        --bubble-x: -25px;
    }
    
    .bubble:nth-child(7) {
        width: 75px;
        height: 75px;
        left: 15%;
        animation-duration: 10s;
        animation-delay: 4s;
        --bubble-x: 30px;
    }
    
    .bubble:nth-child(8) {
        width: 85px;
        height: 85px;
        left: 70%;
        animation-duration: 9s;
        animation-delay: 1.5s;
        --bubble-x: -40px;
    }
    
    .bubble:nth-child(9) {
        width: 65px;
        height: 65px;
        left: 45%;
        animation-duration: 11s;
        animation-delay: 3.5s;
        --bubble-x: 25px;
    }
    
    .bubble:nth-child(10) {
        width: 55px;
        height: 55px;
        left: 90%;
        animation-duration: 12s;
        animation-delay: 2s;
        --bubble-x: -15px;
    }
    
    /* Main content area with glassmorphism effect */
    .main .block-container {
        background: rgba(255, 255, 255, 0.92);
        backdrop-filter: blur(15px) saturate(180%);
        -webkit-backdrop-filter: blur(15px) saturate(180%);
        border-radius: 20px;
        padding: 2.5rem;
        margin-top: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Main theme colors - Modern gradient theme */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    /* Custom header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin: 0;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }
    
    .status-complete {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
    }
    
    .status-pending {
        background: #f0f0f0;
        color: #666;
    }
    
    /* Progress indicator */
    .progress-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 2rem 0;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
    }
    
    .progress-step {
        flex: 1;
        text-align: center;
        position: relative;
    }
    
    .progress-step::after {
        content: '';
        position: absolute;
        top: 20px;
        left: 60%;
        width: 80%;
        height: 3px;
        background: #e0e0e0;
        z-index: 0;
    }
    
    .progress-step:last-child::after {
        display: none;
    }
    
    .step-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: #e0e0e0;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 0.5rem;
        font-size: 1.2rem;
        position: relative;
        z-index: 1;
    }
    
    .step-active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .step-complete {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
    }
    
    /* Feature cards */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .feature-item {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: #333;
    }
    
    .feature-item h3 {
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .feature-item p {
        color: #555;
        margin: 0;
    }
    
    /* Custom button styling */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Download button styling */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    
    .stDownloadButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Selectbox styling */
    .stSelectbox>div>div>select {
        background: #667eea !important;
        color: #ffffff !important;
        border: 2px solid #667eea !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem !important;
    }
    
    .stSelectbox>div>div>select:hover {
        background: #764ba2 !important;
        border-color: #764ba2 !important;
    }
    
    .stSelectbox label {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    /* Test case cards */
    .test-case-card {
        background: #ffffff;
        border-radius: 8px;
        padding: 0.6rem 0.8rem;
        margin: 0.5rem 0;
        border-left: 3px solid #667eea;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .test-case-card h4 {
        color: #333333 !important;
        font-size: 0.95rem !important;
        margin: 0 !important;
        font-weight: 600 !important;
    }
    
    /* Ensure all text in test case section is visible */
    .element-container h3,
    .element-container h2,
    .element-container p {
        color: #000000 !important;
    }
    
    /* Exclude code blocks from text color rules - let Streamlit handle it */
    .stCodeBlock,
    .stCodeBlock pre,
    .stCodeBlock code,
    [data-testid="stCodeBlock"],
    [data-testid="stCodeBlock"] pre,
    [data-testid="stCodeBlock"] code {
        color: inherit !important;
        background: inherit !important;
    }
    
    /* Expander content styling */
    .streamlit-expanderContent {
        color: #000000 !important;
    }
    
    .streamlit-expanderContent p,
    .streamlit-expanderContent div,
    .streamlit-expanderContent strong {
        color: #000000 !important;
    }
    
    /* Markdown text in expanders */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] strong {
        color: #000000 !important;
    }
    
    /* Ensure all Streamlit text is visible */
    .stMarkdown p,
    .stMarkdown strong,
    .stMarkdown h1,
    .stMarkdown h2,
    .stMarkdown h3,
    .stMarkdown h4 {
        color: #000000 !important;
    }
    
    /* Subheader styling */
    h3[data-testid="stHeader"] {
        color: #000000 !important;
    }
    
    /* Main content text - be more specific */
    .main .block-container p,
    .main .block-container h1,
    .main .block-container h2,
    .main .block-container h3,
    .main .block-container h4,
    .main .block-container div[data-testid="stMarkdownContainer"] {
        color: #000000 !important;
    }
    
    /* HTML Preview styling */
    .html-preview-container {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #000000;
        margin-top: 3rem;
    }
    
    .footer h3 {
        color: #000000 !important;
    }
    
    .footer p {
        color: #000000 !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Streamlit widgets background */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>select {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
    
    /* File uploader styling */
    .stFileUploader {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 1rem;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        color: #667eea;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.8);
        border-radius: 10px;
    }
    
    /* Text area placeholder styling */
    .stTextArea textarea::placeholder {
        color: #666 !important;
        opacity: 1 !important;
        font-style: italic;
    }
    
    .stTextArea textarea::-webkit-input-placeholder {
        color: #666 !important;
        opacity: 1 !important;
        font-style: italic;
    }
    
    .stTextArea textarea::-moz-placeholder {
        color: #666 !important;
        opacity: 1 !important;
        font-style: italic;
    }
    
    .stTextArea textarea:-ms-input-placeholder {
        color: #666 !important;
        opacity: 1 !important;
        font-style: italic;
    }
    
    /* Style text area label */
    .stTextArea label {
        color: #000000 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    /* Text area content */
    .stTextArea textarea {
        color: #000000 !important;
        background: rgba(255, 255, 255, 0.95) !important;
    }
    
    /* Disabled text area - Preview HTML Content */
    .stTextArea textarea:disabled,
    textarea[disabled] {
        color: #000000 !important;
        background-color: #f0f0f0 !important;
        -webkit-text-fill-color: #000000 !important;
        opacity: 1 !important;
        border: 1px solid #d0d0d0 !important;
    }
    
    /* Specific styling for preview HTML content */
    textarea[data-baseweb="textarea"][disabled] {
        color: #000000 !important;
        background-color: #f0f0f0 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    
    /* All input labels */
    label {
        color: #000000 !important;
    }
    
    /* Radio button labels */
    .stRadio label {
        color: #000000 !important;
    }
    
    /* File uploader labels */
    .stFileUploader label {
        color: #000000 !important;
    }
    
    /* File uploader uploaded file names */
    .stFileUploader .uploadedFile {
        color: #000000 !important;
    }
    
    .stFileUploader .uploadedFile p {
        color: #000000 !important;
    }
    
    .stFileUploader .uploadedFile span {
        color: #000000 !important;
    }
    
    /* File uploader text */
    [data-testid="stFileUploader"] p,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] div {
        color: #000000 !important;
    }
    
    /* Uploaded file info */
    .uploadedFileInfo,
    .uploadedFileName {
        color: #000000 !important;
    }
    
    /* File uploader drop zone text - make white for dark background */
    [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploaderDropzone"] p,
    [data-testid="stFileUploaderDropzone"] span,
    [data-testid="stFileUploaderDropzone"] div,
    [data-testid="stFileUploaderDropzone"] * {
        color: #ffffff !important;
    }
    
    /* File uploader drop zone instructions and help text */
    .stFileUploader [data-baseweb="base-input"],
    .stFileUploader [class*="upload"],
    .stFileUploader [class*="dropzone"] {
        color: #ffffff !important;
    }
    
    /* Specific targeting for upload area text */
    .stFileUploader > div > div:first-child,
    .stFileUploader > div > div:first-child p,
    .stFileUploader > div > div:first-child span {
        color: #ffffff !important;
    }
    
    /* But keep uploaded file names black */
    .stFileUploader .uploadedFile {
        color: #000000 !important;
    }
    
    .stFileUploader .uploadedFile p {
        color: #000000 !important;
    }
    
    .stFileUploader .uploadedFile span {
        color: #000000 !important;
    }
    
    /* All Streamlit labels */
    [data-testid="stWidgetLabel"] {
        color: #000000 !important;
    }
    
    /* Subheader in Phase 2 */
    .element-container h3 {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# Add animated bubbles to background
st.markdown("""
<div class="bubbles">
    <div class="bubble"></div>
    <div class="bubble"></div>
    <div class="bubble"></div>
    <div class="bubble"></div>
    <div class="bubble"></div>
    <div class="bubble"></div>
    <div class="bubble"></div>
    <div class="bubble"></div>
    <div class="bubble"></div>
    <div class="bubble"></div>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'knowledge_base_built' not in st.session_state:
    st.session_state.knowledge_base_built = False
if 'generated_test_cases' not in st.session_state:
    st.session_state.generated_test_cases = []
if 'html_content' not in st.session_state:
    st.session_state.html_content = ""

# Custom Header
st.markdown("""
<div class="main-header">
    <h1>QA Automation Studio</h1>
    <p>AI-Powered Test Case Generation & Selenium Script Automation</p>
</div>
""", unsafe_allow_html=True)

# Progress Indicator
kb_status = "complete" if st.session_state.knowledge_base_built else "pending"
tc_status = "complete" if st.session_state.generated_test_cases else "pending"

st.markdown("""
<div class="progress-container">
    <div class="progress-step">
        <div class="step-icon {}">1</div>
        <div><strong>Phase 1</strong><br>Knowledge Base</div>
    </div>
    <div class="progress-step">
        <div class="step-icon {}">2</div>
        <div><strong>Phase 2</strong><br>Test Cases</div>
    </div>
    <div class="progress-step">
        <div class="step-icon {}">3</div>
        <div><strong>Phase 3</strong><br>Selenium Scripts</div>
    </div>
</div>
""".format(
    "step-complete" if st.session_state.knowledge_base_built else "step-active",
    "step-complete" if st.session_state.generated_test_cases else ("step-active" if st.session_state.knowledge_base_built else ""),
    "step-active" if st.session_state.generated_test_cases else ""
), unsafe_allow_html=True)

# Feature Highlights
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="feature-item">
        <h3>RAG-Powered</h3>
        <p>Intelligent document retrieval and context understanding</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="feature-item">
        <h3>AI-Generated</h3>
        <p>Automated test case creation with structured output</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="feature-item">
        <h3>Production-Ready</h3>
        <p>Runnable Selenium scripts with best practices</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# PHASE 1: Knowledge Ingestion
# ============================================================================
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; color: white; margin-bottom: 2rem;">
    <h2 style="color: white; margin-bottom: 0.5rem;">Phase 1: Knowledge Base Ingestion</h2>
    <p style="color: rgba(255, 255, 255, 0.9); margin: 0;">Build a comprehensive knowledge base from your documentation and HTML content</p>
</div>
""", unsafe_allow_html=True)

# Support Documents Upload
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("Support Documents")
    st.markdown("Upload support documents (MD, TXT, JSON, PDF, etc.)")
with col2:
    if st.session_state.knowledge_base_built:
        st.markdown('<span class="status-badge status-complete">✓ Knowledge Base Ready</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge status-pending">Pending</span>', unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Select support documents",
    type=['md', 'txt', 'json', 'pdf', 'docx', 'html'],
    accept_multiple_files=True,
    help="Upload multiple support documents that contain feature specifications and rules"
)

# HTML Content Input
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<style>
    .html-content-header {
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
    }
    .html-content-desc {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)
st.markdown('<h3 class="html-content-header">HTML Content</h3>', unsafe_allow_html=True)
st.markdown('<p class="html-content-desc">Paste or upload the HTML content (e.g., checkout.html)</p>', unsafe_allow_html=True)
html_input_method = st.radio(
    "Input method:",
    ["Paste HTML", "Upload HTML file"],
    horizontal=True
)

html_content = ""

if html_input_method == "Paste HTML":
    html_content = st.text_area(
        "HTML Content",
        height=300,
        placeholder="Paste your HTML content here...",
        help="Paste the HTML content of the page you want to test"
    )
else:
    uploaded_html = st.file_uploader(
        "Upload HTML file",
        type=['html', 'htm'],
        help="Upload the HTML file to be tested"
    )
    if uploaded_html is not None:
        html_content = uploaded_html.read().decode('utf-8')
        st.text_area(
            "Preview HTML Content",
            html_content,
            height=300,
            disabled=True,
            key="preview_html_content"
        )

# Build Knowledge Base Button
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Build Knowledge Base", type="primary", use_container_width=True):
            if not uploaded_files and not html_content:
                st.error("Please upload at least one support document or provide HTML content.")
            else:
                try:
                    with st.spinner("Building knowledge base... This may take a moment."):
                        documents_payload = []
                        for uploaded_file in uploaded_files:
                            file_bytes = uploaded_file.getvalue()
                            encoded_content = base64.b64encode(file_bytes).decode("utf-8")
                            documents_payload.append({
                                "filename": uploaded_file.name,
                                "content": encoded_content,
                                "encoding": "base64",
                                "mime_type": uploaded_file.type or "application/octet-stream"
                            })
                        
                        if not documents_payload and html_content:
                            st.warning("No support documents uploaded. Only HTML content will be stored.")
                        
                        payload = {
                            "documents": documents_payload,
                            "html_content": html_content
                        }
                        
                        try:
                            response = requests.post(
                                f"{BACKEND_URL}/ingest",
                                json=payload,
                                timeout=120,
                            )
                            if response.status_code != 200:
                                raise ValueError(response.text or "Backend ingestion failed.")
                            result = response.json()
                            
                            if result.get("status") == "success":
                                st.balloons()  # Celebration animation
                                st.session_state.knowledge_base_built = True
                                st.session_state.html_content = html_content
                                
                                st.success(f"{result.get('message', 'Knowledge Base Built Successfully.')}")
                                
                                stat_col1, stat_col2 = st.columns(2)
                                if documents_payload:
                                    with stat_col1:
                                        st.metric("Documents Processed", len(documents_payload))
                                if html_content:
                                    with stat_col2:
                                        st.metric("HTML Content Size", f"{len(html_content):,} chars")
                                
                                st.markdown("<br>", unsafe_allow_html=True)
                                st.markdown("""
                                <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 2rem; border-radius: 15px; color: white; text-align: center; margin: 2rem 0; box-shadow: 0 10px 30px rgba(240, 147, 251, 0.3);">
                                    <h2 style="color: white; margin-bottom: 1rem;">Knowledge Base Ready!</h2>
                                    <p style="color: rgba(255, 255, 255, 0.95); font-size: 1.1rem; margin-bottom: 0;">
                                        Your knowledge base has been successfully built. You can now proceed to Phase 2 below!
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                                st.rerun()
                            else:
                                st.error(result.get("message", "Failed to build knowledge base."))
                                st.session_state.knowledge_base_built = False
                        except requests.exceptions.RequestException as req_err:
                            st.error(f"Network error while contacting backend: {req_err}")
                            st.session_state.knowledge_base_built = False
                        except Exception as e:
                            st.error(f"Error building knowledge base: {str(e)}")
                            st.session_state.knowledge_base_built = False
                            st.exception(e)  # Show full traceback for debugging
                except Exception as e:
                    st.error(f"Unexpected error: {str(e)}")
                    st.exception(e)

# Guidance text after button
st.markdown("<br>", unsafe_allow_html=True)
if not st.session_state.knowledge_base_built:
    st.markdown("""
    <div style="background: rgba(102, 126, 234, 0.1);
                border-left: 4px solid #667eea;
                border-radius: 8px;
                padding: 1.25rem;
                margin: 1.5rem 0;
                box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);">
        <p style="color: #000000; margin: 0; font-weight: 700; font-size: 1.05rem;">
            What's Next?
        </p>
        <p style="color: #000000; margin: 0.75rem 0 0 0; font-weight: 500; line-height: 1.6;">
            After clicking "Build Knowledge Base" above, Phase 2 will appear below where you can generate test cases using AI-powered analysis of your documents and HTML content.
        </p>
        <p style="color: #666; margin: 0.5rem 0 0 0; font-size: 0.9rem; line-height: 1.5;">
            The system will use RAG (Retrieval-Augmented Generation) to create comprehensive, documentation-grounded test cases automatically.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# PHASE 2: Test Case Generation
# ============================================================================
if st.session_state.knowledge_base_built:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 10px; color: white; margin-bottom: 2rem;">
        <h2 style="color: white; margin-bottom: 0.5rem;">Phase 2: Test Case Generation</h2>
        <p style="color: rgba(255, 255, 255, 0.9); margin: 0;">Generate comprehensive test cases using RAG-powered AI analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.knowledge_base_built:
        st.warning("Please build the knowledge base first (Phase 1) before generating test cases.")
    else:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown('<h3 style="color: #000000; font-weight: 700;">Generate Test Cases</h3>', unsafe_allow_html=True)
            st.markdown('<p style="color: #000000;">Enter a prompt describing what test cases you want to generate, or use the default prompt.</p>', unsafe_allow_html=True)
        with col2:
            if st.session_state.generated_test_cases:
                st.metric("Test Cases", len(st.session_state.generated_test_cases))
        
        # Default prompt option
        use_default_prompt = st.checkbox("Use AI-optimized default prompt", value=True)
        
        if use_default_prompt:
            default_prompt = """Generate comprehensive test cases for the E-Shop Checkout system covering:
1. Discount code functionality (SAVE15 code)
2. Shipping options (Standard and Express)
3. Form validation for all user detail fields
4. Cart summary calculations
5. Order completion workflow"""
            user_prompt = st.text_area(
                "Test Case Generation Prompt",
                value=default_prompt,
                height=150,
                help="Describe what test cases you want to generate based on the knowledge base"
            )
        else:
            user_prompt = st.text_area(
                "Test Case Generation Prompt",
                height=150,
                placeholder="E.g., Generate test cases for discount code validation and form field validation...",
                help="Describe what test cases you want to generate based on the knowledge base"
            )
        
        # HTML Preview Section
        html_preview_content = st.session_state.html_content
        if html_preview_content:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<h3 style="color: #000000; font-weight: 700;">HTML Preview</h3>', unsafe_allow_html=True)
            st.markdown('<p style="color: #000000;">Preview the loaded HTML content to inspect the page structure before generating tests.</p>', unsafe_allow_html=True)
            
            # Display HTML in an iframe
            st.markdown('<div class="html-preview-container">', unsafe_allow_html=True)
            components.html(
                html_preview_content,
                height=400,
                scrolling=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
            st.caption("Use this preview to understand the page structure and element selectors.")
        
        # Generate Test Cases Button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Generate Test Cases", type="primary", use_container_width=True):
            if not user_prompt.strip():
                st.error("Please enter a prompt for test case generation.")
            else:
                try:
                    with st.spinner("Generating test cases using RAG pipeline... This may take a moment."):
                        response = requests.post(
                            f"{BACKEND_URL}/generate",
                            json={"prompt": user_prompt},
                            timeout=120,
                        )
                        if response.status_code != 200:
                            raise ValueError(response.text or "Backend test case generation failed.")
                        result = response.json()
                        
                        if result["status"] == "success":
                            st.balloons()  # Celebration animation
                            st.success(f"{result['message']}")
                            
                            # Display test cases
                            test_cases = result.get("test_cases", [])
                            if test_cases:
                                # Store test cases in session state for Phase 3
                                st.session_state.generated_test_cases = test_cases
                                
                                st.markdown(f'<h3 style="color: #000000; font-weight: 700;">Generated {len(test_cases)} Test Cases</h3>', unsafe_allow_html=True)
                                
                                # Display test cases in a more visual way
                                for idx, tc in enumerate(test_cases, 1):
                                    st.markdown(f"""
                                    <div class="test-case-card">
                                        <h4 style="color: #333333; margin: 0; font-weight: 600; font-size: 0.95rem;">
                                            {tc.get('Test_ID', f'TC-{idx:03d}')}: {tc.get('Feature', 'Unknown Feature')}
                                        </h4>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    with st.expander(f"View Details: {tc.get('Test_ID', f'TC-{idx:03d}')}", expanded=False):
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.markdown(f"<p style='color: #000000;'><strong style='color: #000000;'>Feature:</strong> {tc.get('Feature', 'N/A')}</p>", unsafe_allow_html=True)
                                            st.markdown(f"<p style='color: #000000;'><strong style='color: #000000;'>Test Scenario:</strong></p>", unsafe_allow_html=True)
                                            st.markdown(f"<p style='color: #000000;'>{tc.get('Test_Scenario', 'N/A')}</p>", unsafe_allow_html=True)
                                        with col2:
                                            st.markdown(f"<p style='color: #000000;'><strong style='color: #000000;'>Expected Result:</strong></p>", unsafe_allow_html=True)
                                            st.markdown(f"<p style='color: #000000;'>{tc.get('Expected_Result', 'N/A')}</p>", unsafe_allow_html=True)
                                            st.markdown(f"<p style='color: #000000;'><strong style='color: #000000;'>Grounded In:</strong> {tc.get('Grounded_In', 'N/A')}</p>", unsafe_allow_html=True)
                                
                                # Download button for test cases
                                test_cases_json = json.dumps(result["test_cases"], indent=2)
                                col1, col2, col3 = st.columns([1, 2, 1])
                                with col2:
                                    st.download_button(
                                        label="Download Test Cases as JSON",
                                        data=test_cases_json,
                                        file_name="test_cases.json",
                                        mime="application/json",
                                        use_container_width=True
                                    )
                                
                                # Success message banner
                                st.markdown("<br>", unsafe_allow_html=True)
                                st.markdown("""
                                <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 2rem; border-radius: 15px; color: white; text-align: center; margin: 2rem 0; box-shadow: 0 10px 30px rgba(79, 172, 254, 0.3);">
                                    <h2 style="color: white; margin-bottom: 1rem;">Test Cases Generated!</h2>
                                    <p style="color: rgba(255, 255, 255, 0.95); font-size: 1.1rem; margin-bottom: 0;">
                                        {count} test cases have been successfully generated. You can now proceed to Phase 3 below!
                                    </p>
                                </div>
                                """.format(count=len(test_cases)), unsafe_allow_html=True)
                                st.rerun()
                            else:
                                st.warning("No test cases were generated. Please check your prompt and knowledge base.")
                        else:
                            st.error(f"{result['message']}")
                            if "raw_response" in result:
                                with st.expander("View Raw Response"):
                                    st.text(result["raw_response"])
                except requests.exceptions.RequestException as req_err:
                    st.error(f"Network error while generating test cases: {req_err}")
                except Exception as e:
                    st.error(f"Error generating test cases: {str(e)}")
                    st.exception(e)  # Show full traceback for debugging

# Display Generated Test Cases Section (before Phase 3)
if st.session_state.generated_test_cases:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
                border: 2px solid rgba(102, 126, 234, 0.3);
                border-radius: 15px;
                padding: 2rem;
                margin: 2rem 0;
                box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);">
        <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
            <div style="width: 4px; height: 35px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 2px; margin-right: 1rem;"></div>
            <h2 style="color: #000000; margin: 0; font-size: 1.75rem; font-weight: 700;">Generated Test Cases</h2>
        </div>
        <p style="color: #666; margin-bottom: 1.5rem; font-size: 1rem;">Review the test cases below before proceeding to Phase 3</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display all generated test cases
    test_cases = st.session_state.generated_test_cases
    st.markdown(f'<h3 style="color: #000000; font-weight: 700; margin-bottom: 1rem;">Total: {len(test_cases)} Test Cases</h3>', unsafe_allow_html=True)
    
    for idx, tc in enumerate(test_cases, 1):
        st.markdown(f"""
        <div class="test-case-card">
            <h4 style="color: #333333; margin: 0; font-weight: 600; font-size: 0.95rem;">
                {tc.get('Test_ID', f'TC-{idx:03d}')}: {tc.get('Feature', 'Unknown Feature')}
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander(f"View Details: {tc.get('Test_ID', f'TC-{idx:03d}')}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"<p style='color: #000000;'><strong style='color: #000000;'>Feature:</strong> {tc.get('Feature', 'N/A')}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: #000000;'><strong style='color: #000000;'>Test Scenario:</strong></p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: #000000;'>{tc.get('Test_Scenario', 'N/A')}</p>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<p style='color: #000000;'><strong style='color: #000000;'>Expected Result:</strong></p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: #000000;'>{tc.get('Expected_Result', 'N/A')}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: #000000;'><strong style='color: #000000;'>Grounded In:</strong> {tc.get('Grounded_In', 'N/A')}</p>", unsafe_allow_html=True)
    
    # Download button for test cases
    test_cases_json = json.dumps(st.session_state.generated_test_cases, indent=2)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label="Download Test Cases as JSON",
            data=test_cases_json,
            file_name="test_cases.json",
            mime="application/json",
            use_container_width=True
        )
    
    st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# PHASE 3: Selenium Scripting
# ============================================================================
if st.session_state.generated_test_cases:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1.5rem; border-radius: 10px; color: white; margin-bottom: 2rem;">
        <h2 style="color: white; margin-bottom: 0.5rem;">Phase 3: Selenium Script Generation</h2>
        <p style="color: rgba(255, 255, 255, 0.9); margin: 0;">Generate production-ready Selenium automation scripts</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Generate Selenium Script")
    st.markdown("Select a test case to generate a runnable Python Selenium script.")
    
    # Get test cases from session state
    test_cases = st.session_state.generated_test_cases
    
    # Create a dropdown to select test case
    test_case_options = {
        f"{tc.get('Test_ID', f'TC-{idx:03d}')}: {tc.get('Feature', 'Unknown Feature')}": tc
        for idx, tc in enumerate(test_cases)
    }
    
    selected_test_case_label = st.selectbox(
        "Select Test Case:",
        options=list(test_case_options.keys()),
        help="Choose a test case to generate a Selenium script for"
    )
    
    selected_test_case = test_case_options[selected_test_case_label]
    
    # Display selected test case details in a card
    st.markdown(f"""
    <div class="test-case-card">
        <h4 style="color: #4facfe;">Selected: {selected_test_case.get('Test_ID', 'N/A')}</h4>
        <p><strong>Feature:</strong> {selected_test_case.get('Feature', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("View Full Test Case Details", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Test ID:** {selected_test_case.get('Test_ID', 'N/A')}")
            st.markdown(f"**Feature:** {selected_test_case.get('Feature', 'N/A')}")
            st.markdown(f"**Test Scenario:**")
            st.markdown(selected_test_case.get('Test_Scenario', 'N/A'))
        with col2:
            st.markdown(f"**Expected Result:**")
            st.markdown(selected_test_case.get('Expected_Result', 'N/A'))
            st.markdown(f"**Grounded In:** {selected_test_case.get('Grounded_In', 'N/A')}")
    
    # Generate script button
    if st.button("Generate Selenium Script", type="primary", use_container_width=True):
        try:
            with st.spinner("Generating Selenium script... This may take a moment."):
                response = requests.post(
                    f"{BACKEND_URL}/generate_script",
                    json={"test_case": selected_test_case},
                    timeout=120,
                )
                if response.status_code != 200:
                    raise ValueError(response.text or "Backend script generation failed.")
                result = response.json()
                
                if result["status"] == "success":
                    st.balloons()  # Celebration animation
                    st.success(f"{result['message']}")
                    
                    # Display the generated script
                    st.subheader("Generated Selenium Script")
                    script = result.get("script", "")
                    
                    if script:
                        # Display script in code block with better styling
                        st.code(script, language="python", line_numbers=True)
                        
                        # Download button for the script
                        script_filename = f"{selected_test_case.get('Test_ID', 'test_case').replace(' ', '_')}_selenium_script.py"
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            st.download_button(
                                label="Download Selenium Script",
                                data=script,
                                file_name=script_filename,
                                mime="text/x-python",
                                use_container_width=True
                            )
                        
                        # Instructions in a styled box
                        st.markdown("""
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; color: white; margin-top: 1rem;">
                            <h4 style="color: white; margin-bottom: 1rem;">Next Steps</h4>
                            <ol style="color: white; line-height: 2;">
                                <li>Download the script using the button above</li>
                                <li>Install dependencies: <code style="background: rgba(255,255,255,0.2); padding: 0.2rem 0.5rem; border-radius: 5px;">pip install selenium webdriver-manager</code></li>
                                <li>Update the HTML file path in the script (if needed)</li>
                                <li>Run the script: <code style="background: rgba(255,255,255,0.2); padding: 0.2rem 0.5rem; border-radius: 5px;">python script_name.py</code></li>
                            </ol>
                            <p style="color: rgba(255,255,255,0.9); margin-top: 1rem; margin-bottom: 0;">
                                <strong>Note:</strong> Make sure you have Chrome browser and ChromeDriver installed, or modify the script to use your preferred browser.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("Script was generated but appears to be empty.")
                else:
                    st.error(f"{result['message']}")
                    if "script" in result and result["script"]:
                        with st.expander("View Partial Script"):
                            st.code(result["script"], language="python")
        except requests.exceptions.RequestException as req_err:
            st.error(f"Network error while generating Selenium script: {req_err}")
        except Exception as e:
            st.error(f"Error generating Selenium script: {str(e)}")
            st.exception(e)  # Show full traceback for debugging

# Footer
st.markdown("""
<div class="footer">
    <hr style="border: none; border-top: 2px solid #e0e0e0; margin: 2rem 0;">
    <h3 style="color: #000000;">QA Automation Studio</h3>
    <p style="color: #000000;">Powered by AI • RAG-Powered Test Generation • Production-Ready Automation</p>
    <p style="font-size: 0.9rem; color: #000000;">Automating QA Testing with Intelligence</p>
</div>
""", unsafe_allow_html=True)
