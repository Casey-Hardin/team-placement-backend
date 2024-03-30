# third-party imports
import uvicorn


PRODUCTION = False


def start():
    """ Launch at root level with 'poetry run start'. """
    uvicorn.run(
        "team_placement.api:app",
        host="127.0.0.1",
        port=8000,
        reload=not PRODUCTION,
    )


if __name__ == "__main__":
    start()