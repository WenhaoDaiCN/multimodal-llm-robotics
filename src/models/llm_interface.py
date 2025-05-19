"""
Large Language Model Interface for Embodied Agent

This module provides interfaces to various large language models and multimodal models
used by the embodied agent system.

"""

import os
import base64
import logging
from typing import List, Dict, Any, Optional, Union, Tuple
import json

# Import third-party libraries
from openai import OpenAI
import qianfan
from anthropic import Anthropic
import google.generativeai as genai

# Import configuration
from config import (
    OPENAI_API_KEY, OPENAI_ORG_ID, ANTHROPIC_API_KEY, GOOGLE_API_KEY,
    QWEN_API_KEY, YI_API_KEY, QIANFAN_ACCESS_KEY, QIANFAN_SECRET_KEY,
    APPBUILDER_TOKEN, DEFAULT_TEXT_MODEL, DEFAULT_VISION_MODEL
)
from agent.prompts import VISION_SYSTEM_PROMPT, VISUAL_QA_PROMPT

# Re-export system prompt for convenience
from agent.prompts import SYSTEM_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ====================== OpenAI GPT Models ======================

def query_openai_gpt(messages: List[Dict[str, str]], model: str = "gpt-4o") -> str:
    """
    Query OpenAI's GPT models.
    
    Args:
        messages: List of message dictionaries with role and content
        model: Model name to use (default: gpt-4o)
    
    Returns:
        Model response text
    """
    try:
        # OpenAI client setup with optional organization ID
        client_kwargs = {"api_key": OPENAI_API_KEY}
        if OPENAI_ORG_ID:
            client_kwargs["organization"] = OPENAI_ORG_ID
        
        client = OpenAI(**client_kwargs)
        
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
        )
        
        result = completion.choices[0].message.content.strip()
        return result
        
    except Exception as e:
        logger.error(f"Error querying OpenAI GPT: {e}")
        return '{"function": ["back_to_zero()"], "response": "I encountered an error with OpenAI GPT and need to reset."}'


# ====================== Anthropic Claude Models ======================

def query_claude(messages: List[Dict[str, str]], model: str = "claude-3-opus-20240229") -> str:
    """
    Query Anthropic's Claude models.
    
    Args:
        messages: List of message dictionaries with role and content
        model: Model name to use (default: claude-3-opus-20240229)
    
    Returns:
        Model response text
    """
    try:
        client = Anthropic(api_key=ANTHROPIC_API_KEY)
        
        # Convert messages format to Anthropic's expected format
        system_message = None
        formatted_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                formatted_messages.append(msg)
        
        # Create the message
        response = client.messages.create(
            model=model,
            system=system_message,
            messages=formatted_messages,
            temperature=0.3,
            max_tokens=2048
        )
        
        return response.content[0].text
        
    except Exception as e:
        logger.error(f"Error querying Claude: {e}")
        return '{"function": ["back_to_zero()"], "response": "I encountered an error with Claude and need to reset."}'


# ====================== Google Gemini Models ======================

def query_gemini(messages: List[Dict[str, str]], model: str = "gemini-1.5-pro") -> str:
    """
    Query Google's Gemini models.
    
    Args:
        messages: List of message dictionaries with role and content
        model: Model name to use (default: gemini-1.5-pro)
    
    Returns:
        Model response text
    """
    try:
        # Configure the Google Gemini API
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # Convert messages to Gemini format
        gemini_messages = []
        for msg in messages:
            if msg["role"] == "user":
                gemini_messages.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                gemini_messages.append({"role": "model", "parts": [msg["content"]]})
            # System messages handled differently in Gemini
        
        model = genai.GenerativeModel(model)
        response = model.generate_content(gemini_messages)
        
        return response.text
        
    except Exception as e:
        logger.error(f"Error querying Gemini: {e}")
        return '{"function": ["back_to_zero()"], "response": "I encountered an error with Gemini and need to reset."}'


# ====================== Yi Models ======================

def query_yi_llm(messages: List[Dict[str, str]], model: str = "yi-large") -> str:
    """
    Query the Yi large language model API.
    
    Args:
        messages: List of message dictionaries with role and content
        model: Model name to use (default: yi-large)
    
    Returns:
        Model response text
    """
    try:
        api_base = "https://api.lingyiwanwu.com/v1"
        
        # Access the LLM API
        client = OpenAI(api_key=YI_API_KEY, base_url=api_base)
        completion = client.chat.completions.create(model=model, messages=messages)
        result = completion.choices[0].message.content.strip()
        return result
        
    except Exception as e:
        logger.error(f"Error querying Yi LLM: {e}")
        return '{"function": ["back_to_zero()"], "response": "I encountered an error with Yi model and need to reset."}'


# ====================== Baidu Qianfan Models ======================

