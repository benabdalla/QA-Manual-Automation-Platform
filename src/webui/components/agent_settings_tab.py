import json
import os

import gradio as gr
from gradio.components import Component
from typing import Any, Dict, Optional
from src.webui.webui_manager import WebuiManager
from src.utils import config
import logging
from functools import partial

logger = logging.getLogger(__name__)


def update_model_dropdown(llm_provider):
    """
    Update the model name dropdown with predefined models for the selected provider.
    """
    if llm_provider in config.model_names:
        return gr.Dropdown(choices=config.model_names[llm_provider], value=config.model_names[llm_provider][0],
                           interactive=True)
    else:
        return gr.Dropdown(choices=[], value="", interactive=True, allow_custom_value=True)


async def update_mcp_server(mcp_file: str, webui_manager: WebuiManager):
    """
    Update the MCP server.
    """
    if hasattr(webui_manager, "bu_controller") and webui_manager.bu_controller:
        logger.warning("⚠️ Close controller because mcp file has changed!")
        await webui_manager.bu_controller.close_mcp_client()
        webui_manager.bu_controller = None

    if not mcp_file or not os.path.exists(mcp_file) or not mcp_file.endswith('.json'):
        logger.warning(f"{mcp_file} is not a valid MCP file.")
        return None, gr.update(visible=False)

    with open(mcp_file, 'r') as f:
        mcp_server = json.load(f)

    return json.dumps(mcp_server, indent=2), gr.update(visible=True)


