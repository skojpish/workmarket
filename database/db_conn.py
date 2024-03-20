from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


from config import db_user, db_pass, db_host, db_port, db_name

DB_URL = f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

engine = create_async_engine(DB_URL)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
