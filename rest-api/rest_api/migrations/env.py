import asyncio
from logging.config import fileConfig
from typing import Any, Iterable

import models.ai  # noqa: F401
import models.business.hr  # noqa: F401
import models.business.logistic  # noqa: F401
import models.business.trade  # noqa: F401
import models.core  # noqa: F401
from alembic import context
from alembic.operations.ops import CreateForeignKeyOp, CreateTableOp, MigrateOperation
from config.settings import Settings
from database.engine import Engine
from sqlalchemy import Column, ForeignKeyConstraint, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

config = context.config


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


settings = Settings()  # type: ignore
db = Engine(settings)
target_metadata = db.get_base().metadata


def foreign_key_split_hook(directives: list[Any]) -> None:
    script = directives[0]
    upgrade_ops = script.upgrade_ops

    new_operations: list[MigrateOperation] = []
    foreign_key_operations: list[CreateForeignKeyOp] = []
    seen_constraints: set[tuple[str, str, tuple[str, ...], str, tuple[str, ...]]] = set()

    for operation in upgrade_ops.ops:
        if not isinstance(operation, CreateTableOp):
            new_operations.append(operation)
            continue

        table_fks, cleaned_columns = extract_foreign_keys(operation, seen_constraints)
        composite_fks = extract_composite_constraints(operation, seen_constraints)

        operation.columns = cleaned_columns
        new_operations.append(operation)
        foreign_key_operations.extend(table_fks + composite_fks)

    upgrade_ops.ops = new_operations + foreign_key_operations


def normalize_constraint_name(constraint_name: Any) -> str | None:
    if constraint_name is None:
        return None
    name_str = str(constraint_name)
    return name_str if name_str and name_str.lower() != "none" else None


def build_constraint_fingerprint(
    constraint_name: Any,
    source_table: str,
    local_columns: Iterable[str],
    target_table: str,
    target_columns: Iterable[str],
) -> tuple[str, str, tuple[str, ...], str, tuple[str, ...]]:
    normalized_name = normalize_constraint_name(constraint_name)
    if normalized_name is None:
        normalized_name = f"{source_table}__{target_table}__{'__'.join(local_columns)}__{'__'.join(target_columns)}"
    return (
        normalized_name,
        source_table,
        tuple(local_columns),
        target_table,
        tuple(target_columns),
    )


def extract_foreign_keys(
    create_table_op: CreateTableOp,
    seen_constraints: set[tuple[str, str, tuple[str, ...], str, tuple[str, ...]]],
) -> tuple[list[CreateForeignKeyOp], list[Any]]:
    foreign_key_ops: list[CreateForeignKeyOp] = []
    cleaned_columns: list[Any] = []

    for element in create_table_op.columns:
        if isinstance(element, Column):
            column = element
            if getattr(column, "foreign_keys", None):
                for foreign_key in list(column.foreign_keys):
                    constraint_name = getattr(foreign_key.constraint, "name", None)
                    fingerprint = build_constraint_fingerprint(
                        constraint_name,
                        create_table_op.table_name,
                        [column.name],
                        foreign_key.column.table.name,
                        [foreign_key.column.name],
                    )
                    if fingerprint in seen_constraints:
                        column.foreign_keys.remove(foreign_key)
                        continue

                    seen_constraints.add(fingerprint)
                    foreign_key_ops.append(
                        CreateForeignKeyOp(
                            constraint_name=normalize_constraint_name(constraint_name)
                            or f"fk_{create_table_op.table_name}_{column.name}_{foreign_key.column.table.name}",
                            source_table=create_table_op.table_name,
                            referent_table=foreign_key.column.table.name,
                            local_cols=[column.name],
                            remote_cols=[foreign_key.column.name],
                        )
                    )
                    column.foreign_keys.remove(foreign_key)

            cleaned_columns.append(column)

        elif isinstance(element, ForeignKeyConstraint):
            constraint_name = element.name
            local_columns = list(element.columns.keys())
            target_columns = [col_ref.column.name for col_ref in element.elements]
            fingerprint = build_constraint_fingerprint(
                constraint_name,
                create_table_op.table_name,
                local_columns,
                element.referred_table.name,
                target_columns,
            )
            if fingerprint in seen_constraints:
                continue

            seen_constraints.add(fingerprint)
            foreign_key_ops.append(
                CreateForeignKeyOp(
                    constraint_name=normalize_constraint_name(constraint_name)
                    or f"fk_{create_table_op.table_name}_composite_inline",
                    source_table=create_table_op.table_name,
                    referent_table=element.referred_table.name,
                    local_cols=local_columns,
                    remote_cols=target_columns,
                )
            )

        else:
            cleaned_columns.append(element)

    return foreign_key_ops, cleaned_columns


def extract_composite_constraints(
    create_table_op: CreateTableOp,
    seen_constraints: set[tuple[str, str, tuple[str, ...], str, tuple[str, ...]]],
) -> list[CreateForeignKeyOp]:
    foreign_key_ops: list[CreateForeignKeyOp] = []
    table_constraints = create_table_op.kw.get("constraints", [])

    for constraint in list(table_constraints):
        if isinstance(constraint, ForeignKeyConstraint):
            constraint_name = constraint.name
            local_columns = list(constraint.columns.keys())
            target_columns = [col_ref.column.name for col_ref in constraint.elements]

            fingerprint = build_constraint_fingerprint(
                constraint_name,
                create_table_op.table_name,
                local_columns,
                constraint.referred_table.name,
                target_columns,
            )

            if fingerprint in seen_constraints:
                table_constraints.remove(constraint)
                continue

            seen_constraints.add(fingerprint)
            table_constraints.remove(constraint)
            foreign_key_ops.append(
                CreateForeignKeyOp(
                    constraint_name=normalize_constraint_name(constraint_name)
                    or f"fk_{create_table_op.table_name}_composite",
                    source_table=create_table_op.table_name,
                    referent_table=constraint.referred_table.name,
                    local_cols=local_columns,
                    remote_cols=target_columns,
                )
            )

    return foreign_key_ops


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    if url:
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
            process_revision_directives=lambda ctx, rev, directives: foreign_key_split_hook(directives),
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
        process_revision_directives=lambda ctx, rev, directives: foreign_key_split_hook(directives),
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
