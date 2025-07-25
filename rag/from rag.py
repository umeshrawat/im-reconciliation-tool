from rag.vector_store import add_document, query_documents, persist

# Add a document
add_document("doc1", "Trade ID 123 was acknowledged.", {"type": "ack"})

# Query similar documents
results = query_documents("Was Trade ID 123 acknowledged?")
print(results)

# Persist the database
persist()