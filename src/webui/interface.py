import gradio as gr

from src.webui.webui_manager import WebuiManager
from src.webui.components.agent_settings_tab import create_agent_settings_tab
from src.webui.components.browser_settings_tab import create_browser_settings_tab
from src.webui.components.browser_use_agent_tab import create_browser_use_agent_tab
from src.webui.components.home_page import create_home_page, get_home_page_css

theme_map = {
    "Soft": gr.themes.Soft(),
}


def create_main_content(ui_manager: WebuiManager, auth_manager=None, user_data=None):
    """Create the main application content (tabs and components)"""
    agent_settings_result = None
    with gr.Tabs() as tabs:
        with gr.TabItem("⚙️ Agent Settings"):
            # Pass auth_manager to enable database save/load when authenticated
            agent_settings_result = create_agent_settings_tab(ui_manager, auth_manager)

        with gr.TabItem("🌐 Browser Settings"):
            create_browser_settings_tab(ui_manager)

        with gr.TabItem("🤖 Run Agent"):
            create_browser_use_agent_tab(ui_manager)
    
    return None, None


def create_ui(theme_name="Soft"):
    css = """
    /* ============ Global Styles - Light & Minimal ============ */
    .gradio-container {
        width: 80vw !important; 
        max-width: 1400px !important; 
        margin-left: auto !important;
        margin-right: auto !important;
        padding: 30px 20px !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
        color: #1e293b !important;
    }
    
    /* ============ Global Text Styles ============ */
    * {
        --text-primary: #1e293b;
        --text-secondary: #475569;
        --text-tertiary: #64748b;
        --accent-blue: #3b82f6;
        --accent-purple: #8b5cf6;
    }
    
    body, p, span, div {
        color: #1e293b !important;
    }
    
    /* ============ Header Styles - Clean & Modern ============ */
    .header-text {
        text-align: center;
        margin-bottom: 30px;
        padding: 35px 25px;
        background: linear-gradient(135deg, #ffffff, #f8fafc);
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
    }
    .header-text h1 {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 10px !important;
        letter-spacing: -0.02em !important;
    }
    .header-text h3 {
        color: #64748b !important;
        font-weight: 400 !important;
        font-size: 1.1rem !important;
    }
    
    .tab-header-text {
        text-align: center;
        padding: 20px;
        border-radius: 14px;
        background: linear-gradient(135deg, #f8fafc, #ffffff);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }
    
    /* ============ Tab Styles - Soft Pills ============ */
    .tabs {
        border-radius: 16px !important;
        background: white !important;
        box-shadow: 0 2px 15px rgba(0, 0, 0, 0.04) !important;
    }
    .tab-nav {
        background: #f8fafc !important;
        border-radius: 16px 16px 0 0 !important;
        padding: 12px !important;
        gap: 8px !important;
        border-bottom: 1px solid #e2e8f0 !important;
    }
    .tab-nav button {
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 500 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: none !important;
        background: transparent !important;
        color: #64748b !important;
        font-size: 0.95rem !important;
    }
    .tab-nav button:hover {
        background: rgba(59, 130, 246, 0.08) !important;
        color: #3b82f6 !important;
        transform: translateY(-1px) !important;
    }
    .tab-nav button.selected {
        background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
    }
    
    /* ============ Button Styles - Modern & Clean ============ */
    button {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        letter-spacing: 0.3px !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
        pointer-events: none;
    }
    
    button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .primary {
        background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 14px 32px !important;
        border-radius: 12px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3), 0 0 20px rgba(59, 130, 246, 0.1) !important;
        font-size: 0.95rem !important;
        cursor: pointer !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1) !important;
        letter-spacing: 0.5px !important;
    }
    
    .primary:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.5), 0 0 30px rgba(59, 130, 246, 0.2) !important;
        background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
    }
    
    .primary:active {
        transform: translateY(-1px) scale(0.98) !important;
    }
    
    .secondary {
        background: #ffffff !important;
        border: 2px solid #cbd5e1 !important;
        color: #3b82f6 !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        padding: 12px 32px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
        font-size: 0.95rem !important;
        cursor: pointer !important;
        letter-spacing: 0.5px !important;
    }
    
    .secondary:hover {
        background: linear-gradient(135deg, #f0f9ff, #f8fafc) !important;
        border-color: #3b82f6 !important;
        color: #2563eb !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.15) !important;
    }
    
    .secondary:active {
        transform: translateY(0) !important;
    }
    
    .stop {
        background: linear-gradient(135deg, #ef4444, #dc2626) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        padding: 14px 32px !important;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3), 0 0 20px rgba(239, 68, 68, 0.1) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-size: 0.95rem !important;
        cursor: pointer !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1) !important;
        letter-spacing: 0.5px !important;
    }
    
    .stop:hover {
        background: linear-gradient(135deg, #dc2626, #b91c1c) !important;
        box-shadow: 0 8px 25px rgba(239, 68, 68, 0.5), 0 0 30px rgba(239, 68, 68, 0.2) !important;
        transform: translateY(-3px) scale(1.02) !important;
    }
    
    .stop:active {
        transform: translateY(-1px) scale(0.98) !important;
    }
    
    /* ============ Input Styles - Clean Fields ============ */
    input, textarea, select {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        color: #1e293b !important;
        transition: all 0.3s ease !important;
        padding: 10px 14px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
    }
    input:focus, textarea:focus, select:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        outline: none !important;
        background: #ffffff !important;
    }
    input::placeholder, textarea::placeholder {
        color: #94a3b8 !important;
    }
    
    /* ============ Group/Card Styles - Elevated Cards ============ */
    .group {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.3s ease !important;
    }
    .group:hover {
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06) !important;
    }
    
    /* ============ Checkbox & Slider Styles ============ */
    input[type="checkbox"] {
        accent-color: #3b82f6 !important;
        width: 18px !important;
        height: 18px !important;
    }
    input[type="range"] {
        accent-color: #3b82f6 !important;
    }
    
    /* ============ Dropdown Styles ============ */
    .dropdown {
        border-radius: 12px !important;
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    /* ============ Dataframe/Table Styles - Clean Tables ============ */
    .dataframe {
        border-radius: 14px !important;
        overflow: hidden !important;
        border: 1px solid #e2e8f0 !important;
    }
    .dataframe th {
        background: linear-gradient(135deg, #f8fafc, #f1f5f9) !important;
        color: #1e293b !important;
        font-weight: 600 !important;
        padding: 16px !important;
        border-bottom: 2px solid #e2e8f0 !important;
    }
    .dataframe td {
        background: #ffffff !important;
        padding: 14px !important;
        border-bottom: 1px solid #f1f5f9 !important;
        color: #475569 !important;
    }
    .dataframe tr:hover td {
        background: #f8fafc !important;
    }
    
    /* ============ Scrollbar Styles - Minimal ============ */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 6px;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #3b82f6, #6366f1);
        border-radius: 6px;
        border: 2px solid #f1f5f9;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #2563eb, #4f46e5);
    }
    
    /* ============ Label Styles ============ */
    label {
        color: #1e293b !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        margin-bottom: 10px !important;
        display: block !important;
        letter-spacing: 0.3px !important;
        text-transform: capitalize !important;
    }
    
    /* ============ Heading Styles ============ */
    h1, h2, h3, h4, h5, h6 {
        color: #1e293b !important;
        font-weight: 800 !important;
        letter-spacing: -0.015em !important;
    }
    
    h2 {
        font-size: 1.875rem !important;
        margin-bottom: 16px !important;
    }
    
    h3 {
        font-size: 1.5rem !important;
        margin-bottom: 12px !important;
    }
    
    h4 {
        font-size: 1.125rem !important;
        margin-bottom: 10px !important;
        color: #334155 !important;
    }
    
    /* ============ Paragraph & Text Styles ============ */
    p {
        color: #475569 !important;
        line-height: 1.6 !important;
        font-size: 0.95rem !important;
        font-weight: 400 !important;
    }
    
    .text-muted {
        color: #64748b !important;
        font-size: 0.9rem !important;
    }
    
    .text-accent {
        color: #3b82f6 !important;
        font-weight: 700 !important;
    }
    
    /* ============ Accordion Styles ============ */
    .accordion {
        border-radius: 14px !important;
        border: 1px solid #e2e8f0 !important;
        overflow: hidden !important;
        background: #ffffff !important;
    }
    
    /* ============ Theme Section ============ */
    .theme-section {
        margin-bottom: 16px;
        padding: 24px;
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(99, 102, 241, 0.05));
        border: 1px solid rgba(59, 130, 246, 0.15);
    }
    
    /* ============ Success/Error Messages ============ */
    .success-message {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.08), rgba(22, 163, 74, 0.08)) !important;
        border: 1px solid rgba(34, 197, 94, 0.3) !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        color: #16a34a !important;
        font-weight: 500 !important;
    }
    .error-message {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.08), rgba(220, 38, 38, 0.08)) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        color: #dc2626 !important;
        font-weight: 500 !important;
    }
    
    /* ============ Chatbot Styles - Modern Chat ============ */
    .chatbot {
        border-radius: 16px !important;
        border: 1px solid #e2e8f0 !important;
        background: #ffffff !important;
    }
    .chatbot .message {
        border-radius: 14px !important;
        padding: 14px 18px !important;
        margin: 8px 0 !important;
    }
    .chatbot .user {
        background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
        color: white !important;
    }
    .chatbot .bot {
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        color: #1e293b !important;
    }
    
    /* ============ Animation - Smooth & Fluid ============ */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .fade-in {
        animation: fadeIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* ============ Tooltip Styles ============ */
    .tooltip {
        background: rgba(15, 23, 42, 0.95) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* ============ Checkbox & Radio Styles - Modern ============ */
    input[type="checkbox"],
    input[type="radio"] {
        cursor: pointer !important;
        width: 20px !important;
        height: 20px !important;
        accent-color: #3b82f6 !important;
        transition: all 0.3s ease !important;
    }
    
    input[type="checkbox"]:hover,
    input[type="radio"]:hover {
        transform: scale(1.1) !important;
        filter: brightness(1.1) !important;
    }
    
    input[type="checkbox"]:checked,
    input[type="radio"]:checked {
        box-shadow: 0 0 0 2px #ffffff, 0 0 0 4px #3b82f6 !important;
    }
    
    input[type="checkbox"]:focus,
    input[type="radio"]:focus {
        outline: 2px solid #3b82f6 !important;
        outline-offset: 2px !important;
    }
    
    /* ============ Checkbox Label Styles ============ */
    label input[type="checkbox"] + span,
    label input[type="radio"] + span {
        margin-left: 10px !important;
        font-weight: 500 !important;
        color: #1e293b !important;
        transition: color 0.3s ease !important;
    }
    
    label input[type="checkbox"]:hover + span,
    label input[type="radio"]:hover + span {
        color: #3b82f6 !important;
    }
    
    /* ============ Toggle Switch Styles ============ */
    .toggle-container {
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        padding: 8px 12px !important;
        background: #f8fafc !important;
        border-radius: 10px !important;
        border: 1px solid #e2e8f0 !important;
        transition: all 0.3s ease !important;
    }
    
    .toggle-container:hover {
        border-color: #3b82f6 !important;
        background: #f0f9ff !important;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* ============ Switch Toggle (HTML input range styled as toggle) ============ */
    input[type="range"] {
        cursor: pointer !important;
        accent-color: #3b82f6 !important;
        height: 6px !important;
        border-radius: 3px !important;
        transition: all 0.3s ease !important;
    }
    
    input[type="range"]:hover {
        filter: brightness(1.1) !important;
    }
    
    input[type="range"]:focus {
        outline: 2px solid #3b82f6 !important;
        outline-offset: 2px !important;
    }
    
    /* ============ Select/Dropdown Styles - Enhanced ============ */
    select {
        background: #ffffff !important;
        border: 2px solid #cbd5e1 !important;
        color: #1e293b !important;
        border-radius: 10px !important;
        padding: 12px 14px !important;
        font-size: 0.95rem !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        cursor: pointer !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
    }
    
    select:hover {
        border-color: #3b82f6 !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1) !important;
        background: linear-gradient(135deg, #ffffff, #f0f9ff) !important;
    }
    
    select:focus {
        outline: none !important;
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1), 0 0 0 5px rgba(59, 130, 246, 0.05) !important;
    }
    
    select:disabled {
        background-color: #f1f5f9 !important;
        border-color: #e2e8f0 !important;
        color: #94a3b8 !important;
        cursor: not-allowed !important;
    }
    
    /* ============ Dropdown Options ============ */
    select option {
        background: #ffffff !important;
        color: #1e293b !important;
        padding: 10px 8px !important;
    }
    
    select option:hover {
        background: #f0f9ff !important;
        color: #2563eb !important;
    }
    
    select option:checked {
        background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
        color: #ffffff !important;
    }
    
    /* ============ Enhanced Button States ============ */
    button:disabled {
        background: #e2e8f0 !important;
        color: #94a3b8 !important;
        cursor: not-allowed !important;
        opacity: 0.6 !important;
        transform: none !important;
    }
    
    button:disabled:hover {
        transform: none !important;
        box-shadow: none !important;
    }
    
    /* ============ Button Loading State ============ */
    .btn-loading {
        position: relative !important;
        color: transparent !important;
    }
    
    .btn-loading::after {
        content: '';
        position: absolute;
        width: 16px;
        height: 16px;
        top: 50%;
        left: 50%;
        margin-left: -8px;
        margin-top: -8px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top-color: white;
        animation: spin 0.6s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* ============ Animated Gradient Buttons ============ */
    .btn-gradient-animated {
        background: linear-gradient(90deg, #3b82f6, #6366f1, #3b82f6) !important;
        background-size: 200% 100% !important;
        animation: gradientShift 3s ease infinite !important;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% center; }
        50% { background-position: 100% center; }
        100% { background-position: 0% center; }
    }
    
    /* ============ Icon Button Styles ============ */
    .btn-icon {
        width: 44px !important;
        height: 44px !important;
        padding: 0 !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.2rem !important;
        transition: all 0.3s ease !important;
    }
    
    .btn-icon:hover {
        transform: scale(1.1) rotate(5deg) !important;
    }
    
    /* ============ Group/Card Button Container ============ */
    .btn-group {
        display: flex !important;
        gap: 12px !important;
        flex-wrap: wrap !important;
        padding: 16px !important;
        background: #ffffff !important;
        border-radius: 14px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
    }
    
    .btn-group button {
        flex: 1 !important;
        min-width: 120px !important;
    }
    
    /* ============ Dark Mode Toggle Button ============ */
    .theme-toggle {
        position: fixed !important;
        top: 20px !important;
        right: 20px !important;
        width: 50px !important;
        height: 50px !important;
        border-radius: 50% !important;
        background: #ffffff !important;
        border: 2px solid #e2e8f0 !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.5rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        z-index: 1000 !important;
    }
    
    .theme-toggle:hover {
        transform: scale(1.1) rotate(20deg) !important;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.2) !important;
        border-color: #3b82f6 !important;
    }
    
    .theme-toggle:active {
        transform: scale(0.95) !important;
    }
    
    /* ============ Dark Mode Styles ============ */
    .dark-mode {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%) !important;
        color: #f1f5f9 !important;
    }
    
    .dark-mode .gradio-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%) !important;
    }
    
    .dark-mode button {
        background: linear-gradient(135deg, #1e40af, #6d28d9) !important;
        color: #f1f5f9 !important;
    }
    
    .dark-mode input,
    .dark-mode select,
    .dark-mode textarea {
        background: #1e293b !important;
        color: #f1f5f9 !important;
        border-color: #334155 !important;
    }
    
    .dark-mode .group,
    .dark-mode .contain {
        background: #1e293b !important;
        border-color: #334155 !important;
    }
    
    .dark-mode .header-text {
        background: linear-gradient(135deg, #1e293b, #0f172a) !important;
        border-color: #334155 !important;
    }
    
    /* ============ Accessibility - Focus Visible ============ */
    *:focus-visible {
        outline: 2px solid #3b82f6 !important;
        outline-offset: 2px !important;
    }
    
    /* ============ High Contrast Mode Support ============ */
    @media (prefers-contrast: more) {
        button {
            border: 2px solid currentColor !important;
        }
        input {
            border-width: 2px !important;
        }
    }
    
    /* ============ Reduced Motion Support ============ */
    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    
    /* ============ Additional Refinements ============ */
    .pending {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    .contain {
        background: #ffffff !important;
        border-radius: 14px !important;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04) !important;
    }
    
    /* ============ Smooth Page Transitions ============ */
    .page-transition {
        animation: pageSlideIn 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    @keyframes pageSlideIn {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* ============ Responsive Button Sizes ============ */
    @media (max-width: 768px) {
        button {
            padding: 12px 24px !important;
            font-size: 0.9rem !important;
        }
        .btn-icon {
            width: 40px !important;
            height: 40px !important;
        }
        .theme-toggle {
            width: 44px !important;
            height: 44px !important;
            font-size: 1.2rem !important;
        }
    }
    """

    # Light mode with smooth animations and dark mode toggle
    js_func = """
    function refresh() {
        const url = new URL(window.location);

        if (url.searchParams.get('__theme') !== 'light') {
            url.searchParams.set('__theme', 'light');
            window.location.href = url.href;
        }
        
        // Initialize dark mode from localStorage
        const isDarkMode = localStorage.getItem('darkMode') === 'true';
        if (isDarkMode) {
            document.body.classList.add('dark-mode');
        }
        
        // Add smooth entrance animations
        document.addEventListener('DOMContentLoaded', function() {
            // Animate elements on page load
            const elements = document.querySelectorAll('.group, .tabs, .header-text');
            elements.forEach((el, index) => {
                el.style.opacity = '0';
                el.style.transform = 'translateY(30px)';
                setTimeout(() => {
                    el.style.transition = 'opacity 0.6s cubic-bezier(0.4, 0, 0.2, 1), transform 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
                    el.style.opacity = '1';
                    el.style.transform = 'translateY(0)';
                }, index * 80);
            });
            
            // Create and add dark mode toggle button if not exists
            if (!document.querySelector('.theme-toggle')) {
                const themeToggle = document.createElement('button');
                themeToggle.className = 'theme-toggle';
                themeToggle.innerHTML = isDarkMode ? '🌙' : '☀️';
                themeToggle.title = isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode';
                
                themeToggle.addEventListener('click', function() {
                    const isCurrentlyDark = document.body.classList.contains('dark-mode');
                    
                    if (isCurrentlyDark) {
                        document.body.classList.remove('dark-mode');
                        themeToggle.innerHTML = '☀️';
                        themeToggle.title = 'Switch to Dark Mode';
                        localStorage.setItem('darkMode', 'false');
                    } else {
                        document.body.classList.add('dark-mode');
                        themeToggle.innerHTML = '🌙';
                        themeToggle.title = 'Switch to Light Mode';
                        localStorage.setItem('darkMode', 'true');
                    }
                });
                
                document.body.appendChild(themeToggle);
            }
            
            // Add hover ripple effect to buttons
            document.querySelectorAll('button').forEach(button => {
                button.addEventListener('mouseenter', function() {
                    if (!this.classList.contains('theme-toggle')) {
                        this.style.filter = 'brightness(1.05)';
                    }
                });
                button.addEventListener('mouseleave', function() {
                    this.style.filter = 'brightness(1)';
                });
            });
            
            // Add smooth focus outlines to interactive elements
            document.querySelectorAll('input, select, textarea, button').forEach(element => {
                element.addEventListener('focus', function() {
                    this.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
                });
                element.addEventListener('blur', function() {
                    this.style.boxShadow = '';
                });
            });
            
            // Add page transition animation
            document.documentElement.style.opacity = '1';
        });
    }
    """

    ui_manager = WebuiManager()

    with gr.Blocks(
            title="Ines QA Platform", theme=theme_map[theme_name], css=css, js=js_func,
    ) as demo:
        with gr.Tabs() as tabs:
            with gr.TabItem("⚙️ Agent Settings"):
                create_agent_settings_tab(ui_manager)

            with gr.TabItem("🌐 Browser Settings"):
                create_browser_settings_tab(ui_manager)

            with gr.TabItem("🤖 Run Agent"):
                create_browser_use_agent_tab(ui_manager)

    return demo


