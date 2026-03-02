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
        timeout_raw = os.getenv("LLM_TIMEOUT_SECONDS", "90").strip()
        try:
            llm_timeout = float(timeout_raw)
            if llm_timeout <= 0:
                llm_timeout = 90.0
        except ValueError:
            llm_timeout = 90.0

        if api_key and base_url and model:
            self.llm = ChatOpenAI(
                base_url=base_url,
                model=model,
                api_key=api_key,
                timeout=llm_timeout,
                max_retries=2,
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
            timeout=llm_timeout,
            max_retries=2,
        )

    def select_tables(self, question: str, tables_dict: dict,
                       field_detail_tables: dict = None) -> tuple[list, dict]:
        """Step 1: choose relevant tables.

        field_detail_tables: dict mapping table_name -> list of field names whose
        descriptions should appear in the prompt.
        Format for matched tables: 表名 (字段描述1, 字段描述2, ...): 表描述
        Tables not in the dict are shown as: 表名: 表描述.
        """
        field_detail_map = field_detail_tables or {}

        def _field_desc(name, info):
            selected_fields = field_detail_map.get(name)
            if selected_fields is not None and info.get('fields'):
                descs = [
                    f['description'] for f in info['fields']
                    if f['name'] in selected_fields and f.get('description')
                ]
                if descs:
                    return f"- {name} ({', '.join(descs)}): {info['description']}"
            return f"- {name}: {info['description']}"

        table_summary = "\n".join([
            _field_desc(name, info)
            for name, info in tables_dict.items()
        ])

        system_msg = """你是一个SQL专家。根据用户的问题，从给定的数据库表列表中选择需要用到的表。
注意：可能需要多张表进行JOIN查询，请仔细分析字段依赖关系，选出所有相关的表。
只返回JSON格式，例如: {"tables": ["T_JCXX", "T_LK"]}
不要返回任何其他内容。"""
        human_msg = f"""数据库表列表（格式：表名 (字段描述): 表描述）：
{table_summary}

用户问题：{question}

请选择需要用到的所有表（可以是多张表，只返回JSON）："""

        messages = [
            SystemMessage(content=system_msg),
            HumanMessage(content=human_msg)
        ]

        response = self.llm.invoke(messages)
        result = json.loads(_extract_json(response.content))
        tables = result.get("tables", [])

        log = {
            "step": "table_selection",
            "request": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": human_msg},
            ],
            "response": response.content,
            "selected_tables": tables,
        }
        return tables, log

    def generate_sql(self, question: str, selected_tables: list, tables_dict: dict,
                     conversation_history: list = None, db_vendor: str = None,
                     table_relations: list = None) -> dict:
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

        relations_str = ""
        if table_relations:
            rel_lines = [
                f"  - {r['from_table']}.{r['from_column']} -> {r['to_table']}.{r['to_column']}"
                + (f" ({r['description']})" if r.get('description') else "")
                for r in table_relations
            ]
            if rel_lines:
                relations_str = "\n\n表关联关系（外键->主键）：\n" + "\n".join(rel_lines)

        history_str = ""
        if conversation_history:
            for msg in conversation_history[-6:]:
                role = "用户" if msg["role"] == "user" else "助手"
                history_str += f"{role}: {msg['content']}\n"

        vendor_hint = ""
        if db_vendor and db_vendor in DB_VENDOR_HINTS:
            vendor_hint = f"\n\n重要：{DB_VENDOR_HINTS[db_vendor]}"

        system_msg = f"""你是一个SQL专家，专门处理数据库查询。
根据用户问题和提供的表结构，生成准确的SQL查询语句。
所有表都通过F_BLH(病理号)关联。{vendor_hint}

如果用户的问题中包含了当前已知表结构中不存在的字段过滤条件（例如用户提到了某个属性，但已知表中没有对应字段），请不要强行生成包含不存在字段的SQL。请在sql字段中输出特殊标记：NEED_MORE_INFO: [缺失的实体或属性描述]

返回JSON格式：
{{
  "sql": "SELECT语句 或 NEED_MORE_INFO: [缺失描述]",
  "joins": ["JOIN条件描述1", "JOIN条件描述2"],
  "explanation": "查询逻辑说明"
}}
只返回JSON，不要其他内容。"""
        human_msg = f"""相关表结构：
{schema_str}{relations_str}

{("对话历史：" + chr(10) + history_str) if history_str else ""}

用户问题：{question}

请生成SQL查询（只返回JSON）："""

        messages = [
            SystemMessage(content=system_msg),
            HumanMessage(content=human_msg)
        ]

        response = self.llm.invoke(messages)
        result = json.loads(_extract_json(response.content))

        log = {
            "step": "sql_generation",
            "request": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": human_msg},
            ],
            "response": response.content,
        }

        return {
            "sql": result.get("sql", ""),
            "joins": result.get("joins", []),
            "explanation": result.get("explanation", ""),
            "tables_used": selected_tables,
            "log": log,
        }

    def _find_tables_for_missing_info(self, missing_info: str, tables_dict: dict,
                                      excluded_tables: list) -> list:
        """Find tables that might contain the missing information by keyword matching.

        Single-character tokens are excluded to reduce noise (especially relevant
        for Chinese text where meaningful terms are typically 2+ characters).
        Returns up to 2 top-scoring candidate tables to limit context growth per iteration.
        """
        keywords = [kw for kw in missing_info.lower().split() if len(kw) > 1]
        candidates = []
        for table_name, table_info in tables_dict.items():
            if table_name in excluded_tables:
                continue
            table_text = (
                table_info['description'] + " " +
                " ".join(f['name'] + " " + f['description'] for f in table_info['fields'])
            ).lower()
            score = sum(1 for kw in keywords if kw in table_text)
            if score > 0:
                candidates.append((score, table_name))
        candidates.sort(reverse=True)
        # Return at most 2 additional tables per iteration to avoid context bloat
        return [t for _, t in candidates[:2]]

    async def process_question(self, question: str, conversation_history: list = None,
                               tables_dict: dict = None, db_vendor: str = None,
                               fixed_tables: list = None,
                               table_relations: list = None,
                               field_detail_tables: list = None) -> dict:
        if tables_dict is None:
            tables_dict = TABLES

        selected_tables, selection_log = self.select_tables(
            question, tables_dict, field_detail_tables=field_detail_tables
        )
        if not selected_tables:
            first_table = next(iter(tables_dict), None)
            if first_table:
                selected_tables = [first_table]

        # Always include fixed context tables
        if fixed_tables:
            for t in fixed_tables:
                if t in tables_dict and t not in selected_tables:
                    selected_tables.append(t)

        all_logs = [selection_log]

        # Step 2: SQL generation with self-healing loop (max 3 iterations)
        result = None
        for attempt in range(3):
            relevant_relations = [
                r for r in (table_relations or [])
                if r['from_table'] in selected_tables or r['to_table'] in selected_tables
            ]

            result = self.generate_sql(
                question, selected_tables, tables_dict,
                conversation_history, db_vendor, relevant_relations
            )
            all_logs.append(result["log"])

            sql = result.get("sql", "")
            if sql.startswith("NEED_MORE_INFO:"):
                missing_info = sql[len("NEED_MORE_INFO:"):].strip()
                additional_tables = self._find_tables_for_missing_info(
                    missing_info, tables_dict, selected_tables
                )
                if additional_tables:
                    selected_tables = selected_tables + additional_tables
                    continue
            break

        return {
            "sql": result["sql"],
            "joins": result["joins"],
            "explanation": result["explanation"],
            "tables_used": selected_tables,
            "call_logs": all_logs,
        }
