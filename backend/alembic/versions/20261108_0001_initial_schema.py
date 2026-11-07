"""initial RCA relational schema

Revision ID: 20261108_0001
Revises:
Create Date: 2026-11-08
"""
from alembic import op
import sqlalchemy as sa

revision = "20261108_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    json_type = sa.JSON()
    op.create_table("users",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("email", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(120), nullable=False), sa.Column("role", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_table("investigations",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("investigation_number", sa.String(64), nullable=False),
        sa.Column("title", sa.String(300), nullable=False), sa.Column("product_name", sa.String(255)), sa.Column("batch_number", sa.String(128)),
        sa.Column("department", sa.String(128)), sa.Column("incident_description", sa.Text()), sa.Column("method", sa.String(32)),
        sa.Column("status", sa.String(32), nullable=False), sa.Column("created_by_id", sa.String(36), sa.ForeignKey("users.id")),
        sa.Column("reviewed_by_id", sa.String(36), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("investigation_number"),
    )
    op.create_index("ix_investigations_investigation_number", "investigations", ["investigation_number"])
    op.create_index("ix_investigations_status", "investigations", ["status"])
    op.create_index("ix_investigation_status_updated", "investigations", ["status", "updated_at"])
    op.create_table("incident_details", sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("investigation_id", sa.String(36), sa.ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_type", sa.String(32), nullable=False), sa.Column("source_text", sa.Text()), sa.Column("extracted_data", json_type, nullable=False),
        sa.UniqueConstraint("investigation_id"))
    for name in ["investigation_methods", "root_causes", "evidence_items", "capa_actions", "investigation_reviews"]:
        pass
    op.create_table("investigation_methods", sa.Column("id", sa.String(36), primary_key=True), sa.Column("investigation_id", sa.String(36), sa.ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False), sa.Column("method", sa.String(32), nullable=False), sa.Column("result", json_type, nullable=False))
    op.create_table("root_causes", sa.Column("id", sa.String(36), primary_key=True), sa.Column("investigation_id", sa.String(36), sa.ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("category", sa.String(64)), sa.Column("status", sa.String(40), nullable=False), sa.Column("evidence_strength", sa.String(40), nullable=False), sa.Column("payload", json_type, nullable=False))
    op.create_table("evidence_items", sa.Column("id", sa.String(36), primary_key=True), sa.Column("investigation_id", sa.String(36), sa.ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False), sa.Column("evidence_required", sa.Text(), nullable=False), sa.Column("priority", sa.String(24), nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("payload", json_type, nullable=False))
    op.create_table("capa_actions", sa.Column("id", sa.String(36), primary_key=True), sa.Column("investigation_id", sa.String(36), sa.ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False), sa.Column("capa_code", sa.String(64), nullable=False), sa.Column("action_type", sa.String(32), nullable=False), sa.Column("recommended_action", sa.Text(), nullable=False), sa.Column("department", sa.String(128)), sa.Column("target_date", sa.Date()), sa.Column("status", sa.String(32), nullable=False), sa.Column("payload", json_type, nullable=False))
    op.create_table("investigation_reviews", sa.Column("id", sa.String(36), primary_key=True), sa.Column("investigation_id", sa.String(36), sa.ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False), sa.Column("reviewer_id", sa.String(36), sa.ForeignKey("users.id")), sa.Column("decision", sa.String(40), nullable=False), sa.Column("comments", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    for table in ["investigation_methods", "root_causes", "evidence_items", "capa_actions", "investigation_reviews"]:
        op.create_index(f"ix_{table}_investigation_id", table, ["investigation_id"])


def downgrade():
    for table in ["investigation_reviews", "capa_actions", "evidence_items", "root_causes", "investigation_methods", "incident_details", "investigations", "users"]:
        op.drop_table(table)
