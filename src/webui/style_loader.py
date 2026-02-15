"""
Helper module to load external CSS and JavaScript files
Keeps Python code clean by separating styles and scripts
"""

import os
from pathlib import Path


def get_static_dir():
    """Get the static directory path"""
    current_dir = Path(__file__).parent
    static_dir = current_dir / 'static'
    static_dir.mkdir(exist_ok=True)
    return static_dir


def load_css():
    """Load CSS from external file"""
    css_path = get_static_dir() / 'styles.css'
    if css_path.exists():
        with open(css_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


def load_javascript():
    """Load JavaScript from external file"""
    js_path = get_static_dir() / 'script.js'
    if js_path.exists():
        with open(js_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


def get_styles_and_scripts():
    """Get both CSS and JS in one call"""
    return {
        'css': load_css(),
        'js': load_javascript()
    }
