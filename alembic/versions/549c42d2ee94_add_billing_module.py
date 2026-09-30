"""add billing module

Revision ID: 549c42d2ee94
Revises: fb9ce2699be1
Create Date: 2026-09-30

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision identifiers
revision: str = "549c42d2ee94"
down_revision: Union[str, Sequence[str], None] = "fb9ce2699be1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add Billing module.

    The billings table may already exist because the application
    currently uses Base.metadata.create_all().
    """

    bind = op.get_bind()

    inspector = sa.inspect(bind)

    existing_tables = inspector.get_table_names()

    if "billings" not in existing_tables:

        op.create_table(
            "billings",

            sa.Column(
                "id",
                sa.Integer(),
                nullable=False
            ),

            sa.Column(
                "patient_id",
                sa.Integer(),
                nullable=False
            ),

            sa.Column(
                "doctor_id",
                sa.Integer(),
                nullable=False
            ),

            sa.Column(
                "appointment_id",
                sa.Integer(),
                nullable=True
            ),

            sa.Column(
                "consultation_fee",
                sa.Numeric(10, 2),
                nullable=False,
                server_default="0"
            ),

            sa.Column(
                "additional_charges",
                sa.Numeric(10, 2),
                nullable=False,
                server_default="0"
            ),

            sa.Column(
                "total_amount",
                sa.Numeric(10, 2),
                nullable=False,
                server_default="0"
            ),

            sa.Column(
                "payment_status",
                sa.String(length=20),
                nullable=False,
                server_default="pending"
            ),

            sa.Column(
                "payment_mode",
                sa.String(length=20),
                nullable=True
            ),

            sa.Column(
                "is_active",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true()
            ),

            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False
            ),

            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False
            ),

            sa.ForeignKeyConstraint(
                ["patient_id"],
                ["patients.id"]
            ),

            sa.ForeignKeyConstraint(
                ["doctor_id"],
                ["doctors.id"]
            ),

            sa.ForeignKeyConstraint(
                ["appointment_id"],
                ["appointments.id"]
            ),

            sa.PrimaryKeyConstraint("id"),

            sa.CheckConstraint(
                "consultation_fee >= 0",
                name="check_consultation_fee_non_negative"
            ),

            sa.CheckConstraint(
                "additional_charges >= 0",
                name="check_additional_charges_non_negative"
            ),

            sa.CheckConstraint(
                "total_amount >= 0",
                name="check_total_amount_non_negative"
            ),

            sa.CheckConstraint(
                "payment_status IN ('pending', 'paid', 'cancelled')",
                name="check_payment_status"
            ),

            sa.CheckConstraint(
                "payment_mode IN ('cash', 'card', 'upi') "
                "OR payment_mode IS NULL",
                name="check_payment_mode"
            ),
        )

        op.create_index(
            "ix_billings_id",
            "billings",
            ["id"],
            unique=False
        )

        op.create_index(
            "ix_billings_patient_id",
            "billings",
            ["patient_id"],
            unique=False
        )

        op.create_index(
            "ix_billings_doctor_id",
            "billings",
            ["doctor_id"],
            unique=False
        )

        op.create_index(
            "ix_billings_appointment_id",
            "billings",
            ["appointment_id"],
            unique=False
        )

        op.create_index(
            "ix_billings_payment_status",
            "billings",
            ["payment_status"],
            unique=False
        )

    # Database-level protection against duplicate billing
    # for the same appointment.
    #
    # SQLite allows multiple NULL values in a UNIQUE index,
    # so billings without an appointment are still allowed.

    existing_indexes = inspector.get_indexes("billings")

    unique_appointment_index_exists = any(
        index.get("unique") == 1
        and index.get("column_names") == ["appointment_id"]
        for index in existing_indexes
    )

    if not unique_appointment_index_exists:

        op.create_index(
            "uq_billing_appointment_id",
            "billings",
            ["appointment_id"],
            unique=True
        )


def downgrade() -> None:
    """
    Remove Billing module.
    """

    bind = op.get_bind()

    inspector = sa.inspect(bind)

    if "billings" not in inspector.get_table_names():
        return

    existing_indexes = inspector.get_indexes("billings")

    for index in existing_indexes:

        index_name = index.get("name")

        if index_name == "uq_billing_appointment_id":

            op.drop_index(
                index_name,
                table_name="billings"
            )

    # Drop the Billing table only during an explicit downgrade.
    op.drop_table("billings")