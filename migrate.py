#!/usr/bin/env python
"""数据库迁移命令封装。

Usage:
    python migrate.py new "description"  # 生成迁移脚本
    python migrate.py up                 # 升级到最新
    python migrate.py down               # 回滚一个版本
    python migrate.py history            # 查看迁移历史
    python migrate.py current            # 查看当前版本
    python migrate.py reset              # 清空所有表和迁移记录，重新生成迁移
"""

import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def reset() -> None:
    """清空数据库所有表、删除迁移文件、重新生成迁移。"""
    print("⚠️  此操作将删除所有表和迁移记录！")
    confirm = input("确认执行? (yes/no): ")
    if confirm.lower() != "yes":
        print("已取消")
        return

    # 1. 删除所有迁移文件
    versions_dir = Path(__file__).parent / "alembic" / "versions"
    for f in versions_dir.glob("*.py"):
        if f.name != "__init__.py":
            f.unlink()
            print(f"删除迁移文件: {f.name}")

    # 2. 删除数据库所有表
    print("正在清空数据库...")
    import asyncio
    asyncio.run(_drop_all_tables())

    print("✅ 重置完成，请执行 python migrate.py new \"init\" 重新生成迁移")


async def _drop_all_tables() -> None:
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    from app.core.config import settings

    engine = create_async_engine(settings.database.url)
    async with engine.begin() as conn:
        await conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        result = await conn.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result.fetchall()]
        for table in tables:
            await conn.execute(text(f"DROP TABLE IF EXISTS `{table}`"))
            print(f"  删除表: {table}")
        await conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    await engine.dispose()


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]

    match cmd:
        case "new":
            if len(sys.argv) < 3:
                print("Usage: python migrate.py new \"description\"")
                sys.exit(1)
            run(["alembic", "revision", "--autogenerate", "-m", sys.argv[2]])
        case "up":
            target = sys.argv[2] if len(sys.argv) > 2 else "head"
            run(["alembic", "upgrade", target])
        case "down":
            target = sys.argv[2] if len(sys.argv) > 2 else "-1"
            run(["alembic", "downgrade", target])
        case "history":
            run(["alembic", "history", "--verbose"])
        case "current":
            run(["alembic", "current"])
        case "reset":
            reset()
        case _:
            print(f"Unknown command: {cmd}")
            print(__doc__)
            sys.exit(1)


if __name__ == "__main__":
    main()
