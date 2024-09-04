import os
import faiss
import re
import signal
from io import StringIO
import asyncio
from contextlib import redirect_stdout
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_community.llms import Ollama
from langchain_community.docstore.in_memory import InMemoryDocstore
import uuid

# Custom timeout exception
class TimeoutException(Exception):
    pass

# Timeout handler function
def timeout_handler(signum, frame):
    raise TimeoutException()

# Step 1: Initialize the Ollama LLM
llm = Ollama(model="llama3.1:8b-instruct-fp16")

# Step 2: Create a FAISS vectorstore for storing context or code snippets
embedding_model = HuggingFaceEmbeddings()
embedding_dimension = len(embedding_model.embed_query("test query"))
index = faiss.IndexFlatL2(embedding_dimension)

# Set up the docstore and index-to-docstore ID mapping
docstore = InMemoryDocstore({})
index_to_docstore_id = {}

vectorstore = FAISS(embedding_function=embedding_model, index=index, docstore=docstore, index_to_docstore_id=index_to_docstore_id)

# Create the cache directory if it doesn't exist
cache_dir = "cache"
os.makedirs(cache_dir, exist_ok=True)

# Step 3: Define the prompt and agent's chain
system_message = SystemMessagePromptTemplate.from_template(
    "Você é uma assistente de IA que gera código Python. "
    "Por favor, forneça apenas o bloco de código entre três crases. "
    "Você não deve incluir bibliotecas externas como numpy, pandas, etc. "
    "Sempre tente garantir que os programas funcionem corretamente e em no máximo 30 segundos eles devem ser terminados. "
    "Qualquer descrição ou informação adicional deve ser retornada como metadados."
)
human_message = HumanMessagePromptTemplate.from_template("Query: {combined_input}")

prompt = ChatPromptTemplate.from_messages([system_message, human_message])

def combine_input(context, query, short_term_memory):
    return f"Context: {context}\nShort-Term Memory: {short_term_memory}\nQuestion: {query}"

# Short-Term Memory to keep track of the last 5 messages
short_term_memory = []

# Step 4: Parse, Save, Execute, and Store Code with Error Handling
def parse_code_from_response(response):
    # Extract code blocks (assuming code is within triple backticks)
    code_blocks = re.findall(r"```python(.*?)```", response, re.DOTALL)
    return code_blocks

def execute_code(code):
    # Redirecionar stdout para capturar declarações de impressão
    with StringIO() as buf, redirect_stdout(buf):
        try:
            exec(code)
            output = buf.getvalue()
        except Exception as e:
            output = str(e)
            code += f"\n\n# Error: {output}"  # Adiciona o erro ao código
    return output, code

def save_code_to_cache(code):
    file_id = str(uuid.uuid4())
    file_name = f"{file_id}.py"
    file_path = os.path.join(cache_dir, file_name)
    
    with open(file_path, 'w') as file:
        file.write(code)
    
    return file_path

def chunk_and_store_code(code, vectorstore, description):
    # Dividir o código em chunks e armazenar no vectorstore com metadatas
    chunk_size = 512
    for i in range(0, len(code), chunk_size):
        chunk = code[i:i + chunk_size]
        doc_id = str(uuid.uuid4())
        metadata = {"description": description}
        vectorstore.add_texts([chunk], ids=[doc_id], metadatas=[metadata])

# Exemplo de uso:
# chunk_and_store_code(updated_code, vectorstore, "Código para desenhar um fractal em ASCII")

def save_vectorstore(vectorstore, directory="vectorstore"):
    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    # Save the vectorstore
    vectorstore.save_local(directory)

# Step 5: Define an async function to interact with the agent
async def run_agent(query: str):
    # Retrieve long-term memory chunks
    context_documents = vectorstore.similarity_search(query)
    context_chunks = [doc.page_content for doc in context_documents]
    context_metadata = [doc.metadata for doc in context_documents]  # Captura os metadados
    context = "\n".join(context_chunks)

    # Combine the short-term memory and the query
    combined_input = combine_input(context, query, "\n".join(short_term_memory))
    
    # Asynchronously stream the response and execute any code found
    response_chunks = []
    async for chunk in llm.astream(combined_input):  # Pass the combined input as a string
        response_chunks.append(chunk)  # Append the chunk directly, as it's a string
        print(chunk, end="", flush=True)
    
    # Combine the response chunks
    response = "".join(response_chunks)
    
    # Parse and execute code
    code_blocks = parse_code_from_response(response)

    if not code_blocks:
        print("Nenhum código encontrado na resposta.")
        return "Nenhum código para executar."

    # Extrair a descrição dos metadados
    metadata_description = response.split("```python")[0].strip()  # O texto antes do bloco de código

    for code in code_blocks:
        print("\nExecutando código...\n")
        temp_file_path = save_code_to_cache(code)
        output, updated_code = execute_code(code)
        print(output)  # Mostrar a saída da execução do código

        # Salvar o código com comentários de erro potenciais no cache
        save_code_to_cache(updated_code)
        
        # Armazenar o código no vectorstore com a descrição extraída
        chunk_and_store_code(updated_code, vectorstore, metadata_description)
    
    # Atualizar a memória de curto prazo
    short_term_memory.append(query)
    if len(short_term_memory) > 5:
        short_term_memory.pop(0)
    
    # Salvar o vectorstore após o processamento
    save_vectorstore(vectorstore)
    
    return output

# Step 6: Main entry point for running the agent
if __name__ == "__main__":
    while True:
        user_input = input("Enter your request: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        asyncio.run(run_agent(user_input))
