import asyncio
import json
import logging
import os
import uuid
from typing import Any, AsyncGenerator, Dict, Optional

import gradio as gr

# from browser_use.agent.service import Agent
from browser_use.agent.views import (
    AgentHistoryList,
    AgentOutput,
)
from browser_use.browser.browser import BrowserConfig
from browser_use.browser.context import BrowserContext, BrowserContextConfig
from browser_use.browser.views import BrowserState
from gradio.components import Component
from langchain_core.language_models.chat_models import BaseChatModel

from src.agent.browser_use.browser_use_agent import BrowserUseAgent
from src.browser.custom_browser import CustomBrowser
from src.controller.custom_controller import CustomController
from src.utils import llm_provider
from src.webui.webui_manager import WebuiManager

logger = logging.getLogger(__name__)


# --- Helper Functions ---


async def _initialize_llm(
        provider: Optional[str],
        model_name: Optional[str],
        temperature: float,
        base_url: Optional[str],
        api_key: Optional[str],
        num_ctx: Optional[int] = None,
        webui_manager: Optional[WebuiManager] = None,
) -> Optional[BaseChatModel]:
    """Initializes the LLM based on settings. Returns None if provider/model is missing.

    If api_key is not provided and webui_manager has an auth_manager,
    it will attempt to fetch the API key from the database.
    """
    if not provider or not model_name:
        logger.info("LLM Provider or Model Name not specified, LLM will be None.")
        return None

    # Try to get API key from database if not provided and auth_manager is available
    effective_api_key = api_key
    if not effective_api_key and webui_manager and hasattr(webui_manager, 'auth_manager') and webui_manager.auth_manager:
        auth_manager = webui_manager.auth_manager
        if auth_manager.is_authenticated():
            db_api_key = auth_manager.get_api_key_for_provider(provider)
            if db_api_key:
                effective_api_key = db_api_key
                logger.info(f"Using API key from database for provider: {provider}")

    try:
        logger.info(
            f"Initializing LLM: Provider={provider}, Model={model_name}, Temp={temperature}"
        )
        llm = llm_provider.get_llm_model(
            provider=provider,
            model_name=model_name,
            temperature=temperature,
            base_url=base_url or None,
            api_key=effective_api_key or None,
            num_ctx=num_ctx if provider == "ollama" else None,
        )
        return llm
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}", exc_info=True)
        gr.Warning(
            f"Failed to initialize LLM '{model_name}' for provider '{provider}'. Please check settings. Error: {e}"
        )
        return None


def _get_config_value(
        webui_manager: WebuiManager,
        comp_dict: Dict[gr.components.Component, Any],
        comp_id_suffix: str,
        default: Any = None,
) -> Any:
    """Safely get value from component dictionary using its ID suffix relative to the tab."""
    tab_name = "browser_use_agent"
    comp_id = f"{tab_name}.{comp_id_suffix}"
    try:
        comp = webui_manager.get_component_by_id(comp_id)
        return comp_dict.get(comp, default)
    except KeyError:
        for prefix in ["agent_settings", "browser_settings"]:
            try:
                comp_id = f"{prefix}.{comp_id_suffix}"
                comp = webui_manager.get_component_by_id(comp_id)
                return comp_dict.get(comp, default)
            except KeyError:
                continue
        logger.warning(
            f"Component with suffix '{comp_id_suffix}' not found in manager for value lookup."
        )
        return default


def _format_agent_output(model_output: AgentOutput) -> str:
    """Formats AgentOutput for display in the chatbot using JSON."""
    content = ""
    if model_output:
        try:
            action_dump = [
                action.model_dump(exclude_none=True) for action in model_output.action
            ]
            state_dump = model_output.current_state.model_dump(exclude_none=True)
            model_output_dump = {
                "current_state": state_dump,
                "action": action_dump,
            }
            json_string = json.dumps(model_output_dump, indent=4, ensure_ascii=False)
            content = f"<pre><code class='language-json'>{json_string}</code></pre>"

        except AttributeError as ae:
            logger.error(f"AttributeError during model dump: {ae}.")
            content = f"<pre><code>Error: Could not format agent output (AttributeError: {ae}).\nRaw output: {str(model_output)}</code></pre>"
        except Exception as e:
            logger.error(f"Error formatting agent output: {e}", exc_info=True)
            content = f"<pre><code>Error formatting agent output.\nRaw output:\n{str(model_output)}</code></pre>"

    return content.strip()


# --- Callbacks ---


