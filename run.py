import uvicorn#用来运行Fastapi的引擎


if __name__ == "__main__":
    uvicorn.run("api.main:app",host="0.0.0.0",port=8000)