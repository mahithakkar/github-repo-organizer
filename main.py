from fastapi import FastAPI

app = FastAPI(title="GitHub Repository Organizer")


@app.get("/")
def read_root():
    return {
        "message": "Welcome to GitHub Repository Organizer API",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}