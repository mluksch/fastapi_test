# FastApi has some advantages:
# (1) asynchronous/non-blocking i.e. not every request handlers needs to run in its own thread
# and blocks any other executions within the same thread.
# Flask on the other hand is based on WSGI (which is synchronous by default, there is
# also an asynchronous version of WSGI: ASGI)
# (2) built-in data validation
# (3) websocket-support
# (4) automatic documentation of API endpoints

import fastapi
import fastapi.encoders as encoders

# Start app by: "pipenv run uvicorn main:app --reload"
# "--reload" for hot-reload on code changes
# Endpoint exposed at: http://localhost:8000
# Docs exposed at: http://localhost:8000/docs
app = fastapi.FastAPI()


# Example: http://localhost:8000
# Returns: {"gruss":"hallo","id":1,"name":"Max"}
@app.get("/")
def index():
    # explicitly encode objects to json-response with FastAPI:
    return encoders.jsonable_encoder({
        "gruss": "hallo",
        "id": 1,
        "name": "Max"
    })


# Example: http://localhost:8000/items?limit=10&even=True
# Returns: [{"magic_number":0},{"magic_number":2},{"magic_number":4},{"magic_number":6},{"magic_number":8}]
@app.get("/items")
def index(even: bool = False, limit: int = 100):
    # explicitly encode objects to json-response with FastAPI:
    return encoders.jsonable_encoder([{
        "magic_number": i
    } for i in range(0, limit) if not even or i % 2 == 0])
