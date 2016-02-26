from application import app
import os


app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", "5005")))
