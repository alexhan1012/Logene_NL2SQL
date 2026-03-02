import os
import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .schemas import TABLES

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")


DB_VENDOR_HINTS = {
    "sqlserver": "请生成 Microsoft SQL Server (T-SQL) 语法的SQL。注意：使用 TOP 代替 LIMIT，使用 GETDATE() 获取当前时间，字符串拼接使用 +，使用 ISNULL 而非 IFNULL。",
    "oracle": "请生成 Oracle 数据库语法的SQL。注意：使用 ROWNUM 或 FETCH FIRST 限制行数，使用 SYSDATE 或 SYSTIMESTAMP 获取当前时间，使用 NVL 而非 IFNULL，字符串拼接使用 ||。",
    "postgresql": "请生成 PostgreSQL 语法的SQL。注意：使用 LIMIT 限制行数，使用 NOW() 或 CURRENT_TIMESTAMP 获取当前时间，使用 COALESCE 而非 IFNULL，支持 ILIKE 不区分大小写匹配。",
    "mysql": "请生成 MySQL 语法的SQL。注意：使用 LIMIT 限制行数，使用 NOW() 获取当前时间，使用 IFNULL，字符串拼接使用 CONCAT()。",
    "kingbasees": "请生成人大金仓(KingbaseES)数据库语法的SQL。KingbaseES 兼容 PostgreSQL 语法，使用 LIMIT 限制行数，使用 NOW() 获取当前时间，使用 COALESCE 而非 IFNULL。",
    "dm": "请生成达梦(DM)数据库语法的SQL。达梦数据库兼容 Oracle 语法，使用 ROWNUM 限制行数，使用 SYSDATE 获取当前时间，使用 NVL。",
}


def _extract_json(content: str) -> str:
    """Strip markdown code fences from LLM response to get raw JSON."""
    content = content.strip()
    if "```" in content:
        parts = content.split("```")
        if len(parts) >= 2:
            inner = parts[1]
            if inner.startswith("json"):
                inner = inner[4:]
            return inner.strip()
    # Try to find JSON object directly
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1:
        return content[start:end + 1]
    return content


