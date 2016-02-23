from application import app
import os
import logging
from logger import logging_config

logging_config.setup_logging()
LOGGER = logging.getLogger(__name__)

LOGGER.info("Starting the server")

app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", "5005")))
