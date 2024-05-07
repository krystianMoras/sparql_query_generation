import requests
from fastembed import TextEmbedding
import chromadb
import json

embedding_model = TextEmbedding()
chroma_client = chromadb.PersistentClient(path="../props_vector_db")

collection = chroma_client.get_collection("wikidata_properties")

entity_properties = {}

with open("entity_properties.jsonl", "r") as f:
    for line in f:
        entity_properties.update(json.loads(line))


def get_property_value(property_id, entity_id):
    query = f'SELECT ?value ?valueLabel WHERE {{ wd:{entity_id} wdt:{property_id} ?value . SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }} }}'
    url = "https://query.wikidata.org/sparql"
    r = requests.get(url, params={"query": query, "format": "json"})
    data = r.json()
    if len(data["results"]["bindings"]) == 0:
        return None

    answer_set = set()

    for binding in data["results"]["bindings"]:
        answer_set.add(binding["value"]["value"].split("/")[-1])

    return answer_set, query


def find_properties_for_entity(entity_id):
    if entity_id in entity_properties:
        return entity_properties[entity_id]

    query = (
        "SELECT ?pLabel ?p WHERE { wd:"
        + entity_id
        + ' ?a ?b.  ?p wikibase:directClaim ?a . SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }}'
    )

    url = "https://query.wikidata.org/sparql"
    r = requests.get(url, params={"query": query, "format": "json"})
    data = r.json()
    props = []
    for binding in data["results"]["bindings"]:
        props.append(binding["p"]["value"].split("/")[-1])

    entity_properties[entity_id] = props

    with open("entity_properties.jsonl", "a") as f:
        f.write(json.dumps({entity_id: props}) + "\n")

    return props


def answer_simple_direct_question(question, entity_id):
    question_embedding = list(embedding_model.embed([question]))[0].tolist()

    allowed_properties = find_properties_for_entity(entity_id)

    result = collection.query(
        question_embedding, where={"prop": {"$in": allowed_properties}}
    )

    best_fit_prop = result["metadatas"][0][0]["prop"]

    answers, query = get_property_value(best_fit_prop, entity_id)

    return answers, query


# if __name__ == "__main__":

#     question = "What is the capital of India?"
#     entity_id = "Q668"
#     entity_label = "India"

#     answer_simple_direct_question(question, entity_id, entity_label)
