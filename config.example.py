config = {
    "tensoul": "https://your_deployed_tensoul/convert?id=",
    "tensoul_usr": "",
    "tensoul_pwd": "",
    "citylogs": "https://rc.honk.li/api/log",
    "models3p": [
        # to disable 3p or 4p reviewing, set the list to empty
        {
            "name": "local 3p model 1",
            "reviewer": "/path/to/mjai-reviewer3p/target/release/mjai-reviewer",
            "mortal": "/path/to/exe-wrapper.exe or /mortal for 3 player game",
            "config": "/path/to/config.toml for 3 player game",
            "is_online": False,
        },
        {
            "name": "local 3p model 2",
            "reviewer": "/path/to/mjai-reviewer3p/target/release/mjai-reviewer",
            "mortal": "...", # diffrent folder from other models recommended
            "config": "...", # diffrent folder from other models recommended  
            "is_online": False,
        },
        {
            "name": "online model eg. AkagiOT",
            "reviewer": "/path/to/mjai-reviewer3p/target/release/mjai-reviewer",
            "mortal": "/path/to/wrapper for AkagiOT bot",
            "config": "/path/to/config.toml for AkagiOT bot",
            "is_online": True,
        },
    ],
    "models4p": [
        {
            "name": "local 4p model",
            "reviewer": "/path/to/mjai-reviewer/target/release/mjai-reviewer",
            "mortal": "/path/to/exe-wrapper.exe or /mortal for 4 player game",
            "config": "/path/to/config.toml for 4 player game",
            "is_online": False,
        },
        {
            "name": "online model eg. AkagiOT",
            "reviewer": "/path/to/mjai-reviewer/target/release/mjai-reviewer",
            "mortal": "/path/to/wrapper for AkagiOT bot",
            "config": "/path/to/config.toml for AkagiOT bot",
            "is_online": True,
        },
    ],
    "turnstile_sitekey": "",    # captcha is disabled if sitekey and secret is empty
    "turnstile_secret": "",
    "max_task": 2,  # concurrent task limit
    "max_queue": 0,  # reject new task if queue size exceeds this limit, 0 to disable
    "max_task_ot": 1,  # concurrent task limit for AkagiOT, OT API has rate limit
    "max_queue_ot": 0,  # max queue size, 0 to disable
    "file_expire": 0,  # 1296000, # Retain paipu and output files for 15 days, 0 to disable
    "clean_interval": 0,  # 3600,   # Clean paipu and output files every hour, 0 to disable
}
