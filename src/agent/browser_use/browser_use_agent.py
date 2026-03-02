from __future__ import annotations

import logging
import os

from browser_use.agent.gif import create_history_gif  # noqa: F401 – re-exported for callers
from browser_use.agent.service import Agent
from browser_use.agent.views import (
    ActionResult,
    AgentHistory,
    AgentHistoryList,
    AgentStepInfo,
)
from browser_use.browser.views import BrowserStateHistory
from browser_use.utils import time_execution_async  # noqa: F401 – re-exported for callers
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

SKIP_LLM_API_KEY_VERIFICATION = (
    os.environ.get("SKIP_LLM_API_KEY_VERIFICATION", "false").lower()[0] in "ty1"
)


class BrowserUseAgent(Agent):
    """
    Thin subclass of browser_use.Agent.

    browser-use 0.12.0 removed AgentHookFunc / SignalHandler /
    is_model_without_tool_support / save_playwright_script_path, so all
    overrides that depended on those APIs have been removed.
    The parent Agent.run() is used directly.
    """
    pass
