import asyncio
import threading

from uvicorn import Config, Server

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from importlib import metadata
from importlib.metadata import PackageNotFoundError

if __name__ == "__main__":
    import VERSION
    import sendnotification
else:
    from src import VERSION
    from src import sendnotification


if __name__ == "__main__":
    staticFolder = "api/static"
    templatesFolder = "api/templates"
else:
    staticFolder = "src/api/static"
    templatesFolder = "src/api/templates"


app = FastAPI()
templates = Jinja2Templates(directory=templatesFolder)
app.mount("/static", StaticFiles(directory=staticFolder), name="static")

@app.api_route("/", methods=["GET"])
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.api_route("/api/v1/status", methods=["GET"])
def api_status():
    return JSONResponse({"version": VERSION.VERSION.version(),
                        "build": VERSION.VERSION.build(),
                        "release": VERSION.VERSION.release()})

@app.api_route("/api/v1/dependency/{module}", methods=["GET"])
def dependency(request: Request, module: str):
    try:
        return JSONResponse({"status": True, "version": metadata.version(module)})
    except PackageNotFoundError:
        return JSONResponse({"status": False, "error": "PackageNotFoundError"}, status_code=404)
    
@app.api_route("/api/v1/notification/send", methods=["POST"])
async def api_notification_send(request: Request):
    data = await request.json()
    if not data.get("level"):
        data["level"] = "INFO"
    try:
        sendnotification.sendnotification(message=data["message"], title=data["title"], level=data["level"])
        return JSONResponse({"status": True})
    except Exception as e:
        return JSONResponse({"status": False, "error": ""}, status_code=500)

""""
@app.api_route("/api/lib/{module}/{fucc}", methods=["GET"])
def dependency(request: Request, module: str, fucc: str):
    if module == "cache" or "Cache":
        return JSONResponse({"status": True, "CacheSize"})
"""

if VERSION.VERSION.release() == "DEV0":
    reload = True
else:
    reload = False

class api:
    def __init__(self, host: str = "127.0.0.1", port: int = 8000, fork: bool = True, reload: bool = False):
        self.config = Config(app=app, host=host, port=port, reload=reload, server_header=False, log_level="warning", access_log=False)
        self.server = Server(config=self.config)
        self.thread = None
        self.fork = fork


    def _run_async(self):
        try:
            asyncio.run(self.server.serve())
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[API] Exception: {e}")

    def _run(self):
        try:
            self.server.run()
        except asyncio.exceptions.CancelledError:
            print("[API] CancelledError capturé")
        except BaseException as e:
            print(f"[API] Exception (BaseException): {e}")

    
    def run(self):
        funcc = self._run
        if self.fork:
            self.thread = threading.Thread(target=funcc, name="API_Winion")
            self.thread.start()
        else:
            funcc()
    
    def stop(self):
        self.server.should_exit = True
        if self.thread:
            self.thread.join(timeout=4)

if __name__ == "__main__":
    import time
    session = api(reload=True)
    session.run()
    time.sleep(10)
    session.stop()