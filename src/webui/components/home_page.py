"""
Home Page Component - Dashboard view after login
"""
import gradio as gr


def create_home_page(user_data=None):
    """
    Create the home page dashboard with header, user info, and 3 main cards
    
    Args:
        user_data: Dictionary with user information (username, email, avatar, etc.)
    
    Returns:
        Gradio Column component
    """
    
    # Set default user data if not provided
    if user_data is None:
        user_data = {
            "username": "User",
            "email": "user@example.com",
            "avatar": "👤"
        }
    
    username = user_data.get("username", "User")
    email = user_data.get("email", "user@example.com")
    
    with gr.Column() as home_container:
        # ============ Header Section with User Info ============
        with gr.Row(elem_classes=["home-header-wrapper"]):
            with gr.Column(scale=1, elem_classes=["home-header-left"]):
                gr.Markdown(
                    f"""
                    # 🏠 Welcome, {username}!
                    """,
                    elem_classes=["home-title"]
                )
                gr.Markdown(
                    f"**{email}**",
                    elem_classes=["home-subtitle"]
                )
            
            with gr.Column(scale=0, elem_classes=["home-header-right"]):
                with gr.Row(elem_classes=["home-user-actions"]):
                    gr.Button("🏠 Home", size="sm", interactive=False, elem_classes=["btn-home-icon"])
                    gr.Button(f"👤 {username}", size="sm", interactive=False, elem_classes=["btn-user-avatar"])
        
        gr.Markdown("---", elem_classes=["home-divider"])
        
        # ============ Main Content - 3 Cards ============
        gr.Markdown(
            "### ✨ Quick Access",
            elem_classes=["home-section-title"]
        )
        
        with gr.Row(elem_classes=["home-cards-row"]):
            # ============ Card 1: Test Case Generator ============
            with gr.Column(elem_classes=["home-card", "card-1"]):
                gr.Markdown(
                    """
                    ## 📋 Test Case Generator
                    """,
                    elem_classes=["card-title"]
                )
                gr.Markdown(
                    """
                    Generate comprehensive test cases for your Jira issues using AI. 
                    Automatically create well-structured test scenarios with steps, 
                    expected results, and detailed descriptions.
                    """,
                    elem_classes=["card-description"]
                )
                gr.Button(
                    "🚀 Start Generator",
                    variant="primary",
                    size="lg",
                    elem_classes=["card-button"]
                )
                with gr.Row(elem_classes=["card-stats"]):
                    gr.Markdown("⏱️ **Time:** ~2-5 min", elem_classes=["card-stat-item"])
                    gr.Markdown("📊 **Output:** JSON", elem_classes=["card-stat-item"])
            
            # ============ Card 2: Test IA Agent ============
            with gr.Column(elem_classes=["home-card", "card-2"]):
                gr.Markdown(
                    """
                    ## 🤖 Test IA Agent
                    """,
                    elem_classes=["card-title"]
                )
                gr.Markdown(
                    """
                    Deploy intelligent AI agents to automate your testing workflows.
                    Control browsers, interact with web applications, and execute 
                    complex testing scenarios with natural language instructions.
                    """,
                    elem_classes=["card-description"]
                )
                gr.Button(
                    "🎯 Launch Agent",
                    variant="primary",
                    size="lg",
                    elem_classes=["card-button"]
                )
                with gr.Row(elem_classes=["card-stats"]):
                    gr.Markdown("⏱️ **Time:** Variable", elem_classes=["card-stat-item"])
                    gr.Markdown("🌐 **Type:** Automation", elem_classes=["card-stat-item"])
            
            # ============ Card 3: Code Generator ============
            with gr.Column(elem_classes=["home-card", "card-3"]):
                gr.Markdown(
                    """
                    ## 💻 Code Generator
                    """,
                    elem_classes=["card-title"]
                )
                gr.Markdown(
                    """
                    Generate production-ready test code and automation scripts.
                    Create test implementations in multiple programming languages 
                    with proper structure, error handling, and best practices.
                    """,
                    elem_classes=["card-description"]
                )
                gr.Button(
                    "⚙️ Generate Code",
                    variant="primary",
                    size="lg",
                    elem_classes=["card-button"]
                )
                with gr.Row(elem_classes=["card-stats"]):
                    gr.Markdown("⏱️ **Time:** ~1-3 min", elem_classes=["card-stat-item"])
                    gr.Markdown("💾 **Format:** Multiple", elem_classes=["card-stat-item"])
        
        # ============ Footer Section - Recent Activity or Info ============
        gr.Markdown("---", elem_classes=["home-divider"])
        
        with gr.Row(elem_classes=["home-footer"]):
            with gr.Column(scale=1):
                gr.Markdown(
                    """
                    ### 📚 Documentation
                    [Quick Start Guide](https://docs.example.com) • [API Reference](https://api.example.com) • [Support](https://support.example.com)
                    """,
                    elem_classes=["home-footer-text"]
                )
            
            with gr.Column(scale=1):
                gr.Markdown(
                    """
                    ### ⚙️ Settings
                    [Preferences](https://settings.example.com) • [API Keys](https://keys.example.com) • [Profile](https://profile.example.com)
                    """,
                    elem_classes=["home-footer-text"]
                )
    
    return home_container