class NL2SQLService:
    def __init__(self, api_key=None, base_url=None, model=None, provider=None):
        """Initialize the service. If parameters are provided, use them; otherwise read from env."""
        if api_key and base_url and model:
            self.llm = ChatOpenAI(
                base_url=base_url,
                model=model,
                api_key=api_key,
            )
            return

        provider = provider or os.getenv("LLM_PROVIDER", "bailian").strip().lower()
        provider_config = {
            "bailian": {
                "api_key": os.getenv("BAILIAN_API_KEY", "").strip(),
                "base_url": os.getenv("BAILIAN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
                "model": os.getenv("BAILIAN_MODEL", "qwen-max"),
                "error_help": (
                    "1. 访问阿里云百炼控制台 (https://bailian.console.aliyun.com/)\n"
                    "2. 获取你的 API 密钥\n"
                    "3. 编辑 backend/.env 文件\n"
                    "4. 设置 BAILIAN_API_KEY=你的实际_API_密钥\n"
                    "5. 重启后端服务"
                ),
            },
            "ark": {
                "api_key": os.getenv("ARK_API_KEY", "").strip(),
                "base_url": os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
                "model": os.getenv("ARK_MODEL", "doubao-pro-32k-241215"),
                "error_help": (
                    "1. 访问火山引擎控制台 (https://console.volcengine.com/)\n"
                    "2. 获取你的 API 密钥\n"
                    "3. 编辑 backend/.env 文件\n"
                    "4. 设置 ARK_API_KEY=你的实际_API_密钥\n"
                    "5. 重启后端服务"
                ),
            },
            "siliconflow": {
                "api_key": os.getenv("SILICONFLOW_API_KEY", "").strip(),
                "base_url": os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1"),
                "model": os.getenv("SILICONFLOW_MODEL", "deepseek-ai/DeepSeek-V3"),
                "error_help": (
                    "1. 访问硅基流动控制台 (https://cloud.siliconflow.cn/)\n"
                    "2. 获取你的 API 密钥\n"
                    "3. 编辑 backend/.env 文件\n"
                    "4. 设置 SILICONFLOW_API_KEY=你的实际_API_密钥\n"
                    "5. 重启后端服务"
                ),
            },
        }
        if provider not in provider_config:
            supported_providers = " 或 ".join(sorted(provider_config.keys()))
            raise ValueError(f"[ERROR] 不支持的 LLM_PROVIDER，请使用 {supported_providers}")
        config = provider_config[provider]
        api_key = config["api_key"]

        # 检查 API 密钥
        if not api_key or api_key == "your_api_key_here":
            raise ValueError(f"[ERROR] 缺少有效的 API 密钥配置\n\n请完成以下步骤：\n{config['error_help']}")

        self.llm = ChatOpenAI(
            base_url=config["base_url"],
            model=config["model"],
            api_key=api_key,
        )

    def select_tables(self, question: str, tables_dict: dict) -> list:
        table_summary = "\n".join([
            f"- {name}: {info['description']}"
            for name, info in tables_dict.items()
        ])

        messages = [
            SystemMessage(content="""你是一个SQL专家。根据用户的问题，从给定的数据库表列表中选择需要用到的表。
只返回JSON格式，例如: {"tables": ["T_JCXX", "T_LK"]}
不要返回任何其他内容。"""),
            HumanMessage(content=f"""数据库表列表：
{table_summary}

用户问题：{question}

请选择需要用到的表（只返回JSON）：""")
        ]

        response = self.llm.invoke(messages)
        result = json.loads(_extract_json(response.content))
        return result.get("tables", [])

    def generate_sql(self, question: str, selected_tables: list, tables_dict: dict,
                     conversation_history: list = None, db_vendor: str = None) -> dict:
        schema_details = []
        for table_name in selected_tables:
            if table_name in tables_dict:
                table = tables_dict[table_name]
                fields_str = "\n".join([
                    f"  - {f['name']} ({f['type']}): {f['description']}"
                    for f in table['fields']
                ])
                schema_details.append(f"表名: {table_name}\n描述: {table['description']}\n字段:\n{fields_str}")

        schema_str = "\n\n".join(schema_details)

        history_str = ""
        if conversation_history:
            for msg in conversation_history[-6:]:
                role = "用户" if msg["role"] == "user" else "助手"
                history_str += f"{role}: {msg['content']}\n"

        vendor_hint = ""
        if db_vendor and db_vendor in DB_VENDOR_HINTS:
            vendor_hint = f"\n\n重要：{DB_VENDOR_HINTS[db_vendor]}"

        messages = [
            SystemMessage(content=f"""你是一个SQL专家，专门处理数据库查询。
根据用户问题和提供的表结构，生成准确的SQL查询语句。
所有表都通过F_BLH(病理号)关联。{vendor_hint}

返回JSON格式：
{{
  "sql": "SELECT语句",
  "joins": ["JOIN条件描述1", "JOIN条件描述2"],
  "explanation": "查询逻辑说明"
}}
只返回JSON，不要其他内容。"""),
            HumanMessage(content=f"""相关表结构：
{schema_str}

{("对话历史：" + chr(10) + history_str) if history_str else ""}

用户问题：{question}

请生成SQL查询（只返回JSON）：""")
        ]

        response = self.llm.invoke(messages)
        result = json.loads(_extract_json(response.content))
        return {
            "sql": result.get("sql", ""),
            "joins": result.get("joins", []),
            "explanation": result.get("explanation", ""),
            "tables_used": selected_tables
        }

    async def process_question(self, question: str, conversation_history: list = None,
                               tables_dict: dict = None, db_vendor: str = None) -> dict:
        if tables_dict is None:
            tables_dict = TABLES

        selected_tables = self.select_tables(question, tables_dict)
        if not selected_tables:
            first_table = next(iter(tables_dict), None)
            if first_table:
                selected_tables = [first_table]

        result = self.generate_sql(question, selected_tables, tables_dict, conversation_history, db_vendor)
        return result
