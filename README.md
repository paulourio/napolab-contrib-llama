# Code to run experiments with Llama 3

This small repo runs experiments caching results in a sqlite db.

## Setup

Because [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) won't compile to CUDA Compute 8.9 to run with RTX40 series.
I had to change CMakeLists of `llama-cpp-python` and build a wheel with

```bash
CMAKE_ARGS="-DGGML_CUDA=ON" python -m build
```

Then, to setup a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt ../llama-cpp-python/dist/llama_cpp_python-0.2.90-cp312-cp312-linux_x86_64.whl
```

## Generating grammar

I've set up a grammar constraint for Llama to generate integers 0-5.
To generate output BNF grammar from JSON Schema:

```bash
python ~/dev/llama.cpp/examples/json_schema_to_grammar.py assets/output_schema.json > assets/output_grammar.bnf
```

## Running

I need to run once populate script to read `test.csv` into sqlite db:

```bash
python populate.py
```

Then I run experiments for some model:

```bash
python run.py -m model.gguf -g 88
```