def get_home_page_css():
    """
    Returns CSS styles for the home page
    """
    return """
    /* ============ Home Page Container ============ */
    .home-header-wrapper {
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        padding: 20px 0 !important;
        margin-bottom: 10px !important;
    }
    
    .home-header-left {
        flex: 1 !important;
    }
    
    .home-header-right {
        display: flex !important;
        gap: 10px !important;
        align-items: center !important;
    }
    
    .home-title {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 !important;
        letter-spacing: -0.02em !important;
    }
    
    .home-subtitle {
        color: #64748b !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        margin: 5px 0 0 0 !important;
    }
    
    .home-user-actions {
        display: flex !important;
        gap: 8px !important;
    }
    
    .btn-home-icon,
    .btn-user-avatar {
        background: linear-gradient(135deg, #f8fafc, #f1f5f9) !important;
        border: 1px solid #e2e8f0 !important;
        color: #475569 !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        padding: 10px 16px !important;
        font-size: 0.9rem !important;
        cursor: default !important;
    }
    
    /* ============ Home Divider ============ */
    .home-divider {
        margin: 20px 0 !important;
        border-color: #e2e8f0 !important;
    }
    
    /* ============ Section Title ============ */
    .home-section-title {
        color: #1e293b !important;
        font-weight: 700 !important;
        font-size: 1.3rem !important;
        margin-bottom: 20px !important;
        letter-spacing: -0.01em !important;
    }
    
    /* ============ Cards Row ============ */
    .home-cards-row {
        display: grid !important;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)) !important;
        gap: 24px !important;
        margin-bottom: 30px !important;
    }
    
    /* ============ Card Styles ============ */
    .home-card {
        background: linear-gradient(135deg, #ffffff, #f9fafb) !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 28px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 16px !important;
        position: relative !important;
        overflow: hidden !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04) !important;
    }
    
    .home-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
    }
    
    .home-card:hover {
        transform: translateY(-8px) scale(1.02) !important;
        box-shadow: 0 12px 28px rgba(59, 130, 246, 0.15), 0 4px 12px rgba(0, 0, 0, 0.08) !important;
        border-color: #cbd5e1 !important;
    }
    
    .card-1::before {
        background: linear-gradient(90deg, #3b82f6, #60a5fa) !important;
    }
    
    .card-2::before {
        background: linear-gradient(90deg, #8b5cf6, #a78bfa) !important;
    }
    
    .card-3::before {
        background: linear-gradient(90deg, #ec4899, #f472b6) !important;
    }
    
    /* ============ Card Title ============ */
    .card-title {
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        margin: 0 !important;
        letter-spacing: -0.015em !important;
    }
    
    /* ============ Card Description ============ */
    .card-description {
        color: #64748b !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
        font-weight: 400 !important;
        margin: 8px 0 !important;
        flex-grow: 1 !important;
    }
    
    /* ============ Card Button ============ */
    .card-button {
        width: 100% !important;
        background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 14px 20px !important;
        border-radius: 12px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
        font-size: 0.95rem !important;
        cursor: pointer !important;
    }
    
    .card-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4) !important;
        background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
    }
    
    .card-button:active {
        transform: translateY(0) !important;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2) !important;
    }
    
    /* ============ Card Stats ============ */
    .card-stats {
        display: flex !important;
        gap: 12px !important;
        margin-top: 12px !important;
        padding-top: 12px !important;
        border-top: 1px solid #e2e8f0 !important;
    }
    
    .card-stat-item {
        font-size: 0.85rem !important;
        color: #64748b !important;
        font-weight: 500 !important;
        margin: 0 !important;
        flex: 1 !important;
    }
    
    /* ============ Home Footer ============ */
    .home-footer {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 20px !important;
        margin-top: 20px !important;
    }
    
    .home-footer-text {
        color: #64748b !important;
        font-size: 0.9rem !important;
        text-align: center !important;
        margin: 0 !important;
    }
    
    .home-footer-text a {
        color: #3b82f6 !important;
        text-decoration: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .home-footer-text a:hover {
        color: #2563eb !important;
        text-decoration: underline !important;
    }
    
    /* ============ Responsive Design ============ */
    @media (max-width: 1024px) {
        .home-cards-row {
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)) !important;
            gap: 16px !important;
        }
        
        .home-card {
            padding: 20px !important;
        }
        
        .home-title {
            font-size: 1.8rem !important;
        }
    }
    
    @media (max-width: 768px) {
        .home-header-wrapper {
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 12px !important;
        }
        
        .home-header-right {
            width: 100% !important;
            justify-content: flex-start !important;
        }
        
        .home-cards-row {
            grid-template-columns: 1fr !important;
            gap: 12px !important;
        }
        
        .home-card {
            padding: 16px !important;
        }
        
        .home-title {
            font-size: 1.5rem !important;
        }
        
        .home-footer {
            grid-template-columns: 1fr !important;
            gap: 12px !important;
        }
    }
    """
