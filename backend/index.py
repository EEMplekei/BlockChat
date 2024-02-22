from fastapi import FastAPI

# Create an instance of the FastAPI class
app = FastAPI()

# Define a route using a decorator
@app.get("/")
async def read_root():
    return {"message": "Hello, World"}