async def _handle_new_step(
        webui_manager: WebuiManager, state: BrowserState, output: AgentOutput, step_num: int
):
    """Callback for each step taken by the agent, including screenshot display."""
    if not hasattr(webui_manager, "bu_chat_history"):
        logger.error("Attribute 'bu_chat_history' not found in webui_manager!")
        webui_manager.bu_chat_history = []

    step_num -= 1
    logger.info(f"Step {step_num} completed.")

    screenshot_html = ""
    screenshot_data = getattr(state, "screenshot", None)
    if screenshot_data:
        try:
            if isinstance(screenshot_data, str) and len(screenshot_data) > 100:
                img_tag = f'<img src="data:image/jpeg;base64,{screenshot_data}" alt="Step {step_num} Screenshot" style="max-width: 800px; max-height: 600px; object-fit:contain;" />'
                screenshot_html = img_tag + "<br/>"
            else:
                logger.warning(f"Screenshot for step {step_num} seems invalid.")
                screenshot_html = "**[Invalid screenshot data]**<br/>"
        except Exception as e:
            logger.error(f"Error processing screenshot for step {step_num}: {e}", exc_info=True)
            screenshot_html = "**[Error displaying screenshot]**<br/>"
    else:
        logger.debug(f"No screenshot available for step {step_num}.")

    formatted_output = _format_agent_output(output)

    step_header = f"--- **Step {step_num}** ---"
    final_content = step_header + "<br/>" + screenshot_html + formatted_output

    chat_message = {
        "role": "assistant",
        "content": final_content.strip(),
    }
    webui_manager.bu_chat_history.append(chat_message)

    await asyncio.sleep(0.05)


def _handle_done(webui_manager: WebuiManager, history: AgentHistoryList):
    """Callback when the agent finishes the task."""
    logger.info(
        f"Agent task finished. Duration: {history.total_duration_seconds():.2f}s, Tokens: {history.total_input_tokens()}"
    )
    final_summary = "**Task Completed**\n"
    final_summary += f"- Duration: {history.total_duration_seconds():.2f} seconds\n"
    final_summary += f"- Total Input Tokens: {history.total_input_tokens()}\n"

    final_result = history.final_result()
    if final_result:
        final_summary += f"- Final Result: {final_result}\n"

    errors = history.errors()
    if errors and any(errors):
        final_summary += f"- **Errors:**\n```\n{errors}\n```\n"
    else:
        final_summary += "- Status: Success\n"

    webui_manager.bu_chat_history.append(
        {"role": "assistant", "content": final_summary}
    )


async def _ask_assistant_callback(
        webui_manager: WebuiManager, query: str, browser_context: BrowserContext
) -> Dict[str, Any]:
    """Callback triggered by the agent's ask_for_assistant action."""
    logger.info("Agent requires assistance. Waiting for user input.")

    if not hasattr(webui_manager, "_chat_history"):
        logger.error("Chat history not found in webui_manager during ask_assistant!")
        return {"response": "Internal Error: Cannot display help request."}

    webui_manager.bu_chat_history.append(
        {
            "role": "assistant",
            "content": f"**Need Help:** {query}\nPlease provide information or perform the required action in the browser, then type your response/confirmation below and click 'Submit Response'.",
        }
    )

    webui_manager.bu_response_event = asyncio.Event()
    webui_manager.bu_user_help_response = None

    try:
        logger.info("Waiting for user response event...")
        await asyncio.wait_for(webui_manager.bu_response_event.wait(), timeout=3600.0)
        logger.info("User response event received.")
    except asyncio.TimeoutError:
        logger.warning("Timeout waiting for user assistance.")
        webui_manager.bu_chat_history.append(
            {"role": "assistant", "content": "**Timeout:** No response received. Trying to proceed."}
        )
        webui_manager.bu_response_event = None
        return {"response": "Timeout: User did not respond."}

    response = webui_manager.bu_user_help_response
    webui_manager.bu_chat_history.append({"role": "user", "content": response})
    webui_manager.bu_response_event = None
    return {"response": response}


# --- Core Agent Execution Logic ---


