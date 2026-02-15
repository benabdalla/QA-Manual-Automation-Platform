"""
Authentication Interface - Gradio components for login/register
"""
import gradio as gr
from typing import Tuple, Any
from src.auth.auth_manager import AuthManager


def create_auth_ui(auth_manager: AuthManager, on_login_success: callable):
    """
    Create authentication UI with login and registration tabs
    
    Args:
        auth_manager: AuthManager instance
        on_login_success: Callback function when login is successful
    
    Returns:
        Gradio Blocks component
    """
    
    css = """
    .auth-container {
        max-width: 450px !important;
        margin: 50px auto !important;
        padding: 30px !important;
    }
    .auth-header {
        text-align: center;
        margin-bottom: 30px;
    }
    .auth-form {
        padding: 20px;
    }
    .error-message {
        color: #ff4444;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .success-message {
        color: #00cc66;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    """
    
    js_func = """
    function refresh() {
        const url = new URL(window.location);
        if (url.searchParams.get('__theme') !== 'dark') {
            url.searchParams.set('__theme', 'dark');
            window.location.href = url.href;
        }
    }
    """
    
    with gr.Blocks(title="Ines QA Platform - Login", css=css, js=js_func) as auth_demo:
        # State for storing token
        token_state = gr.State(value="")
        user_state = gr.State(value=None)
        
        with gr.Column(elem_classes=["auth-container"]):
            gr.Markdown(
                """
                # 🌐 Ines QA Platform
                ### Please login or create an account
                """,
                elem_classes=["auth-header"]
            )
            
            with gr.Tabs() as auth_tabs:
                # Login Tab
                with gr.TabItem("🔐 Login", id="login-tab"):
                    with gr.Column(elem_classes=["auth-form"]):
                        login_username = gr.Textbox(
                            label="Username or Email",
                            placeholder="Enter your username or email",
                            type="text"
                        )
                        login_password = gr.Textbox(
                            label="Password",
                            placeholder="Enter your password",
                            type="password"
                        )
                        login_message = gr.Markdown(visible=False)
                        login_button = gr.Button("Login", variant="primary", size="lg")
                        
                        gr.Markdown(
                            """
                            ---
                            Don't have an account? Click the **Register** tab above.
                            """
                        )
                
                # Register Tab
                with gr.TabItem("📝 Register", id="register-tab"):
                    with gr.Column(elem_classes=["auth-form"]):
                        reg_username = gr.Textbox(
                            label="Username",
                            placeholder="Choose a username (letters, numbers, underscores)",
                            type="text"
                        )
                        reg_email = gr.Textbox(
                            label="Email",
                            placeholder="Enter your email address",
                            type="email"
                        )
                        reg_password = gr.Textbox(
                            label="Password",
                            placeholder="Create a strong password (min 8 chars, uppercase, lowercase, number)",
                            type="password"
                        )
                        reg_confirm_password = gr.Textbox(
                            label="Confirm Password",
                            placeholder="Confirm your password",
                            type="password"
                        )
                        reg_message = gr.Markdown(visible=False)
                        register_button = gr.Button("Create Account", variant="primary", size="lg")
                        
                        gr.Markdown(
                            """
                            ---
                            Already have an account? Click the **Login** tab above.
                            """
                        )
        
        # Login handler
        def handle_login(username: str, password: str) -> Tuple[Any, ...]:
            result = auth_manager.login(username, password)
            
            if result["success"]:
                return (
                    gr.update(visible=True, value=f"✅ Welcome back, **{result['user']['username']}**! Redirecting..."),
                    result["token"]["access_token"],
                    result["user"]
                )
            else:
                return (
                    gr.update(visible=True, value=f"❌ {result['error']}"),
                    "",
                    None
                )
        
        # Register handler
        def handle_register(username: str, email: str, password: str, confirm_password: str) -> Tuple[Any, ...]:
            result = auth_manager.register(username, email, password, confirm_password)
            
            if result["success"]:
                return gr.update(visible=True, value=f"✅ {result['message']}")
            else:
                return gr.update(visible=True, value=f"❌ {result['error']}")
        
        # Trigger main app when login successful
        def check_login_success(token: str, user: dict):
            if token and user:
                # Call the success callback
                on_login_success(token, user)
                return True
            return False
        
        login_button.click(
            fn=handle_login,
            inputs=[login_username, login_password],
            outputs=[login_message, token_state, user_state]
        )
        
        register_button.click(
            fn=handle_register,
            inputs=[reg_username, reg_email, reg_password, reg_confirm_password],
            outputs=[reg_message]
        )
    
    return auth_demo, token_state, user_state


