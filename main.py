from app import create_app
from app.services import AskarStorage, AgentController
import asyncio

# asyncio.run(AskarStorage().provision(recreate=False))
# asyncio.run(AgentController().provision())

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=True)
