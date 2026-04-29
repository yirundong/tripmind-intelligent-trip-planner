"""LLM服务模块"""

import os
from typing import Optional

from langchain_openai import ChatOpenAI

from ..config import get_settings

# 全局LLM实例
_llm_instance: Optional[ChatOpenAI] = None


def get_llm() -> ChatOpenAI:
    """
    获取LangChain Chat模型实例。

    Returns:
        ChatOpenAI实例。项目使用OpenAI兼容接口,可对接DashScope等模型服务。
    """
    global _llm_instance

    if _llm_instance is None:
        settings = get_settings()
        api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or settings.openai_api_key
        base_url = os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_BASE_URL") or settings.openai_base_url
        model = os.getenv("LLM_MODEL_ID") or os.getenv("OPENAI_MODEL") or settings.openai_model
        timeout = float(os.getenv("LLM_TIMEOUT", "90"))

        if not api_key:
            raise ValueError("LLM_API_KEY或OPENAI_API_KEY未配置")

        _llm_instance = ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            temperature=0.2,
        )

        print("✅ LangChain LLM服务初始化成功")
        print(f"   模型: {model}")
        print(f"   Base URL: {base_url}")

    return _llm_instance


def reset_llm():
    """重置LLM实例(用于测试或重新配置)"""
    global _llm_instance
    _llm_instance = None
