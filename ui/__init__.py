"""
وحدة واجهة المستخدم
تحتوي على جميع مكونات الواجهة الرسومية
"""

from ui.styles import inject_styles
from ui.sidebar import render_sidebar
from ui.tab_tashkeel import render_tab_tashkeel
from ui.tab_file import render_tab_file
from ui.tab_info import render_tab_info

__all__ = [
    "inject_styles",
    "render_sidebar",
    "render_tab_tashkeel",
    "render_tab_file",
    "render_tab_info",
]
