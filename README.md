# sparql_query_generation

## Setup 

```bash
make install
```

get vector store with calculated embeddings of properties or create your own according to embed_properties.ipynb

put the vector store inside "../props_vector_db" #todo

## Run server

```bash
make run
```

Answer a simple direct question:

http://127.0.0.1:5000/answer_question?question=What%20is%20Davids%20party?&entity_id=Q5217081&entity_label=David

