import asyncio
from logging.config import fileConfig
from typing import cast, Any

from alembic import context
from alembic.operations.ops import CreateTableOp, CreateForeignKeyOp, MigrateOperation
from sqlalchemy import pool, Column, ForeignKeyConstraint
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

import entities.core
from config import Database, Settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

settings = Settings()  # type: ignore
db = Database(settings)
target_metadata = db.get_base().metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def foreign_key_split_hook(directives: list[Any]) -> None:
    script = directives[0]
    upgrade_ops = script.upgrade_ops

    new_ops: list[MigrateOperation] = []
    fk_ops: list[CreateForeignKeyOp] = []

    for op in upgrade_ops.ops:
        if not isinstance(op, CreateTableOp):
            new_ops.append(op)
            continue

        table_fks, new_cols = extract_foreign_keys(op)
        composite_fks = extract_composite_constraints(op)

        op.columns = new_cols
        new_ops.append(op)
        fk_ops.extend(table_fks + composite_fks)

    upgrade_ops.ops = new_ops + fk_ops


def extract_foreign_keys(
    op: CreateTableOp,
) -> tuple[list[CreateForeignKeyOp], list[Column]]:
    fks: list[CreateForeignKeyOp] = []
    new_cols: list[Column] = []

    for col in op.columns:
        if not isinstance(col, Column):
            continue
        for fk in list(col.foreign_keys):
            fks.append(
                CreateForeignKeyOp(
                    constraint_name=f"fk_{op.table_name}_{col.name}_{fk.column.table.name}",
                    source_table=op.table_name,
                    referent_table=fk.column.table.name,
                    local_cols=[col.name],
                    remote_cols=[fk.column.name],
                )
            )
            col.foreign_keys.remove(fk)
        new_cols.append(col)

    return fks, new_cols


def extract_composite_constraints(op: CreateTableOp) -> list[CreateForeignKeyOp]:
    fks: list[CreateForeignKeyOp] = []
    constraints = op.kw.get("constraints", [])

    for constraint in list(constraints):
        if isinstance(constraint, ForeignKeyConstraint):
            constraints.remove(constraint)
            fks.append(
                CreateForeignKeyOp(
                    constraint_name=constraint.name or f"fk_{op.table_name}_composite",
                    source_table=op.table_name,
                    referent_table=constraint.referred_table.name,
                    local_cols=constraint.columns.keys(),
                    remote_cols=[e.column.name for e in constraint.elements],
                )
            )

    return fks


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    if url:
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
            process_revision_directives=lambda ctx, rev, directives: foreign_key_split_hook(
                directives
            ),
        )

        with context.begin_transaction():
            context.run_migrations()


async def run_migrations_online() -> None:
    url = config.get_main_option("sqlalchemy.url")
    if url:
        connectable = create_async_engine(
            url,
            poolclass=pool.NullPool,
        )
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
        await connectable.dispose()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        process_revision_directives=lambda ctx, rev, directives: foreign_key_split_hook(
            directives
        ),
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
