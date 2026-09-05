from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

import app.models # The import itself isn't directly used. Its purpose is to register the models with Base.metadata.
from app.core.config import get_settings
from app.db.session import Base


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


settings = get_settings() # means Alembic gets the PostgreSQL connection from our existing configuration.

config.set_main_option(
    "sqlalchemy.url",
    settings.database_url,
)

target_metadata = Base.metadata
# this line tells Alembic - "The database schema should be based on the SQLAlchemy models attached to this Base."

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""

    url = settings.database_url

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    configuration = config.get_section(
        config.config_ini_section,
        {},
    )

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()