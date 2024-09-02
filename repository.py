from contextlib import closing
from dataclasses import dataclass
from hashlib import sha256
import sqlite3

from tqdm import tqdm


@dataclass
class PromptCase:
    digest: bytes
    system: str
    user: str
    answer: str
    dataset: str
    language: str

    def __repr__(self):
        return f'PromptCase({self.digest.hex()[-6:]})'


@dataclass
class PromptOutput:
    model: str
    digest: bytes
    answer: str
    elapsed: float
    error: str


class Repository:

    def __init__(self, fname):
        self.con = sqlite3.connect(fname)
        self._up()

    def _up(self):
        with closing(self.con.cursor()) as cur:
            cur.executescript(open('assets/up.sql').read())
        self.con.commit()

    def add_prompts(self, prompts):
        data = []
        for p in tqdm(prompts):
            data.append((
                make_digest(p),
                p['system_prompt'],
                p['user_prompt'],
                p['answer'],
                p['dataset_name'],
                p['language'],
            ))
        with closing(self.con.cursor()) as cur:
            cur.executemany(
                ('INSERT INTO prompt '
                 '(digest, system_prompt, user_prompt, answer, dataset_name, language) '
                 'VALUES (?, ?, ?, ?, ?, ?) '
                 'ON CONFLICT (digest) DO NOTHING;'),
                data)
        self.con.commit()

    def add_result(self, po: PromptOutput):
        with closing(self.con.cursor()) as cur:
            cur.execute(
                ('INSERT INTO result (model, digest, answer, elapsed, error) '
                 'VALUES (?, ?, ?, ?, ?) '
                 'ON CONFLICT (model, digest) '
                 'DO UPDATE SET answer = ?, elapsed = ?, error = ?'),
                (po.model, po.digest, po.answer, po.elapsed, po.error,
                 po.answer, po.elapsed, po.error),
            )
        self.con.commit()

    def get_remaining_prompts(self, model, dataset, language) -> list[PromptCase]:
        sql = (
            'SELECT p.digest, p.system_prompt, p.user_prompt, p.answer, '
            'p.dataset_name, p.language '
            'FROM prompt AS p '
            'LEFT JOIN (SELECT digest FROM result WHERE model = ?) AS r '
            'ON p.digest = r.digest '
            'WHERE p.dataset_name = ? '
            'AND p.language = ? '
            'AND r.digest IS NULL '
        )
        prompts = []
        with closing(self.con.cursor()) as cur:
            for p in cur.execute(sql, (model, dataset, language)):
                prompts.append(PromptCase(*p))
        return prompts

    def available_datasets(self):
        with closing(self.con.cursor()) as cur:
            return [x[0] for x in cur.execute(
                'SELECT DISTINCT dataset_name FROM prompt ORDER BY 1')]

    def available_languages(self):
        with closing(self.con.cursor()) as cur:
            return [x[0] for x in cur.execute(
                'SELECT DISTINCT language FROM prompt ORDER BY 1')]


def make_digest(prompt):
    h = sha256()
    s1, s2 = prompt['sentence1'], prompt['sentence2']
    h.update(s1.encode() if isinstance(s1, str) else 'null'.encode())
    h.update(';'.encode())
    h.update(s2.encode() if isinstance(s2, str) else 'null'.encode())
    return h.digest()