def create_agent_settings_tab(webui_manager: WebuiManager, auth_manager=None):
    """
    Creates an agent settings tab with optional database save/load functionality.
    
    Args:
        webui_manager: The WebUI manager instance
        auth_manager: Optional AuthManager for database operations (when authenticated)
    """
    input_components = set(webui_manager.get_components())
    tab_components = {}

    # System Prompt Settings (completely hidden - used internally for database save/load)
    # These are hidden state components, not visible in UI
    override_system_prompt = gr.Textbox(value="", visible=False)
    extend_system_prompt = gr.Textbox(value="", visible=False)
    mcp_server_config = gr.Textbox(value="", visible=False)

    with gr.Group():
        with gr.Row():
            llm_provider = gr.Dropdown(
                choices=[provider for provider, model in config.model_names.items()],
                label="LLM Provider",
                value=os.getenv("DEFAULT_LLM", "openai"),
                info="Select LLM provider for LLM",
                interactive=True
            )
            llm_model_name = gr.Dropdown(
                label="LLM Model Name",
                choices=config.model_names[os.getenv("DEFAULT_LLM", "openai")],
                value=config.model_names[os.getenv("DEFAULT_LLM", "openai")][0],
                interactive=True,
                allow_custom_value=True,
                info="Select a model in the dropdown options or directly type a custom model name"
            )
        with gr.Row():
            llm_temperature = gr.Slider(
                minimum=0.0,
                maximum=2.0,
                value=0.6,
                step=0.1,
                label="LLM Temperature",
                info="Controls randomness in model outputs",
                interactive=True
            )
            use_vision = gr.Checkbox(
                label="Use Vision",
                value=True,
                info="Enable Vision(Input highlighted screenshot into LLM)",
                interactive=True
            )
            ollama_num_ctx = gr.Slider(
                minimum=2 ** 8,
                maximum=2 ** 16,
                value=16000,
                step=1,
                label="Ollama Context Length",
                info="Controls max context length model needs to handle (less = faster)",
                visible=False,
                interactive=True
            )
        with gr.Row():
            llm_base_url = gr.Textbox(
                label="Base URL",
                value="",
                info="API endpoint URL (if required)"
            )
            llm_api_key = gr.Textbox(
                label="API Key",
                type="password",
                value="",
                info="Your API key (leave blank to use .env)"
            )



    with gr.Row():
        max_steps = gr.Slider(
            minimum=1,
            maximum=1000,
            value=100,
            step=1,
            label="Max Run Steps",
            info="Maximum number of steps the agent will take",
            interactive=True
        )
        max_actions = gr.Slider(
            minimum=1,
            maximum=100,
            value=10,
            step=1,
            label="Max Number of Actions",
            info="Maximum number of actions the agent will take per step",
            interactive=True
        )

    with gr.Row():
        max_input_tokens = gr.Number(
            label="Max Input Tokens",
            value=128000,
            precision=0,
            interactive=True
        )
        tool_calling_method = gr.Dropdown(
            label="Tool Calling Method",
            value="auto",
            interactive=True,
            allow_custom_value=True,
            choices=['function_calling', 'json_mode', 'raw', 'auto', 'tools', "None"],
            visible=True
        )

    tab_components.update(dict(
        override_system_prompt=override_system_prompt,
        extend_system_prompt=extend_system_prompt,
        mcp_server_config=mcp_server_config,
        llm_provider=llm_provider,
        llm_model_name=llm_model_name,
        llm_temperature=llm_temperature,
        use_vision=use_vision,
        ollama_num_ctx=ollama_num_ctx,
        llm_base_url=llm_base_url,
        llm_api_key=llm_api_key,
        max_steps=max_steps,
        max_actions=max_actions,
        max_input_tokens=max_input_tokens,
        tool_calling_method=tool_calling_method,
    ))
    webui_manager.add_components("agent_settings", tab_components)

    llm_provider.change(
        fn=lambda x: gr.update(visible=x == "ollama"),
        inputs=llm_provider,
        outputs=ollama_num_ctx
    )
    llm_provider.change(
        lambda provider: update_model_dropdown(provider),
        inputs=[llm_provider],
        outputs=[llm_model_name]
    )


    # ============ Database Settings Management (when authenticated) ============
    if auth_manager is not None:
        gr.Markdown("---")
        gr.Markdown("### 💾 Agent Settings Database Management")
        
        with gr.Group():
            gr.Markdown("#### Save Current Settings")
            with gr.Row():
                setting_name_input = gr.Textbox(
                    label="Setting Name",
                    placeholder="Enter a name for this agent setting profile",
                    scale=2
                )
                setting_description = gr.Textbox(
                    label="Description (Optional)",
                    placeholder="Brief description",
                    scale=2
                )
            save_setting_btn = gr.Button("💾 Save Agent Settings", variant="primary")
            save_setting_status = gr.Markdown(visible=False)
        
        with gr.Group():
            gr.Markdown("#### Load / Delete Settings")
            with gr.Row():
                settings_dropdown = gr.Dropdown(
                    label="Select Saved Settings",
                    choices=[],
                    interactive=True,
                    scale=3
                )
                refresh_settings_btn = gr.Button("🔄 Refresh", scale=1)
            
            setting_info = gr.Markdown(visible=False)
            
            with gr.Row():
                load_setting_btn = gr.Button("📂 Load Selected", variant="primary")
                delete_setting_btn = gr.Button("🗑️ Delete Selected", variant="stop")
            
            load_setting_status = gr.Markdown(visible=False)
        
        with gr.Group():
            gr.Markdown("#### Your Saved Agent Settings")
            settings_table = gr.Dataframe(
                headers=["ID", "Name", "LLM Provider", "Model", "Description", "Last Updated"],
                datatype=["number", "str", "str", "str", "str", "str"],
                col_count=(6, "fixed"),
                interactive=False,
                visible=True
            )
        
        settings_ids_state = gr.State(value={})

        async def save_agent_setting_to_db(
                setting_name, description,
                override_prompt, extend_prompt, mcp_config,
                provider, model, temp, vision, ollama_ctx, base_url, api_key,
                steps, actions, tokens, tool_method,
                request: gr.Request = None  # Gradio injects this - NOT in inputs list
        ):
            """Save current agent settings to database"""
            if auth_manager is None:
                return gr.update(visible=True, value="❌ Authentication manager not initialized")

            if not setting_name or not setting_name.strip():
                return gr.update(visible=True, value="❌ Please enter a setting name")

            # Get user_id from cookies
            user_id = None
            if request is not None:
                print(f"All cookies: {dict(request.cookies)}")
                # Try common cookie names
                user_id = (
                        request.cookies.get("user_id") or
                        request.cookies.get("userID") or
                        request.cookies.get("userId")
                )
                print(f"user_id from cookie: {user_id}")

            # Fallback to session if no cookie
            if not user_id:
                user_id = auth_manager.get_current_user_id()
                print(f"user_id from session: {user_id}")

            if not user_id:
                return gr.update(visible=True, value="❌ Could not determine user ID")

            settings = {
                'override_system_prompt': override_prompt or '',
                'extend_system_prompt': extend_prompt or '',
                'mcp_server_config': mcp_config or '',
                'llm_provider': provider or 'openai',
                'llm_model_name': model or 'gpt-4o',
                'llm_temperature': temp if temp is not None else 0.6,
                'use_vision': vision if vision is not None else True,
                'ollama_num_ctx': ollama_ctx if ollama_ctx is not None else 16000,
                'llm_base_url': base_url or '',
                'llm_api_key': api_key or '',
                'max_steps': steps if steps is not None else 100,
                'max_actions': actions if actions is not None else 10,
                'max_input_tokens': tokens if tokens is not None else 128000,
                'tool_calling_method': tool_method or 'auto'
            }

            try:
                result = auth_manager.save_agent_setting(int(user_id), setting_name.strip(), settings)
                if result.get("success"):
                    return gr.update(visible=True, value=f"✅ {result['message']}")
                else:
                    return gr.update(visible=True, value=f"❌ {result.get('error', 'Unknown error')}")
            except Exception as e:
                logger.error(f"Exception during save: {e}", exc_info=True)
                return gr.update(visible=True, value=f"❌ Error: {str(e)}")
        def refresh_settings_list(request: gr.Request = None):

            """Refresh the list of saved agent settings"""
            try:
                # Get user_id from cookies
                user_id = None
                if request is not None:
                    print(f"All cookies: {dict(request.cookies)}")
                    # Try common cookie names
                    user_id = (
                            request.cookies.get("user_id") or
                            request.cookies.get("userID") or
                            request.cookies.get("userId")
                    )
                    print(f"user_id from cookie: {user_id}")

                # Fallback to session if no cookie
                if not user_id:
                    user_id = auth_manager.get_current_user_id()
                    print(f"user_id from session: {user_id}")

                if not user_id:
                    return gr.update(visible=True, value="❌ Could not determine user ID")
                result = auth_manager.get_agent_settings_list(user_id)
            except Exception as e:
                logger.error(f"Error refreshing settings: {e}")
                return (gr.update(choices=[], value=None), {}, gr.update(value=[], visible=True), gr.update(visible=True, value=f"❌ Error: {str(e)}"))
            
            if not result.get("success"):
                return (gr.update(choices=[], value=None), {}, gr.update(value=[], visible=True), gr.update(visible=True, value=f"❌ {result.get('error', 'Unknown error')}"))
            
            settings = result.get("settings", [])
            if not settings:
                return (gr.update(choices=[], value=None), {}, gr.update(value=[], visible=True), gr.update(visible=True, value="ℹ️ No saved settings found."))
            
            choices, id_mapping, table_data = [], {}, []
            for s in settings:
                # Parse settings JSON if stored as string
                settings_data = s
                if isinstance(s, str):
                    try:
                        settings_data = json.loads(s)
                    except json.JSONDecodeError:
                        settings_data = {}
                
                name = settings_data.get("setting_name", "Unnamed") if isinstance(settings_data, dict) else s.get("setting_name", "Unnamed")
                choices.append(name)
                id_mapping[name] = settings_data.get("id") if isinstance(settings_data, dict) else s.get("id")
                table_data.append([
                    settings_data.get("id", "") if isinstance(settings_data, dict) else s.get("id", ""),
                    name,
                    settings_data.get("llm_provider", "") if isinstance(settings_data, dict) else s.get("llm_provider", ""),
                    settings_data.get("llm_model_name", "") if isinstance(settings_data, dict) else s.get("llm_model_name", ""),
                    settings_data.get("description", "") if isinstance(settings_data, dict) else s.get("description", ""),
                    str(settings_data.get("updated_at", ""))[:19] if isinstance(settings_data, dict) else str(s.get("updated_at", ""))[:19]
                ])
            
            return (gr.update(choices=choices, value=choices[0] if choices else None), id_mapping, gr.update(value=table_data, visible=True), gr.update(visible=False))
        
        def load_agent_setting_from_db(setting_name, settings_ids,request: gr.Request = None):
            """Load agent settings from database"""

                # Get user_id from cookies
            user_id = None
            if request is not None:
                print(f"All cookies: {dict(request.cookies)}")
                    # Try common cookie names
            user_id = (
                        request.cookies.get("user_id") or
                        request.cookies.get("userID") or
                         request.cookies.get("userId")
                )
            print(f"user_id from cookie: {user_id}")

                # Fallback to session if no cookie
            if not user_id:
                    user_id = auth_manager.get_current_user_id()
                    print(f"user_id from session: {user_id}")

            if not user_id:
                    return gr.update(visible=True, value="❌ Could not determine user ID")
            if not setting_name:
                return tuple([gr.update(visible=True, value="❌ Please select a setting")] + [gr.update()] * 21)
            
            result = auth_manager.load_agent_setting(setting_name,user_id)
            if not result.get("success"):
                return tuple([gr.update(visible=True, value=f"❌ {result.get('error', 'Unknown error')}")] + [gr.update()] * 21)
            
            setting_data = result.get("setting", {})
            # Parse JSON string if it's a string
            if isinstance(setting_data, str):
                try:
                    setting_data = json.loads(setting_data)
                except json.JSONDecodeError:
                    setting_data = {}
            
            s = setting_data
            return (
                gr.update(visible=True, value=f"✅ Settings '{setting_name}' loaded!"),
                gr.update(value=s.get('override_system_prompt', '')),
                gr.update(value=s.get('extend_system_prompt', '')),
                gr.update(value=s.get('mcp_server_config', '')),
                gr.update(value=s.get('llm_provider', 'openai')),
                gr.update(value=s.get('llm_model_name', 'gpt-4o')),
                gr.update(value=s.get('llm_temperature', 0.6)),
                gr.update(value=s.get('use_vision', True)),
                gr.update(value=s.get('ollama_num_ctx', 16000)),
                gr.update(value=s.get('llm_base_url', '')),
                gr.update(value=s.get('llm_api_key', '')),
                gr.update(value=s.get('planner_llm_provider', '')),
                gr.update(value=s.get('planner_llm_model_name', '')),
                gr.update(value=s.get('planner_llm_temperature', 0.6)),
                gr.update(value=s.get('planner_use_vision', False)),
                gr.update(value=s.get('planner_ollama_num_ctx', 16000)),
                gr.update(value=s.get('planner_llm_base_url', '')),
                gr.update(value=s.get('planner_llm_api_key', '')),
                gr.update(value=s.get('max_steps', 100)),
                gr.update(value=s.get('max_actions', 10)),
                gr.update(value=s.get('max_input_tokens', 128000)),
                gr.update(value=s.get('tool_calling_method', 'auto'))
            )

        def delete_agent_setting_from_db(setting_name, settings_ids, request: gr.Request = None):
            user_id = None
            if request is not None:
                user_id = (
                        request.cookies.get("user_id") or
                        request.cookies.get("userID") or
                        request.cookies.get("userId")
                )
            if not user_id:
                user_id = auth_manager.get_current_user_id()

            if not setting_name:
                return (
                gr.update(visible=True, value="❌ Please select a setting"), gr.update(), settings_ids, gr.update())

            print(f"DEBUG setting_name={setting_name}, settings_ids={settings_ids}")

            # Get the real setting name from the id mapping
            real_name = None
            for name, sid in settings_ids.items():
                if str(sid) == str(setting_name) or name == setting_name:
                    real_name = name
                    break

            if not real_name:
                real_name = setting_name  # fallback

            print(f"DEBUG real_name={real_name}")
            result = auth_manager.db.delete_agent_setting_by_name(int(user_id), real_name)

            if result.get("success"):
                refresh_result = refresh_settings_list()
                return (
                    gr.update(visible=True, value=f"✅ {result['message']}"),
                    refresh_result[0],
                    refresh_result[1],
                    refresh_result[2]
                )
            return (
            gr.update(visible=True, value=f"❌ {result.get('error', 'Unknown error')}"), gr.update(), settings_ids,
            gr.update())
        def show_setting_info(setting_name, settings_ids):
            """Show information about selected setting"""
            if not setting_name:
                return gr.update(visible=False)
            result = auth_manager.load_agent_setting(setting_name)
            if result.get("success"):
                setting_data = result.get("setting", {})
                # Parse JSON string if it's a string
                if isinstance(setting_data, str):
                    try:
                        setting_data = json.loads(setting_data)
                    except json.JSONDecodeError:
                        setting_data = {}
                s = setting_data
                return gr.update(visible=True, value=f"**Provider:** {s.get('llm_provider', 'N/A')} | **Model:** {s.get('llm_model_name', 'N/A')}\n\n**Description:** {s.get('description', 'No description')}")
            return gr.update(visible=False)
        
        # Connect event handlers
        save_setting_btn.click(
            fn=save_agent_setting_to_db,
            inputs=[setting_name_input, setting_description, override_system_prompt, extend_system_prompt, mcp_server_config,
                    llm_provider, llm_model_name, llm_temperature, use_vision, ollama_num_ctx, llm_base_url, llm_api_key,
                    max_steps, max_actions, max_input_tokens, tool_calling_method],
            outputs=[save_setting_status]
        )
        refresh_settings_btn.click(
            fn=refresh_settings_list,
            inputs=[],
            outputs=[settings_dropdown, settings_ids_state, settings_table, load_setting_status]
        )
        load_setting_btn.click(
            fn=load_agent_setting_from_db,
            inputs=[settings_dropdown, settings_ids_state],
            outputs=[load_setting_status, override_system_prompt, extend_system_prompt, mcp_server_config,
                     llm_provider, llm_model_name, llm_temperature, use_vision, ollama_num_ctx, llm_base_url, llm_api_key,
                     max_steps, max_actions, max_input_tokens, tool_calling_method]
        )
        delete_setting_btn.click(
            fn=delete_agent_setting_from_db,
            inputs=[settings_dropdown, settings_ids_state],
            outputs=[load_setting_status, settings_dropdown, settings_ids_state, settings_table]
        )
        settings_dropdown.change(
            fn=show_setting_info,
            inputs=[settings_dropdown, settings_ids_state],
            outputs=[setting_info]
        )
        
        return refresh_settings_list, settings_dropdown, settings_ids_state, settings_table, load_setting_status
    
    return None
