import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from urllib.parse import parse_qs, urlparse
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
import re
import aiohttp
from hashlib import sha256
import sys
import time
import asyncio
from contextlib import asynccontextmanager
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory=".")
from config import config


task_queue_local = asyncio.Queue(config["max_queue"])
task_queue_ot = asyncio.Queue(config["max_queue_ot"])

for dirname in ["paipus", "outputs", "locks"]:
    if not os.path.exists(dirname):
        os.mkdir(dirname)
paipupath = os.path.abspath("paipus")
outputpath = os.path.abspath("outputs")
lockpath = os.path.abspath("locks")


async def task_worker():
    while True:
        task = await task_queue_local.get()
        try:
            print("Task started", task[4])
            await run_task(*task)
        finally:
            task_queue_local.task_done()


async def task_worker_ot():
    while True:
        task = await task_queue_ot.get()
        try:
            print("Task started", task[4])
            await run_task(*task)
        finally:
            task_queue_ot.task_done()


async def cleanup_files():
    while True:
        now = time.time()
        for directory in [paipupath, outputpath]:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    file_age = now - os.path.getmtime(file_path)
                    if file_age > int(config["file_expire"]):
                        os.remove(file_path)
        await asyncio.sleep(int(config["clean_interval"]))


async def download_log(id: str, platform: str):
    if platform == "custom":
        return json.loads(id)
    async with aiohttp.ClientSession() as session:
        if platform == "tenhou":
            url = f"https://tenhou.net/5/mjlog2json.cgi?{id}"
            headers = {"Referer": "https://tenhou.net/", "User-Agent": "Mozilla/5.0"}
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    return JSONResponse(
                        {"error": f"Failed to fetch {platform} paipu"}, status_code=503
                    )
                return await response.json(content_type="text/plain")
        elif platform == "majsoul":
            url = f"{config['tensoul']}{id}"
            auth = aiohttp.BasicAuth(config["tensoul_usr"], config["tensoul_pwd"])
            async with session.get(url, auth=auth) as response:
                if response.status != 200:
                    res = await response.json()
                    if errmsg := res.get("error"):
                        if type(errmsg) is str:
                            return JSONResponse(
                                {
                                    "error": f"Failed to fetch {platform} paipu: {errmsg}"
                                },
                                status_code=500,
                            )
                        elif errmsg := errmsg.get("code"):
                            if errmsg == 1203:
                                return JSONResponse(
                                    {
                                        "error": f"Failed to fetch {platform} paipu: ERR_GAME_NOT_EXIST"
                                    },
                                    status_code=400,
                                )
                            return JSONResponse(
                                {
                                    "error": f"Failed to fetch {platform} paipu: code {errmsg}"
                                },
                                status_code=500,
                            )
                    return JSONResponse(
                        {"error": f"Failed to fetch {platform} paipu"}, status_code=503
                    )
                return await response.json()
        elif platform == "riichicity":
            data = {"log_id": id}
            async with session.post(config["citylogs"], json=data) as response:
                if response.status != 200:
                    res = await response.json()
                    if errmsg := res.get("errors"):
                        errmsg = errmsg.get("log_id", errmsg)
                        return JSONResponse(
                            {"error": f"Failed to fetch {platform} paipu: {errmsg}"},
                            status_code=503,
                        )
                    return JSONResponse(
                        {"error": f"Failed to fetch {platform} paipu"}, status_code=503
                    )
                return await response.json()


async def run_task(
    nplayer: int,
    engine: int,
    target: int,
    paipu: str,
    taskid: str,
    language: str,
    isjson: bool = False,
):
    args = [
        config["reviewer3p"] if nplayer == 3 else config["reviewer4p"],
        "-e",
        "mortal",
        "--mortal-exe",
        (
            (config["local3p"] if engine == 1 else config["akagiot3p"])
            if nplayer == 3
            else (config["local4p"] if engine == 1 else config["akagiot4p"])
        ),
        "--mortal-cfg",
        (
            (config["local3p_conf"] if engine == 1 else config["akagiot3p_conf"])
            if nplayer == 3
            else (config["local4p_conf"] if engine == 1 else config["akagiot4p_conf"])
        ),
        "--show-rating",
        "--lang",
        language,
        "-a",
        str(target),
        "-i",
        os.path.join(paipupath, paipu),
        "-o",
        os.path.join(outputpath, taskid) + (".html" if not isjson else ".json"),
        "--no-open",
    ]
    if isjson:
        args.append("--json")

    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=sys.stdout,  # asyncio.subprocess.PIPE,
        stderr=sys.stderr,  # asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        print(f"Task failed: {taskid}")
        os.remove(os.path.join(paipupath, paipu))
    os.remove(os.path.join(lockpath, taskid))


