CREATE TABLE IF NOT EXISTS prompt
(
    `digest`  BLOB NOT NULL,
    `system_prompt` TEXT,
    `user_prompt`   TEXT,
    `answer`        TEXT,
    `dataset_name`  TEXT,
    `language`      TEXT,
    UNIQUE (`digest`)
);

CREATE UNIQUE INDEX IF NOT EXISTS `idx_prompt_digest` ON `prompt` (`digest`);

CREATE TABLE IF NOT EXISTS result
(
    `model`   TEXT NOT NULL,
    `digest`  BLOB NOT NULL,
    `answer`  TEXT,
    `elapsed` REAL,
    `error`   TEXT,
    UNIQUE (`model`, `digest`)
);

CREATE UNIQUE INDEX IF NOT EXISTS `idx_result_model_digest` ON `result` (`model`, `digest`);