def create_ui_with_auth(theme_name="Soft"):
    """Create the UI with authentication enabled"""
    from src.auth.auth_manager import AuthManager
    
    css = """
    /* ============ Global Styles - Light & Minimal ============ */
    .gradio-container {
        width: 80vw !important; 
        max-width: 1400px !important; 
        margin-left: auto !important;
        margin-right: auto !important;
        padding: 30px 20px !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
        color: #1e293b !important;
    }
    
    /* ============ Global Text Styles ============ */
    * {
        --text-primary: #1e293b;
        --text-secondary: #475569;
        --text-tertiary: #64748b;
        --accent-blue: #3b82f6;
        --accent-purple: #8b5cf6;
    }
    
    body, p, span, div {
        color: #1e293b !important;
    }
    
    /* ============ Header Styles - Clean & Modern ============ */
    .header-text {
        text-align: center;
        margin-bottom: 30px;
        padding: 35px 25px;
        background: linear-gradient(135deg, #ffffff, #f8fafc);
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
    }
    .header-text h1 {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 10px !important;
        letter-spacing: -0.02em !important;
    }
    .header-text h3 {
        color: #64748b !important;
        font-weight: 400 !important;
        font-size: 1.1rem !important;
    }
    
    .tab-header-text {
        text-align: center;
        padding: 20px;
        border-radius: 14px;
        background: linear-gradient(135deg, #f8fafc, #ffffff);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }
    
    /* ============ Tab Styles - Soft Pills ============ */
    .tabs {
        border-radius: 16px !important;
        background: white !important;
        box-shadow: 0 2px 15px rgba(0, 0, 0, 0.04) !important;
    }
    .tab-nav {
        background: #f8fafc !important;
        border-radius: 16px 16px 0 0 !important;
        padding: 12px !important;
        gap: 8px !important;
        border-bottom: 1px solid #e2e8f0 !important;
    }
    .tab-nav button {
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 500 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: none !important;
        background: transparent !important;
        color: #64748b !important;
        font-size: 0.95rem !important;
    }
    .tab-nav button:hover {
        background: rgba(59, 130, 246, 0.08) !important;
        color: #3b82f6 !important;
        transform: translateY(-1px) !important;
    }
    .tab-nav button.selected {
        background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
    }
    
    /* ============ Button Styles - Modern & Clean ============ */
    button {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        letter-spacing: 0.3px !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
        pointer-events: none;
    }
    
    button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .primary {
        background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 14px 32px !important;
        border-radius: 12px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3), 0 0 20px rgba(59, 130, 246, 0.1) !important;
        font-size: 0.95rem !important;
        cursor: pointer !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1) !important;
        letter-spacing: 0.5px !important;
    }
    
    .primary:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.5), 0 0 30px rgba(59, 130, 246, 0.2) !important;
        background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
    }
    
    .primary:active {
        transform: translateY(-1px) scale(0.98) !important;
    }
    
    .secondary {
        background: #ffffff !important;
        border: 2px solid #cbd5e1 !important;
        color: #3b82f6 !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        padding: 12px 32px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
        font-size: 0.95rem !important;
        cursor: pointer !important;
        letter-spacing: 0.5px !important;
    }
    
    .secondary:hover {
        background: linear-gradient(135deg, #f0f9ff, #f8fafc) !important;
        border-color: #3b82f6 !important;
        color: #2563eb !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.15) !important;
    }
    
    .secondary:active {
        transform: translateY(0) !important;
    }
    
    .stop {
        background: linear-gradient(135deg, #ef4444, #dc2626) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        padding: 14px 32px !important;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3), 0 0 20px rgba(239, 68, 68, 0.1) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-size: 0.95rem !important;
        cursor: pointer !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1) !important;
        letter-spacing: 0.5px !important;
    }
    
    .stop:hover {
        background: linear-gradient(135deg, #dc2626, #b91c1c) !important;
        box-shadow: 0 8px 25px rgba(239, 68, 68, 0.5), 0 0 30px rgba(239, 68, 68, 0.2) !important;
        transform: translateY(-3px) scale(1.02) !important;
    }
    
    .stop:active {
        transform: translateY(-1px) scale(0.98) !important;
    }
    
    /* ============ Input Styles - Clean Fields ============ */
    input, textarea, select {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        color: #1e293b !important;
        transition: all 0.3s ease !important;
        padding: 10px 14px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
    }
    input:focus, textarea:focus, select:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        outline: none !important;
        background: #ffffff !important;
    }
    input::placeholder, textarea::placeholder {
        color: #94a3b8 !important;
    }
    
    /* ============ Group/Card Styles - Elevated Cards ============ */
    .group {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.3s ease !important;
    }
    .group:hover {
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06) !important;
    }
    """
    
    ui_manager = WebuiManager()
    auth_manager = AuthManager()
    
    # Initialize database and authenticate with first available user
    if auth_manager.initialize():
        # Try to get first user from database for development
        try:
            import mysql.connector
            import os
            
            connection = mysql.connector.connect(
                host=os.getenv("MYSQL_HOST", "localhost"),
                port=int(os.getenv("MYSQL_PORT", "3306")),
                user=os.getenv("MYSQL_USER", "root"),
                password=os.getenv("MYSQL_PASSWORD", ""),
                database=os.getenv("MYSQL_DATABASE", "webui_db")
            )
            
            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT id, username, email FROM users LIMIT 1")
                result = cursor.fetchone()
                cursor.close()
                connection.close()
                
                if result:
                    auth_manager.set_current_user_directly(
                        user_id=result['id'],
                        username=result['username'],
                        email=result['email']
                    )
                    print(f"✅ Gradio interface authenticated as: {result['username']}")
        except Exception as e:
            print(f"⚠️  Could not auto-authenticate user: {e}")
    
    user_data = None

    with gr.Blocks(
            title="Ines QA Platform", theme=theme_map[theme_name], css=css,
    ) as demo:
        create_main_content(ui_manager, auth_manager, user_data)

    return demo

