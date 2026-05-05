"""配置管理模块"""

from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """应用配置"""

    app_name: str = "智能旅行助手"
    app_version: str = "1.0.0"
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 8000

    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"

    database_url: str = "postgresql+psycopg://tripmind:tripmind123@127.0.0.1:5432/tripmind"
    jwt_secret_key: str = "change-this-secret-in-production"
    jwt_expire_minutes: int = 60 * 24 * 7

    # 默认管理员账号。普通注册入口不会创建管理员，后台首次启动时按这些环境变量初始化。
    default_admin_email: str = ""
    default_admin_username: str = "系统管理员"
    default_admin_password: str = ""

    amap_api_key: str = ""

    unsplash_access_key: str = ""
    unsplash_secret_key: str = ""

    # LLM 配置，字段名与 .env 中的 LLM_* 变量对应。
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model_id: str = "gpt-4"
    llm_timeout: float = 90.0

    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

    def get_cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(',')]


settings = Settings()


def get_settings() -> Settings:
    return settings


def validate_config():
    errors = []
    warnings = []

    if not settings.amap_api_key:
        errors.append("AMAP_API_KEY未配置")

    if not settings.llm_api_key:
        warnings.append("LLM_API_KEY未配置，LLM功能可能无法使用")

    if errors:
        raise ValueError("配置错误:\n" + "\n".join(f"  - {e}" for e in errors))

    if warnings:
        print("\n⚠️  配置警告:")
        for w in warnings:
            print(f"  - {w}")

    return True


def print_config():
    print(f"应用名称: {settings.app_name}")
    print(f"版本: {settings.app_version}")
    print(f"服务器: {settings.host}:{settings.port}")
    print(f"数据库: {settings.database_url}")
    print(f"默认管理员: {'已配置' if settings.default_admin_email and settings.default_admin_password else '未配置'}")
    print(f"高德地图API Key: {'已配置' if settings.amap_api_key else '未配置'}")
    print(f"LLM API Key: {'已配置' if settings.llm_api_key else '未配置'}")
    print(f"LLM Base URL: {settings.llm_base_url}")
    print(f"LLM Model: {settings.llm_model_id}")
    print(f"日志级别: {settings.log_level}")
