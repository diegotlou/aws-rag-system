from abc import ABC, abstractmethod

class CredentialProvider(ABC):
    @abstractmethod
    def get(self, key):
        pass

class EnvCredentials(CredentialProvider):
    def get(self, key):
        from dotenv import load_dotenv
        import os
        load_dotenv()
        env_var = os.getenv(key)
        if env_var is None:
            raise EnvironmentError(f"Env variable not found: {key}")
        return env_var

class StreamlitCredentials(CredentialProvider):
    def get(self, key):
        import streamlit as st
        return st.secrets[key]

def get_credentials(source):
    if source == "streamlit" : return StreamlitCredentials()
    if source == "env" : return EnvCredentials()

    # Se regresan las credenciales de .secrets en caso de detectarse una sesion de Streamlit
    # De otra forma, se cargan las variables de entorno
    try:
        import streamlit as st
        st.runtime.get_instance()
        return StreamlitCredentials()
    except Exception:
        print("No Streamlit session detected\nLoading environment variables instead")
        return EnvCredentials()