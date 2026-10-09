from pathlib import Path
from huggingface_hub import snapshot_download

root = Path(__file__).resolve().parent.parent
destination = root / 'data/models/Qwen3-TTS-12Hz-1.7B-Base'
required = ('model.safetensors', 'config.json', 'generation_config.json',
            'preprocessor_config.json', 'tokenizer_config.json', 'vocab.json', 'merges.txt',
            'speech_tokenizer/model.safetensors', 'speech_tokenizer/config.json')
if not all((destination / name).is_file() for name in required):
    snapshot_download(repo_id='Qwen/Qwen3-TTS-12Hz-1.7B-Base', local_dir=destination)
print('Voice model ready / Modelo de voz preparado.')
