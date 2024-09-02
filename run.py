from itertools import product
from pathlib import Path
from time import time
import argparse

from llama_cpp import Llama, LlamaGrammar
from tqdm import tqdm

from repository import Repository, PromptOutput


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model')
    parser.add_argument('-g', '--gpu_layers', type=int)
    args = parser.parse_args()

    if not args.model:
        raise RuntimeError('required --model')

    repo = Repository('repository.db')
    grammar = LlamaGrammar.from_file('assets/output_grammar.bnf')
    llm = Llama(
        model_path=args.model,
        n_ctx=2048,
        n_gpu_layers=args.gpu_layers,
        chat_format='llama-3',
        verbose=False,
    )
    model_name = Path(args.model).name
    datasets = repo.available_datasets()
    languages = repo.available_languages()

    for ds, lang in product(datasets, languages):
        prompts = repo.get_remaining_prompts(model_name, ds, lang)
        if not prompts:
            continue
        print('Processing {} prompts for datasets/{}/languages/{}'.format(
              len(prompts), ds, lang))
        for p in tqdm(prompts):
            start = time()
            response = llm.create_chat_completion(
                messages=[
                    {
                        'role': 'system',
                        'content': p.system,
                    },
                    {
                        'role': 'user',
                        'content': p.user,
                    }
                ],
                grammar=grammar,
                max_tokens=1,
                temperature=0.1,
            )
            end = time()
            answer = response['choices'][0]['message']['content']
            output = PromptOutput(
                model=model_name,
                digest=p.digest,
                answer=answer,
                elapsed=end - start,
                error='',
            )
            repo.add_result(output)


if __name__ == '__main__':
    main()
