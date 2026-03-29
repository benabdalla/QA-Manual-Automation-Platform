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
    if llm_provider in config.model_names:
        return gr.Dropdown(choices=config.model_names[llm_provider], value=config.model_names[llm_provider][0],
                           interactive=True)
    else:
        return gr.Dropdown(choices=[], value="", interactive=True, allow_custom_value=True)


async def update_mcp_server(mcp_file: str, webui_manager: WebuiManager):
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


# ── Build a pure HTML table with optional green row highlight ───────────────
def _build_html_table(table_data: list, highlighted_name: str = "") -> str:
    headers = ["ID", "Name", "LLM Provider", "Model", "Description", "Last Updated"]

    header_html = "".join(f"<th>{h}</th>" for h in headers)

    rows_html = ""
    for row in table_data:
        name_cell = str(row[1]) if len(row) > 1 else ""
        is_loaded = highlighted_name and name_cell == highlighted_name
        row_style = (
            'style="background-color:#d4edda; color:#155724; font-weight:600;"'
            if is_loaded else ""
        )
        cells = "".join(f"<td>{col}</td>" for col in row)
        rows_html += f"<tr {row_style}>{cells}</tr>"

    if not rows_html:
        rows_html = f'<tr><td colspan="{len(headers)}" style="text-align:center;color:#888;">No saved settings found.</td></tr>'

    return f"""
    <div style="overflow-x:auto; margin-top:8px;">
      <table style="width:100%; border-collapse:collapse; font-size:14px;">
        <thead>
          <tr style="background:#f0f0f0; border-bottom:2px solid #ccc;">
            {header_html}
          </tr>
        </thead>
        <tbody>
          {rows_html}
        </tbody>
      </table>
    </div>
    <style>
      table td, table th {{
        padding: 8px 12px;
        border-bottom: 1px solid #e0e0e0;
        text-align: left;
        white-space: nowrap;
      }}
      table tbody tr:hover td {{
        background-color: #f9f9f9;
      }}
    </style>
    """


