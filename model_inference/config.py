import os

class Settings:
    BASE_MODEL: str = os.getenv("MINDBRIDGE_BASE_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")
    ADAPTER_ID: str = os.getenv("MINDBRIDGE_ADAPTER_ID", "aayush0K/Llama-3-MindBridge")
    ADAPTER_PATH: str = os.getenv("MODEL_ADAPTER_PATH", "../training/models/mindbridge-llm")
    DEVICE: str = os.getenv("DEVICE", "cuda") # or "cpu"
    HOST: str = os.getenv("INFERENCE_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("INFERENCE_PORT", "8001"))
    API_KEY: str = os.getenv("REMOTE_INFERENCE_API_KEY", os.getenv("INFERENCE_API_KEY", ""))

settings = Settings()
