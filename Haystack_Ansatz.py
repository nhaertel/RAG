from haystack import Pipeline, Document
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.converters import PyPDFToDocument
from haystack.components.preprocessors import DocumentCleaner
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack_integrations.components.generators.ollama import OllamaGenerator

file_names = ["/home/adminrag/Desktop/HsbInfos.pdf"] 

# Write documents to InMemoryDocumentStore
document_store = InMemoryDocumentStore()

pdfPipeline = Pipeline()
pdfPipeline.add_component("converter", PyPDFToDocument())
pdfPipeline.add_component("cleaner", DocumentCleaner())
pdfPipeline.add_component("splitter", DocumentSplitter(split_by="period", split_length=2))
pdfPipeline.add_component("writer", DocumentWriter(document_store=document_store))
pdfPipeline.connect("converter", "cleaner")
pdfPipeline.connect("cleaner", "splitter")
pdfPipeline.connect("splitter", "writer")

pdfPipeline.run({"converter":{"sources": file_names}})


# Build a RAG pipeline
prompt_template = """
Given these documents, answer the question. Ignore your own knowledge.
Context:
{% for doc in documents %}
    {{ doc.content }}
{% endfor %}
Question: {{question}}
"""

retriever = InMemoryBM25Retriever(document_store=document_store)
prompt_builder = PromptBuilder(template=prompt_template)

rag_pipeline = Pipeline()
rag_pipeline.add_component("retriever", retriever)
rag_pipeline.add_component("prompt_builder", prompt_builder)
rag_pipeline.connect("retriever", "prompt_builder.documents")
rag_pipeline.add_component("llm", OllamaGenerator(model="llama3.1:latest", url="https://ollama.on.hs-bremen.de:11434"))
rag_pipeline.connect("prompt_builder", "llm")

# Ask a question

print("Stelle eine Frage")
question = input()
results = rag_pipeline.run(
    {
        "retriever": {"query": question},
        "prompt_builder": {"question": question},
    }
)

print(results.get("llm").get("replies"))

