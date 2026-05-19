from pathlib import Path

def read_local_data(file):
    # Regresa el contenido del archivo, si es prompt, busca en la carpeta "prompts", si no, busca en "evals"
    folder = "prompts" if "prompt" in file else "evals/eval_data"
    prompt_path = Path(__file__).parent.parent / folder / file
    with open(prompt_path, "r") as f:
        prompt = f.read()
    return prompt