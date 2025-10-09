from app import create_app
from app.services import AskarStorage
from asyncio import run as _await
from app.operations import setup_demo

askar = AskarStorage()

app = create_app()

if __name__ == "__main__":
    _await(askar.provision(recreate=True))
    if not (demo := _await(askar.fetch("demo", "demo"))):
        _await(askar.store("demo", "demo", setup_demo()))
    app.run(host="0.0.0.0", port="5000", debug=True)
