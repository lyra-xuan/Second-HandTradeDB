from sqlalchemy.ext.asyncio import AsyncSession
from models import AsyncSessionFactory


async def get_session() -> AsyncSession:
    """整个请求共用一个事务：请求成功结束时提交，出错时回滚。

    事务边界放在这里，Repository 中不再自行开启事务，
    这样「下单」这类跨表操作可以在同一个事务内完成。
    """
    async with AsyncSessionFactory() as session:
        async with session.begin():
            yield session