def get_url(fn: str, ui: int, nplayer: int):
    if ui == 1:
        return app.url_path_for("results", path=fn)
    else:
        if nplayer == 3:
            return f"/ui/3p.html?data=/results/{fn}"
        else:
            return f"/ui/?data=/results/{fn}"


def parse_custom_json(paipudata):
    pass


def parse_player_num(paipudata):
    if any(x in paipudata["rule"]["disp"] for x in ["三", "3"]):
        return 3
    return 4


def parse_game_length(paipudata):
    if any(x in paipudata["rule"]["disp"] for x in ["東", "East"]):
        return 1
    return 0


async def validate_turnstile(response: str):
    if not config.get("turnstile_secret") or not config.get("turnstile_sitekey"):
        return True
    if not response:
        return False
    url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    data = {
        "secret": config["turnstile_secret"],
        "response": response,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            if response.status != 200:
                return False
            result = await response.json()
            return result.get("success", False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    for _ in range(int(config["max_task"])):
        asyncio.create_task(task_worker())
    for _ in range(int(config["max_task_ot"])):
        asyncio.create_task(task_worker_ot())
    if int(config["file_expire"]) > 0 and int(config["clean_interval"]) > 0:
        asyncio.create_task(cleanup_files())
    yield


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)


@app.post("/review")
async def review(request: Request):
    form = await request.form()
    captcha = form.get("cf-turnstile-response")
    validation_task = asyncio.create_task(validate_turnstile(captcha))
    paipu_raw = form.get("id")
    target_override = int(form.get("actor", -1))
    engine = int(form.get("engine", 0))
    ui = int(form.get("ui", 0))
    language = form.get("lang")
    target = 0
    if not paipu_raw:
        raise HTTPException(status_code=400, detail="id is required")
    if len(paipu_raw) > 10240:
        raise HTTPException(status_code=413, detail="sorry, your paipu is too large")
    if target_override not in range(-1, 4):
        raise HTTPException(status_code=400, detail="actor is invalid")
    if not engine:
        raise HTTPException(status_code=400, detail="engine is required")
    if engine not in [1, 2]:
        raise HTTPException(status_code=400, detail="engine is not supported")
    if language not in ["ja", "en", "zh", "ko"]:
        raise HTTPException(status_code=400, detail="language is not supported")
    if ui not in [1, 2]:
        raise HTTPException(status_code=400, detail="ui is not supported")
    if ui == 2:
        language = "en"  # there is no difference in language for new ui

    pat_tenhou = re.compile(r"\d{10}gm-\w{4}-\w{4}-\w{8}")
    pat_majsoul = re.compile(r"\w{6}-\w{8}-\w{4}-\w{4}-\w{4}-\w{12}(.*)")
    pat_rcity = re.compile(r"[a-z0-9]{20}(@[0-4])?")

    if paipuid := pat_tenhou.search(paipu_raw):
        paipuid = paipuid.group()
        pat_target = re.compile(r"&tw=(\d+)")
        target = pat_target.search(paipu_raw)
        if target:
            target = target.group(1)
        elif target_override == -1:
            raise HTTPException(
                status_code=400, detail="Failed to infer target from url"
            )
        platform = "tenhou"
    elif paipuid := pat_majsoul.search(paipu_raw):
        paipuid = paipuid.group()
        platform = "majsoul"
    elif (paipuid := pat_rcity.search(paipu_raw)) and len(paipu_raw) < 50:
        paipuid = paipuid.group()
        platform = "riichicity"
        if "@" in paipuid:
            target = int(paipuid[-1])
            paipuid = paipuid[:-2]
        elif target_override == -1:
            raise HTTPException(
                status_code=400, detail="Failed to infer target from url"
            )
    else:
        if target_override == -1:
            raise HTTPException(
                status_code=400, detail="Failed to infer target from url"
            )
        if not (paipu_raw.startswith("{") and paipu_raw.endswith("}")):
            try:
                fragment = urlparse(paipu_raw).fragment
                query = parse_qs(fragment)
                paipu_raw = query["json"][0]
            except:
                raise HTTPException(status_code=400, detail="Failed to identify paipu")
        try:
            tmp = json.loads(paipu_raw)
            assert all(x in tmp for x in ["log", "name", "rule"])
            assert "disp" in tmp["rule"]
            platform = "custom"
            paipuid = json.dumps(tmp, ensure_ascii=False)
        except:
            raise HTTPException(status_code=400, detail="Failed to parse json paipu")

    ext = ".html" if ui == 1 else ".json"
    paipu_fn = sha256(paipuid.encode()).hexdigest()[:16]
    paipud = os.path.join(paipupath, paipu_fn)
    if not await validation_task:
        raise HTTPException(status_code=400, detail="Invalid captcha")
    print(platform, paipuid, target)
    if os.path.exists(paipud):
        try:
            with open(paipud, "r", encoding="utf-8") as f:
                paipudata = json.load(f)
        except Exception as e:
            raise HTTPException(status_code=503, detail="Failed to load cached paipu")
    else:
        f = open(paipud, "w", encoding="utf-8")
        paipudata = await download_log(paipuid, platform)
        if type(paipudata) is JSONResponse:
            f.close()
            os.remove(paipud)
            return paipudata
        json.dump(paipudata, f)
        f.close()

    if platform == "majsoul":
        try:
            target = paipudata["_target_actor"]
        except KeyError:
            if target_override == -1:
                raise HTTPException(
                    status_code=400, detail="Failed to infer target from url"
                )
            target = 0

    playernum = parse_player_num(paipudata)
    game_length = parse_game_length(paipudata)
    if playernum == 4 and game_length == 1:
        raise HTTPException(
            status_code=500, detail="Mortal4p supports hanchan games only"
        )

    if target_override != -1:
        target = target_override
    if target < 0 or target >= playernum:
        raise HTTPException(status_code=400, detail="Invalid actor")

    taskid = f"{paipuid}{target}{engine}{language}{ui}"
    filename = sha256(taskid.encode()).hexdigest()[:16]

    url = (
        app.url_path_for("process", filename=filename + ext)
        + f"?p={playernum}&e={engine}"
    )

    if os.path.exists(os.path.join(outputpath, filename) + ext):
        return RedirectResponse(url, status_code=302)
    if os.path.exists(os.path.join(lockpath, filename)):
        return RedirectResponse(url, status_code=302)

    with open(os.path.join(lockpath, filename), "w") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S"))

    task_queue = task_queue_local if engine == 1 else task_queue_ot
    qsize = task_queue.qsize()
    qsize_config = int(config["max_queue" if engine == 1 else "max_queue_ot"])
    if qsize_config and qsize >= qsize_config:
        os.remove(os.path.join(lockpath, filename))
        return JSONResponse(
            {"error": "Server at maximum capacity, try again later"}, status_code=503
        )

    task_queue.put_nowait(
        (playernum, engine, target, paipu_fn, filename, language, ui != 1)
    )
    print("Task added", filename)
    return RedirectResponse(url, status_code=302)


@app.get("/process/{filename}")
async def process(request: Request, filename: str, p: int, e: int):
    nplayer = p
    if nplayer not in [3, 4]:
        if filename.endswith(".html"):
            nplayer = 4
        else:
            raise HTTPException(status_code=400, detail="Why are you pentesting? :(")
    if e not in [1, 2]:
        raise HTTPException(status_code=400, detail="Why are you pentesting? :(")
    file_path = os.path.join(outputpath, filename)
    lockexist = os.path.exists(os.path.join(lockpath, filename[:16]))

    if os.path.exists(file_path):
        if lockexist:
            os.remove(os.path.join(lockpath, filename[:16]))
        return RedirectResponse(
            get_url(filename, 2 - int(not filename.endswith(".json")), nplayer),
            status_code=302,
        )
    else:
        if lockexist:
            return templates.TemplateResponse(
                "loading.html",
                context={
                    "qsize": (
                        task_queue_local.qsize() if e == 1 else task_queue_ot.qsize()
                    ),
                    "request": request,
                },
            )
        raise HTTPException(
            status_code=404, detail="Task not found, maybe exited unexpectedly"
        )


app.mount("/results", StaticFiles(directory="outputs"), name="results")


@app.get("/")
async def root_html(request: Request, url: str | None = None):
    context = {"captchakey": config.get("turnstile_sitekey"), "request": request}
    if url:
        context["url"] = url

    return templates.TemplateResponse(
        "index.html",
        context=context,
    )


@app.get("/ui/")
async def ui_html():
    return FileResponse("ui/index.html")


app.mount("/ui", StaticFiles(directory="ui"), name="ui")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)