from typing import Any, Dict, Optional

from aiogram.fsm.state import State
from aiogram.fsm.storage.base import (
    BaseStorage,
    DefaultKeyBuilder,
    KeyBuilder,
    StateType,
    StorageKey,
)
from sqlalchemy import Column, DateTime, MetaData, String, Table, delete, select, text, update
from sqlalchemy.dialects.postgresql import JSONB, insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.sql import func

from database.session import engine as default_engine

_metadata = MetaData()

fsm_storage_table = Table(
    "fsm_storage",
    _metadata,
    Column("key", String(256), primary_key=True),
    Column("state", String(128), nullable=True),
    Column("data", JSONB, nullable=False, server_default=text("'{}'::jsonb")),
    Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
)


class PostgresStorage(BaseStorage):
    """FSM storage backed by PostgreSQL."""

    def __init__(
        self,
        engine: AsyncEngine = default_engine,
        key_builder: Optional[KeyBuilder] = None,
    ) -> None:
        if key_builder is None:
            key_builder = DefaultKeyBuilder(with_destiny=True)
        self.engine = engine
        self.key_builder = key_builder

    async def close(self) -> None:
        pass

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        storage_key = self.key_builder.build(key)
        state_value = state.state if isinstance(state, State) else state

        async with self.engine.begin() as conn:
            if state_value is None:
                result = await conn.execute(
                    select(fsm_storage_table.c.data).where(fsm_storage_table.c.key == storage_key)
                )
                row = result.first()
                if row is None:
                    return
                if not row.data:
                    await conn.execute(
                        delete(fsm_storage_table).where(fsm_storage_table.c.key == storage_key)
                    )
                else:
                    await conn.execute(
                        update(fsm_storage_table)
                        .where(fsm_storage_table.c.key == storage_key)
                        .values(state=None, updated_at=func.now())
                    )
                return

            stmt = (
                pg_insert(fsm_storage_table)
                .values(key=storage_key, state=state_value, data={})
                .on_conflict_do_update(
                    index_elements=[fsm_storage_table.c.key],
                    set_={"state": state_value, "updated_at": func.now()},
                )
            )
            await conn.execute(stmt)

    async def get_state(self, key: StorageKey) -> Optional[str]:
        storage_key = self.key_builder.build(key)
        async with self.engine.begin() as conn:
            result = await conn.execute(
                select(fsm_storage_table.c.state).where(fsm_storage_table.c.key == storage_key)
            )
            row = result.first()
            return row.state if row else None

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        storage_key = self.key_builder.build(key)
        async with self.engine.begin() as conn:
            if not data:
                result = await conn.execute(
                    select(fsm_storage_table.c.state).where(fsm_storage_table.c.key == storage_key)
                )
                row = result.first()
                if row is None:
                    return
                if row.state is None:
                    await conn.execute(
                        delete(fsm_storage_table).where(fsm_storage_table.c.key == storage_key)
                    )
                else:
                    await conn.execute(
                        update(fsm_storage_table)
                        .where(fsm_storage_table.c.key == storage_key)
                        .values(data={}, updated_at=func.now())
                    )
                return

            stmt = (
                pg_insert(fsm_storage_table)
                .values(key=storage_key, data=data)
                .on_conflict_do_update(
                    index_elements=[fsm_storage_table.c.key],
                    set_={"data": data, "updated_at": func.now()},
                )
            )
            await conn.execute(stmt)

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        storage_key = self.key_builder.build(key)
        async with self.engine.begin() as conn:
            result = await conn.execute(
                select(fsm_storage_table.c.data).where(fsm_storage_table.c.key == storage_key)
            )
            row = result.first()
            if row is None or row.data is None:
                return {}
            return dict(row.data)