def create_agent_settings_tab(webui_manager: WebuiManager, auth_manager=None):
    """
    Creates an agent settings tab with optional database save/load functionality.
    """
    input_components = set(webui_manager.get_components())
    tab_components = {}

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
                minimum=0.0, maximum=2.0, value=0.6, step=0.1,
                label="LLM Temperature",
                info="Controls randomness in model outputs",
                interactive=True
            )
            use_vision = gr.Checkbox(
                label="Use Vision", value=True,
                info="Enable Vision(Input highlighted screenshot into LLM)",
                interactive=True
            )
            ollama_num_ctx = gr.Slider(
                minimum=2 ** 8, maximum=2 ** 16, value=16000, step=1,
                label="Ollama Context Length",
                info="Controls max context length model needs to handle (less = faster)",
                visible=False, interactive=True
            )
        with gr.Row():
            llm_base_url = gr.Textbox(label="Base URL", value="", info="API endpoint URL (if required)")
            llm_api_key = gr.Textbox(label="API Key", type="password", value="",
                                     info="Your API key (leave blank to use .env)")

    with gr.Row():
        max_steps = gr.Slider(minimum=1, maximum=1000, value=100, step=1,
                              label="Max Run Steps",
                              info="Maximum number of steps the agent will take",
                              interactive=True)
        max_actions = gr.Slider(minimum=1, maximum=100, value=10, step=1,
                                label="Max Number of Actions",
                                info="Maximum number of actions the agent will take per step",
                                interactive=True)

    with gr.Row():
        max_input_tokens = gr.Number(label="Max Input Tokens", value=128000, precision=0, interactive=True)
        tool_calling_method = gr.Dropdown(
            label="Tool Calling Method", value="auto", interactive=True,
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

    llm_provider.change(fn=lambda x: gr.update(visible=x == "ollama"),
                        inputs=llm_provider, outputs=ollama_num_ctx)
    llm_provider.change(lambda provider: update_model_dropdown(provider),
                        inputs=[llm_provider], outputs=[llm_model_name])

    # ============ Database Settings Management ============
    if auth_manager is not None:
        gr.Markdown("---")
        gr.Markdown("### 💾 Agent Settings Database Management")

        # ── Inject button styles ─────────────────────────────────────────────
        gr.HTML("""
        <style>
          /* ── base reset for all icon buttons ── */
          .icon-btn button {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 42px !important;
            min-width: 42px !important;
            height: 42px !important;
            padding: 0 !important;
            border-radius: 10px !important;
            font-size: 20px !important;
            line-height: 1 !important;
            border: 1.5px solid transparent !important;
            cursor: pointer !important;
            transition: all 0.18s ease !important;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08) !important;
          }

          /* ── Save 💾 — soft blue ── */
          .btn-save button {
            background: #e8f0fe !important;
            border-color: #aac3f5 !important;
            color: #1a56db !important;
          }
          .btn-save button:hover {
            background: #1a56db !important;
            border-color: #1a56db !important;
            color: #ffffff !important;
            box-shadow: 0 4px 12px rgba(26,86,219,0.35) !important;
            transform: translateY(-1px) scale(1.06) !important;
          }
          .btn-save button:active {
            transform: translateY(0) scale(0.97) !important;
            box-shadow: 0 1px 4px rgba(26,86,219,0.2) !important;
          }

          /* ── Load 📂 — soft green ── */
          .btn-load button {
            background: #e6f9f0 !important;
            border-color: #6fcf97 !important;
            color: #1a7a4a !important;
          }
          .btn-load button:hover {
            background: #1a7a4a !important;
            border-color: #1a7a4a !important;
            color: #ffffff !important;
            box-shadow: 0 4px 12px rgba(26,122,74,0.35) !important;
            transform: translateY(-1px) scale(1.06) !important;
          }
          .btn-load button:active {
            transform: translateY(0) scale(0.97) !important;
          }

          /* ── Delete 🗑️ — soft red ── */
          .btn-delete button {
            background: #fdecea !important;
            border-color: #f5aca6 !important;
            color: #c0392b !important;
          }
          .btn-delete button:hover {
            background: #c0392b !important;
            border-color: #c0392b !important;
            color: #ffffff !important;
            box-shadow: 0 4px 12px rgba(192,57,43,0.35) !important;
            transform: translateY(-1px) scale(1.06) !important;
          }
          .btn-delete button:active {
            transform: translateY(0) scale(0.97) !important;
          }
        </style>
        """)

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
                # 💾 Save — soft blue, glows on hover
                save_setting_btn = gr.Button(
                    "💾", size="sm", scale=0, min_width=42,
                    elem_classes=["icon-btn", "btn-save"]
                )
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

            setting_info = gr.Markdown(visible=False)

            with gr.Row():
                # 📂 Load — soft green, glows on hover
                load_setting_btn = gr.Button(
                    "📂", size="sm",
                    elem_classes=["icon-btn", "btn-load"]
                )
                # 🗑️ Delete — soft red, glows on hover
                delete_setting_btn = gr.Button(
                    "🗑️", size="sm",
                    elem_classes=["icon-btn", "btn-delete"]
                )

            load_setting_status = gr.Markdown(visible=False)

        with gr.Group():
            gr.Markdown("#### Your Saved Agent Settings")
            settings_table_html = gr.HTML(value=_build_html_table([]))

        settings_ids_state = gr.State(value={})
        table_data_state = gr.State(value=[])
        loaded_name_state = gr.State(value="")

        # ── Helpers ─────────────────────────────────────────────────────────

        def _get_user_id(request):
            user_id = None
            if request is not None:
                print(f"All cookies: {dict(request.cookies)}")
                user_id = (
                    request.cookies.get("user_id") or
                    request.cookies.get("userID") or
                    request.cookies.get("userId")
                )
                print(f"user_id from cookie: {user_id}")
            if not user_id:
                user_id = auth_manager.get_current_user_id()
                print(f"user_id from session: {user_id}")
            return user_id

        def _do_refresh(user_id):
            if not user_id:
                return (
                    gr.update(choices=[], value=None), {},
                    [], gr.update(visible=True, value="❌ Could not determine user ID")
                )
            try:
                result = auth_manager.get_agent_settings_list(user_id)
            except Exception as e:
                logger.error(f"Error refreshing settings: {e}")
                return (
                    gr.update(choices=[], value=None), {},
                    [], gr.update(visible=True, value=f"❌ Refresh error: {str(e)}")
                )

            if not result.get("success"):
                return (
                    gr.update(choices=[], value=None), {},
                    [], gr.update(visible=True, value=f"❌ {result.get('error', 'Unknown error')}")
                )

            settings = result.get("settings", [])
            if not settings:
                return (
                    gr.update(choices=[], value=None), {},
                    [], gr.update(visible=True, value="ℹ️ No saved settings found.")
                )

            choices, id_mapping, table_data = [], {}, []
            for s in settings:
                settings_data = s
                if isinstance(s, str):
                    try:
                        settings_data = json.loads(s)
                    except json.JSONDecodeError:
                        settings_data = {}
                d = settings_data if isinstance(settings_data, dict) else s
                name = d.get("setting_name", "Unnamed")
                choices.append(name)
                id_mapping[name] = d.get("id")
                table_data.append([
                    d.get("id", ""),
                    name,
                    d.get("llm_provider", ""),
                    d.get("llm_model_name", ""),
                    d.get("description", ""),
                    str(d.get("updated_at", ""))[:19]
                ])

            return (
                gr.update(choices=choices, value=choices[0] if choices else None),
                id_mapping,
                table_data,
                gr.update(visible=False)
            )

        # ── Auto-load on page open (replaces Refresh button) ─────────────────
        # outputs: [dropdown, ids_state, table_html, table_data_state,
        #           load_status, loaded_name_state, setting_info]
        def refresh_settings_list(request: gr.Request = None):
            user_id = _get_user_id(request)
            dd, ids, rows, status = _do_refresh(user_id)

            # Auto-select first item and show its info panel
            first_name = rows[0][1] if rows else ""
            info_update = gr.update(visible=False)
            if first_name and user_id:
                result = auth_manager.load_agent_setting(first_name, user_id)
                if result.get("success"):
                    setting_data = result.get("setting", {})
                    if isinstance(setting_data, str):
                        try:
                            setting_data = json.loads(setting_data)
                        except json.JSONDecodeError:
                            setting_data = {}
                    s = setting_data
                    info_update = gr.update(
                        visible=True,
                        value=(
                            f"**Provider:** {s.get('llm_provider', 'N/A')} | "
                            f"**Model:** {s.get('llm_model_name', 'N/A')}"
                            f"**Description:** {s.get('description', 'No description')}"
                        )
                    )

            return (
                dd,                                        # settings_dropdown (value=first item)
                ids,                                       # settings_ids_state
                gr.update(value=_build_html_table(rows)),  # settings_table_html
                rows,                                      # table_data_state
                status,                                    # load_setting_status
                "",                                        # loaded_name_state
                info_update,                               # setting_info
            )

        # ── SAVE ─────────────────────────────────────────────────────────────
        async def save_agent_setting_to_db(
                setting_name, description,
                override_prompt, extend_prompt, mcp_config,
                provider, model, temp, vision, ollama_ctx, base_url, api_key,
                steps, actions, tokens, tool_method,
                request: gr.Request = None
        ):
            user_id = _get_user_id(request)

            if not setting_name or not setting_name.strip():
                dd, ids, rows, status = _do_refresh(user_id)
                return (
                    gr.update(visible=True, value="❌ Please enter a setting name"),
                    dd, ids, gr.update(value=_build_html_table(rows)), rows, status, ""
                )

            if not user_id:
                dd, ids, rows, status = _do_refresh(user_id)
                return (
                    gr.update(visible=True, value="❌ Could not determine user ID"),
                    dd, ids, gr.update(value=_build_html_table(rows)), rows, status, ""
                )

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
                save_status = (
                    gr.update(visible=True, value=f"✅ {result['message']}")
                    if result.get("success")
                    else gr.update(visible=True, value=f"❌ {result.get('error', 'Unknown error')}")
                )
            except Exception as e:
                logger.error(f"Exception during save: {e}", exc_info=True)
                save_status = gr.update(visible=True, value=f"❌ Error: {str(e)}")

            dd, ids, rows, _ = _do_refresh(user_id)
            return (
                save_status,
                dd, ids,
                gr.update(value=_build_html_table(rows)),
                rows,
                gr.update(visible=False),
                "",
            )

        # ── LOAD ──────────────────────────────────────────────────────────────
        _EMPTY = tuple([gr.update()] * 14)

        def load_agent_setting_from_db(setting_name, settings_ids, request: gr.Request = None):
            user_id = _get_user_id(request)
            dd, ids, rows, _ = _do_refresh(user_id)

            choices = dd.get("choices", []) if isinstance(dd, dict) else []
            dd_reset = gr.update(choices=choices, value=None)

            def _err(msg):
                return (
                    gr.update(visible=True, value=msg),
                    *_EMPTY,
                    dd_reset, ids,
                    gr.update(value=_build_html_table(rows, "")),
                    rows,
                    gr.update(visible=False),
                    "",
                )

            if not user_id:
                return _err("❌ Could not determine user ID")
            if not setting_name:
                return _err("❌ Please select a setting")

            result = auth_manager.load_agent_setting(setting_name, user_id)
            if not result.get("success"):
                return _err(f"❌ {result.get('error', 'Unknown error')}")

            setting_data = result.get("setting", {})
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
                gr.update(value=s.get('max_steps', 100)),
                gr.update(value=s.get('max_actions', 10)),
                gr.update(value=s.get('max_input_tokens', 128000)),
                gr.update(value=s.get('tool_calling_method', 'auto')),
                dd_reset,
                ids,
                gr.update(value=_build_html_table(rows, setting_name)),
                rows,
                gr.update(visible=False),
                setting_name,
            )

        # ── DELETE ────────────────────────────────────────────────────────────
        def delete_agent_setting_from_db(setting_name, settings_ids, request: gr.Request = None):
            user_id = _get_user_id(request)

            if not setting_name:
                dd, ids, rows, _ = _do_refresh(user_id)
                return (
                    gr.update(visible=True, value="❌ Please select a setting"),
                    dd, ids,
                    gr.update(value=_build_html_table(rows, "")),
                    rows, gr.update(visible=False), ""
                )

            print(f"DEBUG setting_name={setting_name}, settings_ids={settings_ids}")

            real_name = None
            for name, sid in settings_ids.items():
                if str(sid) == str(setting_name) or name == setting_name:
                    real_name = name
                    break
            if not real_name:
                real_name = setting_name

            print(f"DEBUG real_name={real_name}")
            result = auth_manager.db.delete_agent_setting_by_name(int(user_id), real_name)

            dd, ids, rows, _ = _do_refresh(user_id)
            status_msg = (
                f"✅ {result['message']}" if result.get("success")
                else f"❌ {result.get('error', 'Unknown error')}"
            )
            return (
                gr.update(visible=True, value=status_msg),
                dd, ids,
                gr.update(value=_build_html_table(rows, "")),
                rows,
                gr.update(visible=False),
                "",
            )

        # ── Show info on dropdown change ──────────────────────────────────────
        def show_setting_info(setting_name, settings_ids):
            if not setting_name:
                return gr.update(visible=False)
            user_id = auth_manager.get_current_user_id()
            if not user_id:
                return gr.update(visible=False)
            result = auth_manager.load_agent_setting(setting_name, user_id)
            if result.get("success"):
                setting_data = result.get("setting", {})
                if isinstance(setting_data, str):
                    try:
                        setting_data = json.loads(setting_data)
                    except json.JSONDecodeError:
                        setting_data = {}
                s = setting_data
                return gr.update(
                    visible=True,
                    value=(
                        f"**Provider:** {s.get('llm_provider', 'N/A')} | "
                        f"**Model:** {s.get('llm_model_name', 'N/A')}\n\n"
                        f"**Description:** {s.get('description', 'No description')}"
                    )
                )
            return gr.update(visible=False)

        # ── Wire up events ────────────────────────────────────────────────────

        # ─── outputs list reused by both load-triggers ──────────────────────
        _auto_load_outputs = [
            settings_dropdown,
            settings_ids_state,
            settings_table_html,
            table_data_state,
            load_setting_status,
            loaded_name_state,
            setting_info,
        ]

        # ✅ Trigger 1 — fires on initial page load (covers direct page open)
        # Uses a hidden Number that Gradio renders on startup; its "change" event
        # fires immediately, calling refresh_settings_list before the user does anything.
        _init_flag = gr.Number(value=1, visible=False)
        _init_flag.change(
            fn=refresh_settings_list,
            inputs=[],
            outputs=_auto_load_outputs,
        )

        # ✅ Trigger 2 — also register on the root Blocks.load so it fires when
        # the session connects, giving a second reliable trigger path.
        try:
            from gradio.context import Context
            _root = Context.root_block
            if _root is not None:
                _root.load(
                    fn=refresh_settings_list,
                    inputs=[],
                    outputs=_auto_load_outputs,
                )
        except Exception as _e:
            logger.warning(f"root_block.load() wiring skipped: {_e}")

        # Save
        save_setting_btn.click(
            fn=save_agent_setting_to_db,
            inputs=[
                setting_name_input, setting_description,
                override_system_prompt, extend_system_prompt, mcp_server_config,
                llm_provider, llm_model_name, llm_temperature, use_vision,
                ollama_num_ctx, llm_base_url, llm_api_key,
                max_steps, max_actions, max_input_tokens, tool_calling_method
            ],
            outputs=[
                save_setting_status,
                settings_dropdown, settings_ids_state,
                settings_table_html, table_data_state,
                load_setting_status, loaded_name_state,
            ]
        )

        # Load
        load_setting_btn.click(
            fn=load_agent_setting_from_db,
            inputs=[settings_dropdown, settings_ids_state],
            outputs=[
                load_setting_status,
                override_system_prompt, extend_system_prompt, mcp_server_config,
                llm_provider, llm_model_name, llm_temperature, use_vision,
                ollama_num_ctx, llm_base_url, llm_api_key,
                max_steps, max_actions, max_input_tokens, tool_calling_method,
                settings_dropdown, settings_ids_state,
                settings_table_html, table_data_state,
                load_setting_status, loaded_name_state,
            ]
        )

        # Delete
        delete_setting_btn.click(
            fn=delete_agent_setting_from_db,
            inputs=[settings_dropdown, settings_ids_state],
            outputs=[
                load_setting_status,
                settings_dropdown, settings_ids_state,
                settings_table_html, table_data_state,
                load_setting_status, loaded_name_state,
            ]
        )

        # Dropdown change → info panel
        settings_dropdown.change(
            fn=show_setting_info,
            inputs=[settings_dropdown, settings_ids_state],
            outputs=[setting_info]
        )

        return refresh_settings_list, settings_dropdown, settings_ids_state, settings_table_html, load_setting_status, loaded_name_state, setting_info

    return None