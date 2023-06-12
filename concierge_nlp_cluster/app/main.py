# concierge-app/concierge_nlp_cluster/app/main.py
import uvicorn
from concierge_nlp_cluster.app import app

if __name__ == "__main__":
    # Run the app using uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
