import requests
from fastembed import TextEmbedding
import chromadb

embedding_model = TextEmbedding()
chroma_client = chromadb.PersistentClient(path="../props_vector_db")

collection = chroma_client.get_collection("wikidata_properties")
def get_property_value(property_id, entity_id):
    query =  f'SELECT ?value ?valueLabel WHERE {{ wd:{entity_id} wdt:{property_id} ?value . SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }} }}'

    url = "https://query.wikidata.org/sparql"
    r = requests.get(url, params={"query": query, "format": "json"})
    data = r.json()
    if len(data["results"]["bindings"]) == 0:
        return None
    
    return (data["results"]["bindings"][0]["value"]["value"], data["results"]["bindings"][0]["valueLabel"]["value"])


def find_properties_for_entity(entity_id):
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

    return props


def answer_simple_direct_question(question, entity_id, entity_label):

    question_embedding = list(embedding_model.embed([question]))[0].tolist()

    allowed_properties = find_properties_for_entity(entity_id)

    result = collection.query(question_embedding, where={
    "prop":{
        "$in": allowed_properties
    }
    })

    best_fit_prop = result["metadatas"][0][0]["prop"]

    value, value_label = get_property_value(best_fit_prop, entity_id)

    print(f"{entity_id}:{entity_label}  {value}:{value_label}")
    return f"{entity_id}:{entity_label}  {value}:{value_label}"


if __name__ == "__main__":

    question = "What is the capital of India?"
    entity_id = "Q668"
    entity_label = "India"

    answer_simple_direct_question(question, entity_id, entity_label)




