# mjai-reviewer-ui

Frontend UI and task runner for [mjai-reviewer](https://github.com/Equim-chan/mjai-reviewer), similar to mjai.ekyu.moe

## Features

- Automatically analyze and extract any format of input paipu, including

  - Tenhou
  - Majsoul
  - Riichicity
  - [tenhou.net/6](https://tenhou.net/6) JSON or URL

- Detect 3-player or 4-player and run the corresponding version of mjai-reviewer

- Auto detect target from the input or specify one

- Select different engines(models), UI (classic or [Killerducky](https://github.com/killerducky/killer_mortal_gui)), languages for reviewing

  > Akochan is not supported

- Task queue for concurrent users running multiple tasks

- Cloudflare Turnstile Captcha support

- Scheduler for cleaning up outputs and cached paipus

- Queue size display in loading page

## Get started

### Install Requirements

```bash
pip install fastapi[standard] uvicorn[standard] aiohhttp
```

### Set up dependencies

You need the following for this project to work

- The reviewer binary from [mjai-reviewer](https://github.com/Equim-chan/mjai-reviewer)

  - For reviewing 3-player games, you may need my fork: [mjai-reviewer3p](https://github.com/hidacow/mjai-reviewer3p/)

- The Mortal wrapper *binary* from [Mortal](https://github.com/Equim-chan/Mortal)

  - For reviewing 3-player games or using AkagiOT online model servers, you might need to modify some code in mortal by yourself

    > You might need to Donate to the Akagi project for an api key to AkagiOT server

  - You also need the **corresponding** `libriichi` libraries for Mortal to work properly

    > You might need to implement 3-player `libriichi3p` library yourself, or get one from the Akagi project through donation

- A working config for each version of Mortal, including:

  - A trained model file
  - (optional) a GRP model file (you can remove the need of it by modifying some code in mortal)

- (optional) [tensoul](https://github.com/Equim-chan/tensoul) server for downloading majsoul paipus

- (optional) Turnstile sitekey and secret for captcha to protect your server from abuse

### Write your own config

Create a file called `config.py`, you should refer to `config.example.py` and fill in the paths

### Get Killerducky UI

Clone [killer_mortal_gui](https://github.com/killerducky/killer_mortal_gui) into a directory called `ui`.

> You might need my fork of killer_mortal_gui for supporting 3-player mahjong

### Run the app

```bash
python app.py
```

or as background with custom listen address and output:

```bash
nohup uvicorn app:app --host 127.0.0.1 --port 5000 > app.log 2>&1 &
```

By default, the directory structure will be:

- `locks/`for task locks
- `outputs/` for output htmls and json
- `paipus/` for downloaded paipus
- `ui/` killer_mortal_gui static files
- `app.py` : main file
- `config.py` : your config
- `index.html`
- `loading.html`

## Credits

- [Equim-chan](https://github.com/Equim-chan) for Mortal, tensoul, mjai-reviewer, and <https://mjai.ekyu.moe>
- [shinkuan/Akagi](https://github.com/shinkuan/Akagi/)
- [killerducky/killer_mortal_gui](https://github.com/killerducky/killer_mortal_gui)
