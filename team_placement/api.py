# third-party imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# create a Fast API application
app = FastAPI()


# add middleware to communicate with ReactJS
origins = [
    "http://localhost:5173",
    "localhost:5173",
    ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def homepage() -> None:
    """ Homepage. """
    return {"message": "Hello World"}
