"""initial schema

Revision ID: 20260302_0001
Revises: 
Create Date: 2026-03-02 15:20:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260302_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_role = sa.Enum("ADMIN", "USER", name="user_role")
    category_type = sa.Enum("INCOME", "EXPENSE", name="category_type")
    user_role.create(op.get_bind(), checkfirst=True)
    category_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("jti", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"], unique=False)
    op.create_index("ix_refresh_tokens_jti", "refresh_tokens", ["jti"], unique=True)

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("type", category_type, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "name", name="uq_categories_user_name"),
    )
    op.create_index("ix_categories_user_id", "categories", ["user_id"], unique=False)

    op.create_table(
        "expenses",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("spent_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_expenses_user_id", "expenses", ["user_id"], unique=False)
    op.create_index("ix_expenses_category_id", "expenses", ["category_id"], unique=False)
    op.create_index("ix_expenses_spent_at", "expenses", ["spent_at"], unique=False)
    op.create_index("idx_expenses_user_spent_at", "expenses", ["user_id", "spent_at"], unique=False)
    op.create_index(
        "idx_expenses_user_category_spent_at",
        "expenses",
        ["user_id", "category_id", "spent_at"],
        unique=False,
    )

    op.create_table(
        "budgets",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id", ondelete="CASCADE"), nullable=False),
        sa.Column("month", sa.String(length=7), nullable=False),
        sa.Column("limit_amount", sa.Numeric(12, 2), nullable=False),
        sa.UniqueConstraint("user_id", "category_id", "month", name="uq_budget_user_category_month"),
    )
    op.create_index("ix_budgets_user_id", "budgets", ["user_id"], unique=False)
    op.create_index("ix_budgets_category_id", "budgets", ["category_id"], unique=False)
    op.create_index("ix_budgets_month", "budgets", ["month"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_budgets_month", table_name="budgets")
    op.drop_index("ix_budgets_category_id", table_name="budgets")
    op.drop_index("ix_budgets_user_id", table_name="budgets")
    op.drop_table("budgets")

    op.drop_index("idx_expenses_user_category_spent_at", table_name="expenses")
    op.drop_index("idx_expenses_user_spent_at", table_name="expenses")
    op.drop_index("ix_expenses_spent_at", table_name="expenses")
    op.drop_index("ix_expenses_category_id", table_name="expenses")
    op.drop_index("ix_expenses_user_id", table_name="expenses")
    op.drop_table("expenses")

    op.drop_index("ix_categories_user_id", table_name="categories")
    op.drop_table("categories")

    op.drop_index("ix_refresh_tokens_jti", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_user_id", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    sa.Enum(name="category_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="user_role").drop(op.get_bind(), checkfirst=True)
