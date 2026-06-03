# AWS RAG System

**Asistente técnico especializado en Amazon EC2**

Este proyecto demuestra la creación de un sistema de recuperación aumentada por memoria (RAG) para consultas sobre documentación técnica de AWS EC2. La idea es agregar más documentación en un futuro. Está diseñado para ofrecer respuestas precisas y basadas en contexto, con una integración práctica de almacenamiento vectorial, embeddings y un modelo de lenguaje enfocado en AWS.

## Qué incluye

- **Aplicación Streamlit** para interactuar con el asistente de EC2.
- **Ingestión de documentos** en formato PDF y almacenamiento de contexto con MongoDB.
- **Indexación en Pinecone** para recuperación de información relevante.
- **Uso de embeddings HuggingFace** con `BAAI/bge-small-en-v1.5`.
- **LLM** especializado en respuestas técnicas de AWS (actualmente solo temas de EC2).
- **Mecanismo de evaluación** automatizado con criterios de fidelidad y relevancia.

## Tecnologías clave

- Streamlit
- Pinecone
- MongoDB
- LlamaIndex
- GoogleGenAI
- HuggingFace Embeddings
- PyMuPDF

## Estructura del proyecto

- `Chat.py` - aplicación web con streamlit para consultas.
- `data_ingestion.py` -  pide una ruta de una carpeta, toma los archivos dentro de la carpeta, genera los nodos de los documentos con `HierarchicalNodeParser` y  usa el modelo de embedding de HigginFace `BAAI/bge-small-en-v1.5` para indexar los embeddings de los nodos hoja en **Pinecone**, el resto de nodos se almacenan en **MongoDB**.
- `evaluator.py` -  hace una evaluación con **LLM as a Judge**, el sistema RAG contesta preguntas orientadas a evaluar: relevancia, fidelidad y robustez.

## Cómo usarlo

1. Agregar las bibliotecas necesarias `uv add streamlit pinecone llama-index-core llama-index-llms-google-genai llama-index-embeddings-huggingface llama-index-vector-stores-pinecone llama-index-readers-file pymupdf`
    * El archivo `requirements.txt` solo tiene las bibliotecas necesarias para la ejecución de **Chat.py**
2. Configurar las claves en `st.secrets` y variables `.env`.
3. Ejecutar `data_ingestion.py` para cargar la documentación.
4. Iniciar la aplicación con `streamlit run Chay.py` ó `python -m streamlit run Chay.py`.
5. Consultar la documentación de EC2 desde la interfaz.

## Resultados esperados

- Entregas de respuestas basadas en contexto y no en conjeturas.
- Evaluación de calidad según fidelidad y relevancia.
- Un sistema de soporte técnico para EC2 con enfoque en AWS.
