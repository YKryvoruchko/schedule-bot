"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-12
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(255)),
        sa.Column("first_name", sa.String(255)),
        sa.Column("last_name", sa.String(255)),
        sa.Column("notifications_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notification_minutes_before", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)
    op.create_table(
        "student_groups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_student_groups_name", "student_groups", ["name"], unique=True)
    op.create_table(
        "schedule_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_schedule_versions_is_active", "schedule_versions", ["is_active"])
    op.create_table(
        "schedule_imports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True)),
        sa.Column("row_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("valid_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("invalid_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("warnings", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("errors", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("preview", sa.Text(), nullable=False, server_default="[]"),
    )
    op.create_index("ix_schedule_imports_status", "schedule_imports", ["status"])
    op.create_table(
        "schedule",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("version_id", sa.Integer(), sa.ForeignKey("schedule_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("group_id", sa.Integer(), sa.ForeignKey("student_groups.id"), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("lesson_number", sa.Integer(), nullable=False),
        sa.Column("starts_at", sa.Time(), nullable=False),
        sa.Column("ends_at", sa.Time(), nullable=False),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("teacher", sa.String(500)),
        sa.Column("meeting_url", sa.Text()),
        sa.Column("room", sa.String(255)),
        sa.Column("description", sa.Text()),
        sa.Column("lesson_type", sa.String(64)),
        sa.Column("week_start", sa.Integer()),
        sa.Column("week_end", sa.Integer()),
        sa.Column("week_parity", sa.String(16), nullable=False, server_default="any"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_schedule_day_of_week", "schedule", ["day_of_week"])
    op.create_index("ix_schedule_group_id", "schedule", ["group_id"])
    op.create_index("ix_schedule_version_id", "schedule", ["version_id"])
    op.create_table(
        "notification_deliveries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("schedule_id", sa.Integer(), sa.ForeignKey("schedule.id", ondelete="CASCADE"), nullable=False),
        sa.Column("minutes_before", sa.Integer(), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "schedule_id", "minutes_before", name="uq_notification_once"),
    )
    op.create_index("ix_notification_deliveries_schedule_id", "notification_deliveries", ["schedule_id"])
    op.create_index("ix_notification_deliveries_user_id", "notification_deliveries", ["user_id"])


def downgrade() -> None:
    op.drop_table("notification_deliveries")
    op.drop_table("schedule")
    op.drop_table("schedule_imports")
    op.drop_table("schedule_versions")
    op.drop_table("student_groups")
    op.drop_table("users")
