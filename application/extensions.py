from flask_logconfig import LogConfig
import logging
import json
import traceback
from flask import g, ctx
import collections

# Create empty extension objects here
logger = LogConfig()


def register_extensions(app):
    """Adds any previously created extension objects into the app, and does any further setup they need."""
    # Logging
    logger.init_app(app)
    # Along with the default flask logger (app.logger) define a new one specifically for audit. To use this logger
    # just add app.audit_logger.info("an audit point").
    app.audit_logger = logging.getLogger("audit")

    # All done!
    app.logger.info("Extensions registered")


class ContextualFilter(logging.Filter):
    def filter(self, log_record):
        """Provide some extra variables to be placed into the log message."""

        # If we have an app context (because we're servicing an http request) then get the trace id we have
        # set in g (see app.py)
        if ctx.has_app_context():
            log_record.trace_id = g.trace_id
        else:
            log_record.trace_id = 'N/A'
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record):
        if record.exc_info:
            exc = traceback.format_exception(*record.exc_info)
        else:
            exc = None

        # Timestamp must be first (webops request)
        log_entry = collections.OrderedDict(
            [('timestamp', self.formatTime(record)),
             ('level', record.levelname),
             ('traceid', record.trace_id),
             ('message', record.msg % record.args),
             ('exception', exc)])

        return json.dumps(log_entry)


class JsonAuditFormatter(logging.Formatter):
    def format(self, record):
        # Timestamp must be first (webops request)
        log_entry = collections.OrderedDict(
            [('timestamp', self.formatTime(record)),
             ('level', 'AUDIT'),
             ('traceid', record.trace_id),
             ('message', record.msg % record.args)])

        return json.dumps(log_entry)
