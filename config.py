#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
from typing import Dict, Any

# Function to load API keys from environment variables with fallback to defaults


def get_env_var(var_name: str, default: str) -> str:
    return os.environ.get(var_name, default)

# ==================== LLM API Keys ====================


# OpenAI API (GPT models)
OPENAI_API_KEY = get_env_var("KEY", "")
OPENAI_ORG_ID = get_env_var("OPENAI_ORG_ID", "")  # Optional

# Anthropic API (Claude models)
ANTHROPIC_API_KEY = get_env_var("KEY", "")

# Qwen VL Series API (Aliyun Bailian)
QWEN_API_KEY = get_env_var("KEY", "")


# Default LLM to use (can be changed at runtime)
# Options: openai, claude, gemini, yi, qianfan
DEFAULT_TEXT_MODEL = get_env_var("DEFAULT_TEXT_MODEL", "openai")
DEFAULT_VISION_MODEL = get_env_var(
    "DEFAULT_VISION_MODEL", "qwen")  # Options: openai, gemini, qwen

# ==================== Robot Configuration ====================

ROBOT_CONFIG = {
    "safe_height": 220,         # Safe height for arm movement
    "default_speed": 40,        # Default movement speed
    "coordinate_speed": 20,     # Speed for coordinate-based movement
    "default_gripper_angle": 90  # Default gripper angle
}

# ==================== System Paths ====================

PATHS = {
    "temp_dir": "temp/",
    "assets_dir": "assets/",
    "audio_dir": "assets/audio/",
    "fonts_dir": "assets/fonts/"
}

# ==================== Audio Configuration ====================

AUDIO_CONFIG = {
    "mic_index": 1,            # Default microphone index
    "sample_rate": 16000,      # Audio sample rate
    "quiet_threshold": 700,    # Threshold for silence detection
    "channels": 1,             # Audio channels
    "chunk_size": 1024         # Audio chunk size
}
