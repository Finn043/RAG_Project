from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader

loader = DirectoryLoader(
    path= "./papers",
    glob="**/*.pdf",
    loader_cls=PyPDFLoader,
    show_progress=True,
    use_multithreading=True
    
)

docs = loader.load()

print (docs)
print(len(docs))
