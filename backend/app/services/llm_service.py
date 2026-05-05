"""LLM服务模块"""

from typing import Optional

from langchain_openai import ChatOpenAI

from ..config import get_settings

_llm_instance: Optional[ChatOpenAI] = None


def get_llm() -> ChatOpenAI:
    """获取LangChain Chat模型实例。项目使用OpenAI兼容接口，可对接DashScope等模型服务。"""
    global _llm_instance

    if _llm_instance is None:
        settings = get_settings()

        if not settings.llm_api_key:
            raise ValueError("LLM_API_KEY未配置")

        _llm_instance = ChatOpenAI(
            model=settings.llm_model_id,
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            timeout=settings.llm_timeout,
            temperature=0.2,
        )

        print("✅ LangChain LLM服务初始化成功")
        print(f"   模型: {settings.llm_model_id}")
        print(f"   Base URL: {settings.llm_base_url}")

    return _llm_instance


def reset_llm():
    """重置LLM实例(用于测试或重新配置)"""
    global _llm_instance
    _llm_instance = None