def query_qianfan_llm(prompt: str, model: str = "ERNIE-Bot-4") -> str:
    """
    Query the Baidu Qianfan LLM API.
    
    Args:
        prompt: Text prompt for the model
        model: Model name to use (default: ERNIE-Bot-4)
    
    Returns:
        Model response text
    """
    try:
        # Set API access credentials
        os.environ["QIANFAN_ACCESS_KEY"] = QIANFAN_ACCESS_KEY
        os.environ["QIANFAN_SECRET_KEY"] = QIANFAN_SECRET_KEY
        
        chat_comp = qianfan.ChatCompletion(model=model)
        
        # Query the model
        resp = chat_comp.do(
            messages=[{"role": "user", "content": prompt}], 
            top_p=0.8, 
            temperature=0.3, 
            penalty_score=1.0
        )
        
        response = resp["result"]
        return response
        
    except Exception as e:
        logger.error(f"Error querying Qianfan LLM: {e}")
        return '{"function": ["back_to_zero()"], "response": "I encountered an error with Qianfan and need to reset."}'


# ====================== Unified Interface ======================

def query_text_llm(prompt: str, model_name: str = None) -> str:
    """
    Query LLM with a text prompt using a specified model or default with fallback mechanism.
    
    Args:
        prompt: Text prompt for the model
        model_name: Optional model name to use (e.g., 'openai', 'claude', etc.)
                   If None, uses DEFAULT_TEXT_MODEL from config
    
    Returns:
        Model response text
    """
    # If no model specified, use the default
    if model_name is None:
        model_name = DEFAULT_TEXT_MODEL
    
    model_name = model_name.lower()
    messages = [{"role": "user", "content": prompt}]
    
    # Try the selected model first
    try:
        if model_name == "openai":
            return query_openai_gpt(messages)
        elif model_name == "claude":
            return query_claude(messages)
        elif model_name == "gemini":
            return query_gemini(messages)
        elif model_name == "yi":
            return query_yi_llm(messages)
        elif model_name == "qianfan":
            return query_qianfan_llm(prompt)  # Different signature
        else:
            logger.warning(f"Unknown model name: {model_name}, falling back to OpenAI")
            return query_openai_gpt(messages)
    
    except Exception as e:
        logger.error(f"Error with primary model {model_name}: {e}. Trying fallback...")
        
        # Fallback chain: OpenAI -> Yi -> Qianfan
        try:
            return query_openai_gpt(messages)
        except Exception:
            try:
                return query_yi_llm(messages)
            except Exception:
                return query_qianfan_llm(prompt)


# ====================== Message History Interface ======================

def query_llm_with_history(messages: List[Dict[str, str]], model_name: str = None) -> str:
    """
    Query LLM with a message history using a specified model or default with fallback mechanism.
    
    Args:
        messages: List of message dictionaries with role and content
        model_name: Optional model name to use (e.g., 'openai', 'claude', etc.)
                  If None, uses DEFAULT_TEXT_MODEL from config
    
    Returns:
        Model response text
    """
    # If no model specified, use the default
    if model_name is None:
        model_name = DEFAULT_TEXT_MODEL
    
    model_name = model_name.lower()
    
    # Try the selected model first
    try:
        if model_name == "openai":
            return query_openai_gpt(messages)
        elif model_name == "claude":
            return query_claude(messages)
        elif model_name == "gemini":
            return query_gemini(messages)
        elif model_name == "yi":
            return query_yi_llm(messages)
        elif model_name == "qianfan":
            # Qianfan interface is different, extract the last user message if possible
            last_user_message = ""
            for msg in reversed(messages):
                if msg["role"] == "user":
                    last_user_message = msg["content"]
                    break
            return query_qianfan_llm(last_user_message)
        else:
            logger.warning(f"Unknown model name: {model_name}, falling back to OpenAI")
            return query_openai_gpt(messages)
    
    except Exception as e:
        logger.error(f"Error with primary model {model_name}: {e}. Trying fallback...")
        
        # Fallback chain: OpenAI -> Yi -> Qianfan
        try:
            return query_openai_gpt(messages)
        except Exception:
            try:
                return query_yi_llm(messages)
            except Exception:
                # Extract the last user message for Qianfan if possible
                last_user_message = ""
                for msg in reversed(messages):
                    if msg["role"] == "user":
                        last_user_message = msg["content"]
                        break
                return query_qianfan_llm(last_user_message)


# ====================== Multimodal Vision Models ======================