async def run_agent_task(
        webui_manager: WebuiManager, components: Dict[gr.components.Component, Any]
) -> AsyncGenerator[Dict[gr.components.Component, Any], None]:
    """Handles the entire lifecycle of initializing and running the agent."""

    # --- Get Components ---
    user_input_comp = webui_manager.get_component_by_id("browser_use_agent.user_input")
    run_button_comp = webui_manager.get_component_by_id("browser_use_agent.run_button")
    stop_button_comp = webui_manager.get_component_by_id("browser_use_agent.stop_button")
    pause_resume_button_comp = webui_manager.get_component_by_id("browser_use_agent.pause_resume_button")
    clear_button_comp = webui_manager.get_component_by_id("browser_use_agent.clear_button")
    chatbot_comp = webui_manager.get_component_by_id("browser_use_agent.chatbot")
    history_file_comp = webui_manager.get_component_by_id("browser_use_agent.agent_history_file")
    gif_comp = webui_manager.get_component_by_id("browser_use_agent.recording_gif")
    browser_view_comp = webui_manager.get_component_by_id("browser_use_agent.browser_view")

    # --- 1. Get Task ---
    task = components.get(user_input_comp, "").strip()
    if not task:
        gr.Warning("Please enter a task.")
        yield {run_button_comp: gr.update(interactive=True)}
        return

    webui_manager.bu_chat_history.append({"role": "user", "content": task})

    yield {
        user_input_comp: gr.Textbox(value="", interactive=False, placeholder="Agent is running..."),
        run_button_comp: gr.Button(value="⏳ Running...", interactive=False),
        stop_button_comp: gr.Button(interactive=True),
        pause_resume_button_comp: gr.Button(value="⏸️ Pause", interactive=True),
        clear_button_comp: gr.Button(interactive=False),
        chatbot_comp: gr.update(value=webui_manager.bu_chat_history),
        history_file_comp: gr.update(value=None),
        gif_comp: gr.update(value=None),
    }

    # --- Agent Settings ---
    def get_setting(key, default=None):
        comp = webui_manager.id_to_component.get(f"agent_settings.{key}")
        return components.get(comp, default) if comp else default

    override_system_prompt = get_setting("override_system_prompt") or None
    extend_system_prompt = get_setting("extend_system_prompt") or None
    llm_provider_name = get_setting("llm_provider", None)
    llm_model_name = get_setting("llm_model_name", None)
    llm_temperature = get_setting("llm_temperature", 0.6)
    use_vision = get_setting("use_vision", True)
    ollama_num_ctx = get_setting("ollama_num_ctx", 16000)
    llm_base_url = get_setting("llm_base_url") or None
    llm_api_key = get_setting("llm_api_key") or None
    max_steps = get_setting("max_steps", 100)
    max_actions = get_setting("max_actions", 10)
    max_input_tokens = get_setting("max_input_tokens", 128000)
    tool_calling_str = "auto"
    tool_calling_method = tool_calling_str if tool_calling_str != "None" else None
    mcp_server_config_comp = webui_manager.id_to_component.get("agent_settings.mcp_server_config")
    mcp_server_config_str = components.get(mcp_server_config_comp) if mcp_server_config_comp else None
    mcp_server_config = json.loads(mcp_server_config_str) if mcp_server_config_str else None

    # Planner LLM Settings (Optional)
    planner_llm_provider_name = get_setting("planner_llm_provider") or None
    planner_llm = None
    planner_use_vision = False
    if planner_llm_provider_name:
        planner_llm_model_name = get_setting("planner_llm_model_name")
        planner_llm_temperature = get_setting("planner_llm_temperature", 0.6)
        planner_ollama_num_ctx = get_setting("planner_ollama_num_ctx", 16000)
        planner_llm_base_url = get_setting("planner_llm_base_url") or None
        planner_llm_api_key = get_setting("planner_llm_api_key") or None
        planner_use_vision = get_setting("planner_use_vision", False)

        planner_llm = await _initialize_llm(
            planner_llm_provider_name,
            planner_llm_model_name,
            planner_llm_temperature,
            planner_llm_base_url,
            planner_llm_api_key,
            planner_ollama_num_ctx if planner_llm_provider_name == "ollama" else None,
            webui_manager,
        )

    # --- Browser Settings ---
    def get_browser_setting(key, default=None):
        comp = webui_manager.id_to_component.get(f"browser_settings.{key}")
        return components.get(comp, default) if comp else default

    browser_binary_path = get_browser_setting("browser_binary_path") or None
    browser_user_data_dir = get_browser_setting("browser_user_data_dir") or None
    use_own_browser = get_browser_setting("use_own_browser", False)
    keep_browser_open = get_browser_setting("keep_browser_open", False)
    headless = get_browser_setting("headless", False)
    disable_security = get_browser_setting("disable_security", False)
    window_w = int(get_browser_setting("window_w", 1280))
    window_h = int(get_browser_setting("window_h", 1100))
    cdp_url = get_browser_setting("cdp_url") or None
    wss_url = get_browser_setting("wss_url") or None
    save_recording_path = get_browser_setting("save_recording_path") or None
    save_trace_path = get_browser_setting("save_trace_path") or None
    save_agent_history_path = get_browser_setting("save_agent_history_path", "./tmp/agent_history")
    save_download_path = get_browser_setting("save_download_path", "./tmp/downloads")

    stream_vw = 70
    stream_vh = int(70 * window_h // window_w)

    os.makedirs(save_agent_history_path, exist_ok=True)
    if save_recording_path:
        os.makedirs(save_recording_path, exist_ok=True)
    if save_trace_path:
        os.makedirs(save_trace_path, exist_ok=True)
    if save_download_path:
        os.makedirs(save_download_path, exist_ok=True)

    # --- 2. Initialize LLM ---
    main_llm = await _initialize_llm(
        llm_provider_name,
        llm_model_name,
        llm_temperature,
        llm_base_url,
        llm_api_key,
        ollama_num_ctx if llm_provider_name == "ollama" else None,
        webui_manager,
    )

    async def ask_callback_wrapper(query: str, browser_context: BrowserContext) -> Dict[str, Any]:
        return await _ask_assistant_callback(webui_manager, query, browser_context)

    if not webui_manager.bu_controller:
        webui_manager.bu_controller = CustomController(ask_assistant_callback=ask_callback_wrapper)
        await webui_manager.bu_controller.setup_mcp_client(mcp_server_config)

    # --- 4. Initialize Browser and Context ---
    should_close_browser_on_finish = not keep_browser_open

    try:
        if not keep_browser_open:
            if webui_manager.bu_browser_context:
                logger.info("Closing previous browser context.")
                await webui_manager.bu_browser_context.close()
                webui_manager.bu_browser_context = None
            if webui_manager.bu_browser:
                logger.info("Closing previous browser.")
                await webui_manager.bu_browser.close()
                webui_manager.bu_browser = None

        if not webui_manager.bu_browser:
            logger.info("Launching new browser instance.")
            extra_args = []
            if use_own_browser:
                browser_binary_path = os.getenv("BROWSER_PATH", None) or browser_binary_path
                if browser_binary_path == "":
                    browser_binary_path = None
                browser_user_data = browser_user_data_dir or os.getenv("BROWSER_USER_DATA", None)
                if browser_user_data:
                    extra_args += [f"--user-data-dir={browser_user_data}"]
            else:
                browser_binary_path = None

            webui_manager.bu_browser = CustomBrowser(
                config=BrowserConfig(
                    headless=headless,
                    disable_security=disable_security,
                    browser_binary_path=browser_binary_path,
                    extra_browser_args=extra_args,
                    wss_url=wss_url,
                    cdp_url=cdp_url,
                    new_context_config=BrowserContextConfig(
                        window_width=window_w,
                        window_height=window_h,
                    )
                )
            )

        if not webui_manager.bu_browser_context:
            logger.info("Creating new browser context.")
            context_config = BrowserContextConfig(
                trace_path=save_trace_path if save_trace_path else None,
                save_recording_path=save_recording_path if save_recording_path else None,
                save_downloads_path=save_download_path if save_download_path else None,
                window_height=window_h,
                window_width=window_w,
            )
            if not webui_manager.bu_browser:
                raise ValueError("Browser not initialized, cannot create context.")
            webui_manager.bu_browser_context = (
                await webui_manager.bu_browser.new_context(config=context_config)
            )

        # --- 5. Initialize or Update Agent ---
        webui_manager.bu_agent_task_id = str(uuid.uuid4())
        os.makedirs(
            os.path.join(save_agent_history_path, webui_manager.bu_agent_task_id),
            exist_ok=True,
        )
        history_file = os.path.join(
            save_agent_history_path,
            webui_manager.bu_agent_task_id,
            f"{webui_manager.bu_agent_task_id}.json",
        )
        gif_path = os.path.join(
            save_agent_history_path,
            webui_manager.bu_agent_task_id,
            f"{webui_manager.bu_agent_task_id}.gif",
        )

        async def step_callback_wrapper(state: BrowserState, output: AgentOutput, step_num: int):
            await _handle_new_step(webui_manager, state, output, step_num)

        def done_callback_wrapper(history: AgentHistoryList):
            _handle_done(webui_manager, history)

        if not webui_manager.bu_agent:
            logger.info(f"Initializing new agent for task: {task}")
            if not webui_manager.bu_browser or not webui_manager.bu_browser_context:
                raise ValueError("Browser or Context not initialized, cannot create agent.")
            webui_manager.bu_agent = BrowserUseAgent(
                task=task,
                llm=main_llm,
                browser=webui_manager.bu_browser,
                browser_context=webui_manager.bu_browser_context,
                controller=webui_manager.bu_controller,
                register_new_step_callback=step_callback_wrapper,
                register_done_callback=done_callback_wrapper,
                use_vision=use_vision,
                override_system_message=override_system_prompt,
                extend_system_message=extend_system_prompt,
                max_input_tokens=max_input_tokens,
                max_actions_per_step=max_actions,
                tool_calling_method=tool_calling_method,
                planner_llm=planner_llm,
                use_vision_for_planner=planner_use_vision if planner_llm else False,
                source="webui",
            )
            webui_manager.bu_agent.state.agent_id = webui_manager.bu_agent_task_id
            webui_manager.bu_agent.settings.generate_gif = gif_path
        else:
            webui_manager.bu_agent.state.agent_id = webui_manager.bu_agent_task_id
            webui_manager.bu_agent.add_new_task(task)
            webui_manager.bu_agent.settings.generate_gif = gif_path
            webui_manager.bu_agent.browser = webui_manager.bu_browser
            webui_manager.bu_agent.browser_context = webui_manager.bu_browser_context
            webui_manager.bu_agent.controller = webui_manager.bu_controller

        # --- 6. Run Agent Task and Stream Updates ---
        agent_run_coro = webui_manager.bu_agent.run(max_steps=max_steps)
        agent_task = asyncio.create_task(agent_run_coro)
        webui_manager.bu_current_task = agent_task

        last_chat_len = len(webui_manager.bu_chat_history)
        while not agent_task.done():
            is_paused = webui_manager.bu_agent.state.paused
            is_stopped = webui_manager.bu_agent.state.stopped

            if is_paused:
                yield {
                    pause_resume_button_comp: gr.update(value="▶️ Resume", interactive=True),
                    stop_button_comp: gr.update(interactive=True),
                }
                while is_paused and not agent_task.done():
                    is_paused = webui_manager.bu_agent.state.paused
                    is_stopped = webui_manager.bu_agent.state.stopped
                    if is_stopped:
                        break
                    await asyncio.sleep(0.2)

                if agent_task.done() or is_stopped:
                    break

                yield {
                    pause_resume_button_comp: gr.update(value="⏸️ Pause", interactive=True),
                    run_button_comp: gr.update(value="⏳ Running...", interactive=False),
                }

            if is_stopped:
                logger.info("Agent has stopped.")
                if not agent_task.done():
                    try:
                        await asyncio.wait_for(agent_task, timeout=1.0)
                    except asyncio.TimeoutError:
                        logger.warning("Agent task did not finish quickly, cancelling.")
                        agent_task.cancel()
                    except Exception:
                        pass
                break

            update_dict = {}
            if webui_manager.bu_response_event is not None:
                update_dict = {
                    user_input_comp: gr.update(
                        placeholder="Agent needs help. Enter response and submit.",
                        interactive=True,
                    ),
                    run_button_comp: gr.update(value="✔️ Submit Response", interactive=True),
                    pause_resume_button_comp: gr.update(interactive=False),
                    stop_button_comp: gr.update(interactive=False),
                    chatbot_comp: gr.update(value=webui_manager.bu_chat_history),
                }
                last_chat_len = len(webui_manager.bu_chat_history)
                yield update_dict
                await webui_manager.bu_response_event.wait()

                if not agent_task.done():
                    yield {
                        user_input_comp: gr.update(placeholder="Agent is running...", interactive=False),
                        run_button_comp: gr.update(value="⏳ Running...", interactive=False),
                        pause_resume_button_comp: gr.update(interactive=True),
                        stop_button_comp: gr.update(interactive=True),
                    }
                else:
                    break

            if len(webui_manager.bu_chat_history) > last_chat_len:
                update_dict[chatbot_comp] = gr.update(value=webui_manager.bu_chat_history)
                last_chat_len = len(webui_manager.bu_chat_history)

            if headless and webui_manager.bu_browser_context:
                try:
                    screenshot_b64 = await webui_manager.bu_browser_context.take_screenshot()
                    if screenshot_b64:
                        html_content = f'<img src="data:image/jpeg;base64,{screenshot_b64}" style="width:{stream_vw}vw; height:{stream_vh}vh; border:1px solid #ccc;">'
                        update_dict[browser_view_comp] = gr.update(value=html_content, visible=True)
                    else:
                        html_content = f"<h1 style='width:{stream_vw}vw; height:{stream_vh}vh'>Waiting for browser session...</h1>"
                        update_dict[browser_view_comp] = gr.update(value=html_content, visible=True)
                except Exception as e:
                    logger.debug(f"Failed to capture screenshot: {e}")
                    update_dict[browser_view_comp] = gr.update(
                        value="<div style='...'>Error loading view...</div>", visible=True
                    )
            else:
                update_dict[browser_view_comp] = gr.update(visible=False)

            if update_dict:
                yield update_dict

            await asyncio.sleep(0.1)

        # --- 7. Task Finalization ---
        webui_manager.bu_agent.state.paused = False
        webui_manager.bu_agent.state.stopped = False
        final_update = {}
        try:
            logger.info("Agent task completing...")
            if not agent_task.done():
                await agent_task
            elif agent_task.exception():
                agent_task.result()
            logger.info("Agent task completed processing.")

            logger.info(f"Explicitly saving agent history to: {history_file}")
            webui_manager.bu_agent.save_history(history_file)

            if os.path.exists(history_file):
                final_update[history_file_comp] = gr.File(value=history_file)

            if gif_path and os.path.exists(gif_path):
                logger.info(f"GIF found at: {gif_path}")
                final_update[gif_comp] = gr.Image(value=gif_path)

        except asyncio.CancelledError:
            logger.info("Agent task was cancelled.")
            if not any(
                    "Cancelled" in msg.get("content", "")
                    for msg in webui_manager.bu_chat_history
                    if msg.get("role") == "assistant"
            ):
                webui_manager.bu_chat_history.append(
                    {"role": "assistant", "content": "**Task Cancelled**."}
                )
            final_update[chatbot_comp] = gr.update(value=webui_manager.bu_chat_history)
        except Exception as e:
            logger.error(f"Error during agent execution: {e}", exc_info=True)
            error_message = f"**Agent Execution Error:**\n```\n{type(e).__name__}: {e}\n```"
            if not any(
                    error_message in msg.get("content", "")
                    for msg in webui_manager.bu_chat_history
                    if msg.get("role") == "assistant"
            ):
                webui_manager.bu_chat_history.append(
                    {"role": "assistant", "content": error_message}
                )
            final_update[chatbot_comp] = gr.update(value=webui_manager.bu_chat_history)
            gr.Error(f"Agent execution failed: {e}")

        finally:
            webui_manager.bu_current_task = None

            if should_close_browser_on_finish:
                if webui_manager.bu_browser_context:
                    logger.info("Closing browser context after task.")
                    await webui_manager.bu_browser_context.close()
                    webui_manager.bu_browser_context = None
                if webui_manager.bu_browser:
                    logger.info("Closing browser after task.")
                    await webui_manager.bu_browser.close()
                    webui_manager.bu_browser = None

            # --- 8. Final UI Update ---
            final_update.update(
                {
                    user_input_comp: gr.update(value="", interactive=True, placeholder="Enter your next task..."),
                    run_button_comp: gr.update(value="▶️ Submit Task", interactive=True),
                    stop_button_comp: gr.update(value="⏹️ Stop", interactive=False),
                    pause_resume_button_comp: gr.update(value="⏸️ Pause", interactive=False),
                    clear_button_comp: gr.update(interactive=True),
                    chatbot_comp: gr.update(value=webui_manager.bu_chat_history),
                }
            )
            yield final_update

    except Exception as e:
        logger.error(f"Error setting up agent task: {e}", exc_info=True)
        webui_manager.bu_current_task = None
        yield {
            user_input_comp: gr.update(interactive=True, placeholder="Error during setup. Enter task..."),
            run_button_comp: gr.update(value="▶️ Submit Task", interactive=True),
            stop_button_comp: gr.update(value="⏹️ Stop", interactive=False),
            pause_resume_button_comp: gr.update(value="⏸️ Pause", interactive=False),
            clear_button_comp: gr.update(interactive=True),
            chatbot_comp: gr.update(
                value=webui_manager.bu_chat_history
                      + [{"role": "assistant", "content": f"**Setup Error:** {e}"}]
            ),
        }


# --- Button Click Handlers ---


async def handle_submit(
        webui_manager: WebuiManager, components: Dict[gr.components.Component, Any]
):
    """Handles clicks on the main 'Submit' button."""
    user_input_comp = webui_manager.get_component_by_id("browser_use_agent.user_input")
    user_input_value = components.get(user_input_comp, "").strip()

    # Case 1: Agent is waiting for user assistance → submit the help response
    if webui_manager.bu_response_event and not webui_manager.bu_response_event.is_set():
        logger.info(f"User submitted assistance: {user_input_value}")
        webui_manager.bu_user_help_response = (
            user_input_value if user_input_value else "User provided no text response."
        )
        webui_manager.bu_response_event.set()
        yield {
            user_input_comp: gr.update(
                value="",
                interactive=False,
                placeholder="Waiting for agent to continue...",
            ),
            webui_manager.get_component_by_id(
                "browser_use_agent.run_button"
            ): gr.update(value="⏳ Running...", interactive=False),
        }

    # Case 2: Agent already running → warn user
    elif webui_manager.bu_current_task and not webui_manager.bu_current_task.done():
        logger.warning("Submit clicked while agent is already running.")
        gr.Info("Agent is currently running. Please wait or use Stop/Pause.")
        yield {}

    # Case 3: New task → ✅ clear first, then run
    else:
        logger.info("New task submitted — clearing previous state before running.")

        # Step 1: clear previous agent state and reset UI
        clear_updates = await handle_clear(webui_manager)
        yield clear_updates

        # Step 2: run the new task
        logger.info("Starting new agent task after clear.")
        async for update in run_agent_task(webui_manager, components):
            yield update


async def handle_stop(webui_manager: WebuiManager):
    """Handles clicks on the 'Stop' button."""
    logger.info("Stop button clicked.")
    agent = webui_manager.bu_agent
    task = webui_manager.bu_current_task

    if agent and task and not task.done():
        agent.state.stopped = True
        agent.state.paused = False
        return {
            webui_manager.get_component_by_id("browser_use_agent.stop_button"): gr.update(
                interactive=False, value="⏹️ Stopping..."
            ),
            webui_manager.get_component_by_id("browser_use_agent.pause_resume_button"): gr.update(
                interactive=False
            ),
            webui_manager.get_component_by_id("browser_use_agent.run_button"): gr.update(
                interactive=False
            ),
        }
    else:
        logger.warning("Stop clicked but agent is not running.")
        return {
            webui_manager.get_component_by_id("browser_use_agent.run_button"): gr.update(interactive=True),
            webui_manager.get_component_by_id("browser_use_agent.stop_button"): gr.update(interactive=False),
            webui_manager.get_component_by_id("browser_use_agent.pause_resume_button"): gr.update(interactive=False),
            webui_manager.get_component_by_id("browser_use_agent.clear_button"): gr.update(interactive=True),
        }


async def handle_pause_resume(webui_manager: WebuiManager):
    """Handles clicks on the 'Pause/Resume' button."""
    agent = webui_manager.bu_agent
    task = webui_manager.bu_current_task

    if agent and task and not task.done():
        if agent.state.paused:
            logger.info("Resume button clicked.")
            agent.resume()
            return {
                webui_manager.get_component_by_id("browser_use_agent.pause_resume_button"): gr.update(
                    value="⏸️ Pause", interactive=True
                )
            }
        else:
            logger.info("Pause button clicked.")
            agent.pause()
            return {
                webui_manager.get_component_by_id("browser_use_agent.pause_resume_button"): gr.update(
                    value="▶️ Resume", interactive=True
                )
            }
    else:
        logger.warning("Pause/Resume clicked but agent is not running.")
        return {}


async def handle_clear(webui_manager: WebuiManager):
    """Handles clicks on the 'Clear' button and is called before every new task."""
    logger.info("Clearing agent state and resetting UI.")

    # Stop any running task first
    task = webui_manager.bu_current_task
    if task and not task.done():
        logger.info("Stopping current task before clear.")
        if webui_manager.bu_agent:
            webui_manager.bu_agent.stop()
        task.cancel()
        try:
            await asyncio.wait_for(task, timeout=2.0)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass
        except Exception as e:
            logger.warning(f"Error stopping task on clear: {e}")
    webui_manager.bu_current_task = None

    if webui_manager.bu_controller:
        await webui_manager.bu_controller.close_mcp_client()
        webui_manager.bu_controller = None
    webui_manager.bu_agent = None

    # Reset state
    webui_manager.bu_chat_history = []
    webui_manager.bu_response_event = None
    webui_manager.bu_user_help_response = None
    webui_manager.bu_agent_task_id = None

    logger.info("Agent state cleared successfully.")

    return {
        webui_manager.get_component_by_id("browser_use_agent.chatbot"): gr.update(value=[]),
        webui_manager.get_component_by_id("browser_use_agent.user_input"): gr.update(
            value="", placeholder="Enter your task here..."
        ),
        webui_manager.get_component_by_id("browser_use_agent.agent_history_file"): gr.update(value=None),
        webui_manager.get_component_by_id("browser_use_agent.recording_gif"): gr.update(value=None),
        webui_manager.get_component_by_id("browser_use_agent.browser_view"): gr.update(
            value="<div style='...'>Browser Cleared</div>"
        ),
        webui_manager.get_component_by_id("browser_use_agent.run_button"): gr.update(
            value="▶️ Submit Task", interactive=True
        ),
        webui_manager.get_component_by_id("browser_use_agent.stop_button"): gr.update(interactive=False),
        webui_manager.get_component_by_id("browser_use_agent.pause_resume_button"): gr.update(
            value="⏸️ Pause", interactive=False
        ),
        webui_manager.get_component_by_id("browser_use_agent.clear_button"): gr.update(interactive=True),
    }


# --- Tab Creation Function ---


def create_browser_use_agent_tab(webui_manager: WebuiManager):
    """
    Create the run agent tab, defining UI, state, and handlers.
    """
    webui_manager.init_browser_use_agent()

    tab_components = {}
    with gr.Column():
        chatbot = gr.Chatbot(
            lambda: webui_manager.bu_chat_history,
            elem_id="browser_use_chatbot",
            label="Agent Interaction",
            type="messages",
            height=600,
            show_copy_button=True,
        )
        user_input = gr.Textbox(
            label="Your Task or Response",
            placeholder="Enter your task here or provide assistance when asked.",
            lines=3,
            interactive=True,
            elem_id="user_input",
        )
        with gr.Row():
            stop_button = gr.Button("⏹️ Stop", interactive=False, variant="stop", scale=2)
            pause_resume_button = gr.Button(
                "⏸️ Pause", interactive=False, variant="secondary", scale=2, visible=True
            )
            clear_button = gr.Button("🗑️ Clear", interactive=True, variant="secondary", scale=2)
            run_button = gr.Button("▶️ Submit Task", variant="primary", scale=3)

        browser_view = gr.HTML(
            value="<div style='width:100%; height:50vh; display:flex; justify-content:center; align-items:center; border:1px solid #ccc; background-color:#f0f0f0;'><p>Browser View (Requires Headless=True)</p></div>",
            label="Browser Live View",
            elem_id="browser_view",
            visible=False,
        )
        with gr.Column():
            gr.Markdown("### Task Outputs")
            agent_history_file = gr.File(label="Agent History JSON", interactive=False)
            recording_gif = gr.Image(
                label="Task Recording GIF",
                format="gif",
                interactive=False,
                type="filepath",
            )

    tab_components.update(
        dict(
            chatbot=chatbot,
            user_input=user_input,
            clear_button=clear_button,
            run_button=run_button,
            stop_button=stop_button,
            pause_resume_button=pause_resume_button,
            agent_history_file=agent_history_file,
            recording_gif=recording_gif,
            browser_view=browser_view,
        )
    )
    webui_manager.add_components("browser_use_agent", tab_components)

    all_managed_components = list(webui_manager.get_components())
    run_tab_outputs = list(tab_components.values())

    async def submit_wrapper(*args) -> AsyncGenerator[Dict[Component, Any], None]:
        components_dict = dict(zip(all_managed_components, args))
        async for update in handle_submit(webui_manager, components_dict):
            yield update

    async def stop_wrapper() -> AsyncGenerator[Dict[Component, Any], None]:
        update_dict = await handle_stop(webui_manager)
        yield update_dict

    async def pause_resume_wrapper() -> AsyncGenerator[Dict[Component, Any], None]:
        update_dict = await handle_pause_resume(webui_manager)
        yield update_dict

    async def clear_wrapper() -> AsyncGenerator[Dict[Component, Any], None]:
        update_dict = await handle_clear(webui_manager)
        yield update_dict

    # --- Connect Event Handlers ---
    run_button.click(
        fn=submit_wrapper, inputs=all_managed_components, outputs=run_tab_outputs, trigger_mode="multiple"
    )
    user_input.submit(
        fn=submit_wrapper, inputs=all_managed_components, outputs=run_tab_outputs
    )
    stop_button.click(fn=stop_wrapper, inputs=None, outputs=run_tab_outputs)
    pause_resume_button.click(fn=pause_resume_wrapper, inputs=None, outputs=run_tab_outputs)
    clear_button.click(fn=clear_wrapper, inputs=None, outputs=run_tab_outputs)