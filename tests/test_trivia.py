import pytest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from TriviaRoyale import TriviaGame

def test_categories_not_empty():
    """Test that categories list is not empty"""
    from TriviaRoyale import CATEGORIES
    assert len(CATEGORIES) > 0

def test_colors_contain_required_keys():
    """Test that COLORS dictionary contains required keys"""
    from TriviaRoyale import COLORS
    required_colors = ["light_blue", "soft_yellow", "dark_teal"]
    for color in required_colors:
        assert color in COLORS

def test_fonts_contain_required_keys():
    """Test that FONTS dictionary contains required keys"""
    from TriviaRoyale import FONTS
    required_fonts = ["large", "medium", "small"]
    for font in required_fonts:
        assert font in FONTS