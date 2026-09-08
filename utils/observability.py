from llama_index.core import Settings
from llama_index.core.callbacks import CallbackManager
from langfuse.llama_index import LlamaIndexCallbackHandler, LlamaIndexInstrumentor

def init_observability(credentials):
    langfuse_callback_handler = LlamaIndexCallbackHandler(
        public_key=credentials.get("LANGFUSE_PUBLIC_KEY"),
        secret_key=credentials.get("LANGFUSE_SECRET_KEY"),
        host=credentials.get("LANGFUSE_BASE_URL"),
        debug=True
    )
    Settings.callback_manager = CallbackManager([langfuse_callback_handler])
    return langfuse_callback_handler

def init_instrumentor(credentials):
    instrumentor = LlamaIndexInstrumentor(
        public_key=credentials.get("LANGFUSE_PUBLIC_KEY"),
        secret_key=credentials.get("LANGFUSE_SECRET_KEY"),
        host=credentials.get("LANGFUSE_BASE_URL"),
        debug=True
    )
    instrumentor.start()
    return instrumentor