config = {
    "tensoul": "https://your_deployed_tensoul/convert?id=",
    "tensoul_usr": "",
    "tensoul_pwd": "",
    "citylogs": "https://rc.honk.li/api/log",
    "reviewer3p": "/path/to/mjai-reviewer3p/target/release/mjai-reviewer",
    "reviewer4p": "/path/to/mjai-reviewer/target/release/mjai-reviewer",
    "local3p": "/path/to/exe-wrapper.exe or /mortal for 3 player game",
    "local3p_conf": "/path/to/config.toml for 3 player game",
    "local4p": "/path/to/exe-wrapper.exe or /mortal for 4 player game",
    "local4p_conf": "/path/to/config.toml for 4 player game",
    "akagiot3p": "/path/to/wrapper for AkagiOT bot",
    "akagiot3p_conf": "/path/to/config.toml for AkagiOT bot",
    "akagiot4p": "/path/to/wrapper for AkagiOT bot",
    "akagiot4p_conf": "/path/to/config.toml for AkagiOT bot",
    "turnstile_sitekey": "",
    "turnstile_secret": "",
    "max_task": 2,  # concurrent task limit
    "max_queue": 0,  # reject new task if queue size exceeds this limit, 0 to disable
    "max_task_ot": 1,  # concurrent task limit for AkagiOT, OT API has rate limit
    "max_queue_ot": 0,  # max queue size, 0 to disable
    "file_expire": 0,  # 1296000, # Retain paipu and output files for 15 days, 0 to disable
    "clean_interval": 0,  # 3600,   # Clean paipu and output files every hour, 0 to disable
}
