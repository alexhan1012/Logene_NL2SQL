import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .schemas import TABLES


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
    def __init__(self):
        api_key = os.getenv("ARK_API_KEY", "").strip()
        
        # 检查 API 密钥
        if not api_key or api_key == "your_api_key_here":
            raise ValueError(
                "❌ 缺少有效的 API 密钥配置\n\n"
                "请完成以下步骤：\n"
                "1. 访问火山引擎控制台 (https://console.volcengine.com/)\n"
                "2. 获取你的 API 密钥\n"
                "3. 编辑 backend/.env 文件\n"
                "4. 设置 ARK_API_KEY=你的实际_API_密钥\n"
                "5. 重启后端服务"
            )
        
        self.llm = ChatOpenAI(
            base_url=os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
            model=os.getenv("ARK_MODEL", "doubao-pro-32k-241215"),
            api_key=api_key,
        )

    def select_tables(self, question: str) -> list:
        table_summary = "\n".join([
            f"- {name}: {info['description']}"
            for name, info in TABLES.items()
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

    def generate_sql(self, question: str, selected_tables: list, conversation_history: list = None) -> dict:
        schema_details = []
        for table_name in selected_tables:
            if table_name in TABLES:
                table = TABLES[table_name]
                fields_str = "\n".join([
                    f"  - {f['name']} ({f['type']}): {f['description']}"
                    for f in table['fields']
                ])
                schema_details.append(f"表名: {table_name}\n描述: {table['description']}\n字段:\n{fields_str}")

        schema_str = "\n\n".join(schema_details)

        history_str = ""
        if conversation_history:
            for msg in conversation_history[-4:]:
                role = "用户" if msg["role"] == "user" else "助手"
                history_str += f"{role}: {msg['content']}\n"

        messages = [
            SystemMessage(content="""你是一个SQL专家，专门处理病理信息系统的数据库查询。
根据用户问题和提供的表结构，生成准确的SQL查询语句。
所有表都通过F_BLH(病理号)关联。

返回JSON格式：
{
  "sql": "SELECT语句",
  "joins": ["JOIN条件描述1", "JOIN条件描述2"],
  "explanation": "查询逻辑说明"
}
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

    async def process_question(self, question: str, conversation_history: list = None) -> dict:
        selected_tables = self.select_tables(question)
        if not selected_tables:
            selected_tables = ["T_JCXX"]

        result = self.generate_sql(question, selected_tables, conversation_history)
        return result