def create_protected_ui(main_ui_func: callable, auth_manager: AuthManager, theme_name: str = "Ocean"):
    """
    Create a protected UI that requires authentication
    
    Args:
        main_ui_func: Function that creates the main UI
        auth_manager: AuthManager instance
        theme_name: Theme name for the UI
    
    Returns:
        Gradio Blocks component with authentication
    """
    from src.webui.interface import theme_map
    
    css = """
    .gradio-container {
        width: 70vw !important; 
        max-width: 70% !important; 
        margin-left: auto !important;
        margin-right: auto !important;
        padding-top: 10px !important;
    }
    .auth-container {
        max-width: 450px !important;
        margin: 50px auto !important;
        padding: 30px !important;
    }
    .auth-header {
        text-align: center;
        margin-bottom: 30px;
    }
    .user-info {
        text-align: right;
        padding: 10px;
        margin-bottom: 10px;
    }
    """
    
    js_dark_mode = """
    function refresh() {
        const url = new URL(window.location);
        if (url.searchParams.get('__theme') !== 'dark') {
            url.searchParams.set('__theme', 'dark');
            window.location.href = url.href;
        }
    }
    """
    
    with gr.Blocks(title="Ines QA Platform", theme=theme_map.get(theme_name, theme_map["Ocean"]), css=css, js=js_dark_mode) as demo:
        # State variables
        token_state = gr.State(value="")
        user_state = gr.State(value=None)
        is_authenticated = gr.State(value=False)
        
        # Auth Section (visible when not authenticated)
        with gr.Column(visible=True, elem_classes=["auth-container"]) as auth_section:
            gr.Markdown(
                """
                # 🌐 Ines QA Platform
                ### Please login or create an account
                """,
                elem_classes=["auth-header"]
            )
            
            with gr.Tabs() as auth_tabs:
                # Login Tab
                with gr.TabItem("🔐 Login"):
                    login_username = gr.Textbox(
                        label="Username or Email",
                        placeholder="Enter your username or email"
                    )
                    login_password = gr.Textbox(
                        label="Password",
                        placeholder="Enter your password",
                        type="password"
                    )
                    login_message = gr.Markdown(visible=False)
                    login_button = gr.Button("Login", variant="primary", size="lg")
                
                # Register Tab
                with gr.TabItem("📝 Register"):
                    reg_username = gr.Textbox(
                        label="Username",
                        placeholder="Choose a username"
                    )
                    reg_email = gr.Textbox(
                        label="Email",
                        placeholder="Enter your email"
                    )
                    reg_password = gr.Textbox(
                        label="Password",
                        placeholder="Create a password (min 8 chars)",
                        type="password"
                    )
                    reg_confirm = gr.Textbox(
                        label="Confirm Password",
                        placeholder="Confirm your password",
                        type="password"
                    )
                    reg_message = gr.Markdown(visible=False)
                    register_button = gr.Button("Create Account", variant="primary", size="lg")
        
        # Main App Section (visible when authenticated)
        with gr.Column(visible=False) as main_section:
            # User info bar
            with gr.Row(elem_classes=["user-info"]):
                user_display = gr.Markdown("", elem_id="user-display")
                logout_button = gr.Button("🚪 Logout", size="sm", scale=0)
            
            # Include the main UI here
            main_ui_func()
        
        # Event handlers
        def handle_login(username: str, password: str):
            if not username or not password:
                return (
                    gr.update(visible=True, value="❌ Please enter username and password"),
                    "", None, False,
                    gr.update(visible=True), gr.update(visible=False), ""
                )
            
            result = auth_manager.login(username, password)
            
            if result["success"]:
                user = result["user"]
                token = result["token"]["access_token"]
                return (
                    gr.update(visible=False),
                    token, user, True,
                    gr.update(visible=False), gr.update(visible=True),
                    f"👤 Logged in as: **{user['username']}**"
                )
            else:
                return (
                    gr.update(visible=True, value=f"❌ {result['error']}"),
                    "", None, False,
                    gr.update(visible=True), gr.update(visible=False), ""
                )
        
        def handle_register(username: str, email: str, password: str, confirm: str):
            result = auth_manager.register(username, email, password, confirm)
            
            if result["success"]:
                return gr.update(visible=True, value=f"✅ {result['message']}")
            else:
                return gr.update(visible=True, value=f"❌ {result['error']}")
        
        def handle_logout(token: str):
            auth_manager.logout(token)
            return (
                "", None, False,
                gr.update(visible=True), gr.update(visible=False), ""
            )
        
        login_button.click(
            fn=handle_login,
            inputs=[login_username, login_password],
            outputs=[login_message, token_state, user_state, is_authenticated, auth_section, main_section, user_display]
        )
        
        register_button.click(
            fn=handle_register,
            inputs=[reg_username, reg_email, reg_password, reg_confirm],
            outputs=[reg_message]
        )
        
        logout_button.click(
            fn=handle_logout,
            inputs=[token_state],
            outputs=[token_state, user_state, is_authenticated, auth_section, main_section, user_display]
        )
    
    return demo
