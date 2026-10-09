"""Device selection shared by the model and status endpoint."""
import os


def runtime_info():
    import torch

    requested = os.environ.get('VOZ_LOCAL_DEVICE', 'auto').lower()
    if requested not in ('auto', 'cpu', 'cuda', 'mps'):
        raise RuntimeError('VOZ_LOCAL_DEVICE must be auto, cpu, cuda or mps.')
    if requested in ('auto', 'cuda') and torch.cuda.is_available():
        devices = range(torch.cuda.device_count())
        index = max(devices, key=lambda i: (
            '9060' in torch.cuda.get_device_name(i), torch.cuda.get_device_properties(i).total_memory))
        with torch.cuda.device(index):
            dtype = 'bfloat16' if torch.cuda.is_bf16_supported() else 'float16'
        return {'device': f'cuda:{index}', 'dtype': dtype, 'gpu_available': True,
                'gpus': [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())],
                'backend': 'ROCm' if torch.version.hip else 'CUDA'}
    if requested == 'cuda':
        raise RuntimeError('PyTorch cannot access the GPU. Check the driver and PyTorch installation.')
    # MPS is opt-in until voice generation is verified on a real Mac.
    if requested == 'mps':
        if not torch.backends.mps.is_available():
            raise RuntimeError('PyTorch MPS is not available on this Mac.')
        return {'device': 'mps', 'dtype': 'float32', 'gpu_available': True,
                'gpus': ['Apple MPS'], 'backend': 'MPS (experimental)'}
    return {'device': 'cpu', 'dtype': 'float32', 'gpu_available': False,
            'gpus': [], 'backend': 'CPU'}
