# concierge-nlp-cluster/concierge_nlp_cluster/utils/__init__.py
import yaml

# Load and parse the config.yml file
with open("config.yml", "r") as config_file:
    config = yaml.safe_load(config_file)

# Set model and max_tokens from the config.yml file
embedding_model = config["models"]["embedding"]["model"]
max_tokens = config["models"]["completion"]["max_tokens"]