def query_openai_vision(instruction: str, img_path: str, model: str = "gpt-4o") -> Union[Dict[str, Any], str]:
    """
    Query OpenAI's vision models for image understanding.
    
    Args:
        instruction: Text instruction or question
        img_path: Path to the image file
        model: Model name to use (default: gpt-4o)
        
    Returns:
        Model response (dict for localization tasks, str for QA)
    """
    try:
        # OpenAI client setup with optional organization ID
        client_kwargs = {"api_key": OPENAI_API_KEY}
        if OPENAI_ORG_ID:
            client_kwargs["organization"] = OPENAI_ORG_ID
        
        client = OpenAI(**client_kwargs)
        
        # Encode image as base64
        with open(img_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Create the message with text and image
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": instruction},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                        }
                    ]
                }
            ],
            max_tokens=2048
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Parse response if it's a localization task
        if "localize" in instruction.lower() or "locate" in instruction.lower():
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                logger.error(f"Error parsing OpenAI vision response as JSON: {response_text}")
                return {"error": "Failed to parse localization data"}
        
        return response_text
        
    except Exception as e:
        logger.error(f"Error querying OpenAI vision: {e}")
        return "I encountered an error analyzing the image."


def query_gemini_vision(instruction: str, img_path: str) -> str:
    """
    Query Google's Gemini for image understanding.
    
    Args:
        instruction: Text instruction or question
        img_path: Path to the image file
        
    Returns:
        Model response text
    """
    try:
        # Configure the Google Gemini API
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # Load the image
        image = genai.upload_file(img_path)
        
        # Create and invoke the model
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content([instruction, image])
        
        return response.text
        
    except Exception as e:
        logger.error(f"Error querying Gemini vision: {e}")
        return "I encountered an error analyzing the image with Gemini."


def query_qwen_vision(instruction: str, img_path: str, vision_option: int = 0) -> Union[Dict[str, Any], str]:
    """
    Query Qwen VL model with image and text.
    
    Args:
        instruction: Text instruction or question
        img_path: Path to the image file
        vision_option: 0 for object localization, 1 for visual QA
    
    Returns:
        Model response for the image understanding task (dict for localization, str for QA)
    """
    try:
        # Configure system prompt based on task type
        if vision_option == 0:
            system_prompt = VISION_SYSTEM_PROMPT
        else:
            system_prompt = VISUAL_QA_PROMPT
        
        # Using Qwen VL model via OpenAI-compatible API
        client = OpenAI(
            api_key=QWEN_API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        # Encode image as base64
        with open(img_path, 'rb') as image_file:
            image = 'data:image/jpeg;base64,' + base64.b64encode(image_file.read()).decode('utf-8')
        
        # Create request to the model
        completion = client.chat.completions.create(
            model="qwen-vl-max-2024-11-19",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": system_prompt + instruction
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image
                            }
                        }
                    ]
                },
            ]
        )
        
        # Parse response based on task type
        response_text = completion.choices[0].message.content.strip()
        
        if vision_option == 0:  # Object localization
            try:
                result = eval(response_text)
                return result
            except:
                logger.error(f"Error parsing Qwen vision response: {response_text}")
                return {"start": "unknown", "start_xyxy": [[0, 0], [0, 0]], 
                        "end": "unknown", "end_xyxy": [[0, 0], [0, 0]]}
        else:  # Visual QA
            return response_text
            
    except Exception as e:
        logger.error(f"Error querying Qwen vision API: {e}")
        if vision_option == 0:
            return {"start": "unknown", "start_xyxy": [[0, 0], [0, 0]], 
                    "end": "unknown", "end_xyxy": [[0, 0], [0, 0]]}
        else:
            return "I cannot identify the objects in the image due to an error."


def query_vision_api(instruction: str, img_path: str, vision_option: int = 0, model_name: str = None) -> Union[Dict[str, Any], str]:
    """
    Query a multimodal vision model with image and text using specified model or default.
    
    Args:
        instruction: Text instruction or question
        img_path: Path to the image file
        vision_option: 0 for object localization, 1 for visual QA
        model_name: Optional model name to use (e.g., 'openai', 'gemini', 'qwen')
                  If None, uses DEFAULT_VISION_MODEL from config
    
    Returns:
        Model response for the image understanding task
    """
    # If no model specified, use the default
    if model_name is None:
        model_name = DEFAULT_VISION_MODEL
    
    model_name = model_name.lower()
    
    # Try the selected model first
    try:
        if model_name == "openai":
            return query_openai_vision(instruction, img_path)
        elif model_name == "gemini":
            return query_gemini_vision(instruction, img_path)
        elif model_name == "qwen":
            return query_qwen_vision(instruction, img_path, vision_option)
        else:
            logger.warning(f"Unknown vision model: {model_name}, falling back to Qwen")
            return query_qwen_vision(instruction, img_path, vision_option)
    
    except Exception as e:
        logger.error(f"Error with vision model {model_name}: {e}. Trying fallback...")
        
        # Fallback chain: OpenAI -> Qwen -> Gemini
        try:
            return query_openai_vision(instruction, img_path)
        except Exception:
            try:
                return query_qwen_vision(instruction, img_path, vision_option)
            except Exception:
                return query_gemini_vision(instruction, img_path)
"""
