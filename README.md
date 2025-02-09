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

- Select multiple different engines(models), UI (classic or [Killerducky](https://github.com/killerducky/killer_mortal_gui)), languages for reviewing

  > Akochan is not supported

- Task queue for concurrent users running multiple tasks

- Cloudflare Turnstile Captcha support

- Scheduler for cleaning up outputs and cached paipus

- Queue size display in loading page

- 'Play with you' feature in tenhou private lobby


## Get started

### Install Requirements

```bash
pip install fastapi[standard] uvicorn[standard] aiohhttp "filelock>3.15" toml
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

- A valid config for each version of Mortal, including:

  - A trained model file
  - (optional) a GRP model file (you can remove the need of it by modifying some code in mortal)

- (optional) [tensoul](https://github.com/Equim-chan/tensoul) server for downloading majsoul paipus

- (optional) Turnstile sitekey and secret for captcha to protect your server from abuse

### Write your own config

Create a file called `config.py`, you should refer to `config.example.py` and fill in the paths

### Get Killerducky UI

Clone [killer_mortal_gui](https://github.com/killerducky/killer_mortal_gui) into a directory called `ui`.

> You might need my fork of killer_mortal_gui for supporting 3-player mahjong

### 'Play with you' feature

This project supports the feature that summons Mortal instances into tenhou private lobbies, similar to the one on mjai.ekyu.moe

The app will run `3p.py`  in `config['tenhoubot_path']` with the following params in a subprocess:

```bash
--model modelpath --room roomid[1000-9999] --speed speed[0-2]
```

The app will use regex to parse the output for tenhou log url for the logging feature.

You may **implement the bot by yourself** in order to use this feature. (bot not open source for now)

> The app only targets 3-player South for now. (Send at most 2 bots at a time)

### Run the app

```bash
python app.py
```

or as background with custom listen address and output:

```bash
nohup uvicorn app:app --host 127.0.0.1 --port 5000 > app.log 2>&1 &
```

By default, the directory structure will be:

- `botlog/` for bot logs in 'Play with you' feature
- `locks/`for task locks
- `outputs/` for output htmls and json
- `paipus/` for downloaded paipus
- `ui/` killer_mortal_gui static files
- `static/` static files
- `app.py` : main file
- `config.py` : your config
- `index.html`
- `loading.html`
- ...

## Credits

- [Equim-chan](https://github.com/Equim-chan) for Mortal, tensoul, mjai-reviewer, and <https://mjai.ekyu.moe>
- [shinkuan/Akagi](https://github.com/shinkuan/Akagi/)
- [killerducky/killer_mortal_gui](https://github.com/killerducky/killer_mortal_gui)
