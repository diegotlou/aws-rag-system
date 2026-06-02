from pathlib import Path

def read_local_data(file):
    # Regresa el contenido del archivo, si es prompt, busca en la carpeta "prompts", si no, busca en "evals"
    folder = "prompts" if "prompt" in file else "evals/eval_data"
    data_path = Path(__file__).parent.parent / folder / file
    with open(data_path, "r") as f:
        if folder == "prompts" : prompt = f.read()
        else : prompt = f.readlines()
    return prompt