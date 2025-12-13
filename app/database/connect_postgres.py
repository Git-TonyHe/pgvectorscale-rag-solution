"""
connect_postgres.py

简单的脚本用于连接到 Docker 中运行的 Postgres（或 Timescale/Postgres）数据库并执行一个简单查询以验证连接。
它会优先读取环境变量：DATABASE_URL 或 TIMESCALE_SERVICE_URL，若都不存在则使用默认连接字符串。

要求：在项目的 `requirements.txt` 中已经包含 `psycopg` 和 `python-dotenv`。
"""
from __future__ import annotations

import os
import sys
from typing import Optional

from dotenv import load_dotenv
import psycopg

# 先尝试加载仓库中的 app/example.env（优先级最高），然后再回退加载默认位置的 .env
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
example_env_path = os.path.join(base_dir, "example.env")
if os.path.exists(example_env_path):
    load_dotenv(example_env_path)
# 仍然调用一次通用的 load_dotenv()，以便从项目根或当前工作目录加载其他 .env 文件（不会覆盖已设置的变量）
load_dotenv()

DEFAULT_DSN = os.getenv(
    "TIMESCALE_SERVICE_URL",
    os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/postgres"),
)


def get_connection(dsn: Optional[str] = None) -> psycopg.Connection:
    """返回一个已连接的 psycopg.Connection 对象。

    参数:
        dsn: 可选的数据库连接字符串，如果为 None 则使用环境变量或默认值。
    抛出:
        psycopg.errors.DatabaseError 等连接相关异常。
    """
    if dsn is None:
        dsn = DEFAULT_DSN

    try:
        conn = psycopg.connect(dsn)
        return conn
    except Exception:
        raise


def test_connection(dsn: Optional[str] = None) -> None:
    """测试连接并打印数据库版本和简单查询结果。"""
    conn = None
    try:
        conn = get_connection(dsn)
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()
            print("Database version:", version[0] if version else None)

            cur.execute("SELECT 1;")
            one = cur.fetchone()
            print("Simple query result:", one[0] if one else None)
    except Exception as e:
        print("连接或查询失败:", e, file=sys.stderr)
        raise
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    # 可通过命令行第一个参数传入 DSN，例如: python connect_postgres.py "postgresql://..."
    dsn_arg = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        test_connection(dsn_arg)
    except Exception:
        sys.exit(1)
