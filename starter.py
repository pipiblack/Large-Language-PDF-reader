from llama_index import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage
)
import openai
openai.api_key = "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"
import os.path

PERSIST_DIR = "./storage"

if not os.path.exists(PERSIST_DIR):
    document = SimpleDirectoryReader("ode").load_data()
    index = VectorStoreIndex(document)
    #store indx for later use
    index.storage_context.persist(persist_dir = PERSIST_DIR)
else:
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)

# creating query index
query_engine = index.as_query_engine()
response = query_engine.query("Find the general solution to the differential equation (𝑥 + 𝑦)𝑑𝑦 − (𝑥 − 𝑦)𝑑𝑥 = 0 ,show your steps clearly")
print(response)

