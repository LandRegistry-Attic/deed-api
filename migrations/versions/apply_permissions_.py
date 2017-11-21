# flake8: noqa
"""empty message

Revision ID:
Revises: 182d43ccd37c
Create Date: 2017-10-09 12:57:26.327406

"""

# revision identifiers, used by Alembic.
revision = 'apply_permissions'
down_revision = '22abc7aa0af'

from alembic import op, context
import os


def upgrade():

    context.execute("GRANT SELECT, UPDATE, INSERT, DELETE \
                    ON borrower, deed, mortgage_document, naa_audit, verify_match \
                    TO " + str(os.getenv('APP_SQL_USERNAME')))

    context.execute("GRANT USAGE, SELECT ON SEQUENCE borrower_id_seq, deed_id_seq, naa_audit_id_seq \
                    TO " + str(os.getenv('APP_SQL_USERNAME')))

def downgrade():
    context.execute("REVOKE SELECT, UPDATE, INSERT, DELETE \
                    ON borrower, deed, mortgage_document, naa_audit, verify_match \
                    FROM " + str(os.getenv('APP_SQL_USERNAME')))

    context.execute("REVOKE USAGE, SELECT ON SEQUENCE borrower_id_seq, deed_id_seq, naa_audit_id_seq \
                    FROM " + str(os.getenv('APP_SQL_USERNAME')))
