import uvicorn

from fastapi import FastAPI
from user.interface.controllers.user_controller import router as user_router
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from containers import Container

app = FastAPI()
app.include_router(user_router)

container = Container()
container.wire(modules=[__name__])
app.container = container

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=400,
        content=exc.errors(),
    )

@app.get("/")
def hello():
    return {"Hello": "FastAPI"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)