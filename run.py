from application import app
import os


if not os.path.exists("logs"):
    os.makedirs("logs")

app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", "5005")))
