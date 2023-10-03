from jsonformer import Jsonformer
from transformers import AutoModelForCausalLM, AutoTokenizer
folderLocation = "D:\TextGenModels\TheBloke_Redmond-Puffin-13B-GPTQ_gptq-4bit-32g-actorder_True\config.json"
# load from local
#model = AutoModelForCausalLM.from_pretrained(folderLocation, use_safetensors=True, from_tf=True, load_in_4bit= True, device_map = 'auto')
#tokenizer = AutoTokenizer.from_pretrained(folderLocation)

model = AutoModelForCausalLM.from_pretrained("databricks/dolly-v2-3b", device_map = 'auto')
tokenizer = AutoTokenizer.from_pretrained("databricks/dolly-v2-3b")

json_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "number"},
        "is_student": {"type": "boolean"},
        "courses": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}

prompt = "Generate a person's information based on the following schema:"
jsonformer = Jsonformer(model, tokenizer, json_schema, prompt)
generated_data = jsonformer()

print(generated_data)