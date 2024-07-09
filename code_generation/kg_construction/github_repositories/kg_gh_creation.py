import os
import nest_asyncio
from jinja2 import Template
from IPython.display import HTML, Markdown, display
from llama_index.core import (
    StorageContext, ServiceContext, KnowledgeGraphIndex, Settings
)
from llama_index.readers.github import GithubRepositoryReader, GithubClient
from llama_index.core.prompts.base import PromptTemplate
from llama_index.core.prompts.prompt_type import PromptType
from llama_index.llms.openai import OpenAI
from llama_index.core.graph_stores import SimpleGraphStore
from pyvis.network import Network
from dotenv import load_dotenv
import s3fs
import re
import logging
from datetime import datetime

from llama_index.core import Settings
from llama_index.llms.bedrock import Bedrock
from llama_index.embeddings.bedrock import BedrockEmbedding


# Configure logging
logging.basicConfig(filename='logs.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


nest_asyncio.apply() 

# Static variables
AWS_REGION = "us-east-1"
LLM_MODEL = "anthropic.claude-3-sonnet-20240229-v1:0"
EMBED_MODEL = "cohere.embed-multilingual-v3"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KG_TRIPLETS_TEMPLATE = os.path.join(BASE_DIR, 'code_generation', 'prompts', 'kg_triplets_template.prompt')

def load_template(file_path):
    """Load and return the Jinja2 template from the given file path."""
    with open(file_path, 'r') as file:
        return Template(file.read())

def set_llms():
    Settings.llm = Bedrock(
        model=LLM_MODEL,
        region_name=AWS_REGION,
        context_size=200000,
        timeout=180,
    )
    Settings.embed_model = BedrockEmbedding(
        model=EMBED_MODEL,
        region_name=AWS_REGION,
        timeout=180
    )

def load_environment_variables():
    load_dotenv()
    os.environ['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
    os.environ['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY')
    openai_api_key = os.getenv("OPENAI_API_KEY")
    github_token = os.getenv("GITHUB_TOKEN")
    logging.info("Environment variables loaded")
    return openai_api_key, github_token

def load_github_documents(github_token, owner, repo):
    github_client = GithubClient(github_token=github_token, verbose=True)
    branches = ["main", "master"]

    
    for branch in branches:
        try:
            documents = GithubRepositoryReader(
                github_client=github_client,
                owner=owner,
                repo=repo,
                use_parser=True,
                verbose=False,
                filter_file_extensions=(
                [
                    ".rs",
                    ".ms",
                    ".toml",
                ],
                GithubRepositoryReader.FilterType.INCLUDE,
                ),
            ).load_data(branch=branch)
            logging.info(f"GH Loaded data from branch '{branch}' for repo '{owner}/{repo}'")
            return documents
        except Exception as e:
            logging.error(f"Failed to load data from branch '{branch}' for repo '{owner}/{repo}': {e}")
    
    logging.warning(f"Skipping repo '{owner}/{repo}' as both 'main' and 'master' branches failed.")
    return None

def create_kg_triplet_extraction_template():
    template = load_template(KG_TRIPLETS_TEMPLATE)
    template_str = template.render()
    
    return PromptTemplate(template_str, prompt_type=PromptType.KNOWLEDGE_TRIPLET_EXTRACT)

def create_knowledge_graph_index(documents, triplet_template, max_retries=3, initial_wait=1):
    retries = 0
    while retries < max_retries:
        try:
            logging.info("Inside create_knowledge_graph_index function")
            graph_store = SimpleGraphStore()
            storage_context = StorageContext.from_defaults(graph_store=graph_store)
            index = KnowledgeGraphIndex.from_documents(
                documents=documents,
                kg_triple_extract_template=triplet_template,
                max_triplets_per_chunk=6,
                storage_context=storage_context,
                show_progress=True,
                include_embeddings=True
            )
            logging.info("Knowledge Graph Index created")
            return index
        except Exception as e:
            if "ModelTimeoutException" in str(e):  # Checking for timeout error in the exception message
                retries += 1
                wait_time = initial_wait * (2 ** retries)  # Exponential backoff
                logging.warning(f"ModelTimeoutException occurred. Retrying {retries}/{max_retries} in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logging.error("An error occurred while creating the Knowledge Graph Index: %s", str(e))
                return None
    logging.error("Failed to create Knowledge Graph Index after multiple retries")
    return None


def query_knowledge_graph_index(index, query):
    query_engine = index.as_query_engine()
    response = query_engine.query(query)
    return response.response

def visualize_knowledge_graph(index, output_directory):
    g = index.get_networkx_graph()
    net = Network(
        notebook=False,
        cdn_resources="remote",
        height="500px",
        width="60%",
        select_menu=True,
        filter_menu=False
    )
    net.from_nx(g)
    net.force_atlas_2based(central_gravity=0.015, gravity=-31)
    net.show(output_directory, notebook=False)
    display(HTML(filename=output_directory))
    logging.info(f"Knowledge Graph visualized and saved to {output_directory}")


def persist_knowledge_graph(index, kg_name, urls):
    if kg_name is None or len(kg_name) == 0:
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        kg_name = f"kg_{ts}"
    
    BUCKET_NAME = 'knowledge-graph-data'
    FOLDER_NAME = f"{kg_name}/kg_data"
    S3_PATH = f"s3://{BUCKET_NAME}/{FOLDER_NAME}"
    
    # Persist knowledge graph
    s3 = s3fs.S3FileSystem(anon=False)
    index.storage_context.persist(persist_dir=S3_PATH, fs=s3)
    logging.info(f"Persisted knowledge graph to S3 at {S3_PATH}")
    
    # Save URLs to source.txt
    FOLDER_NAME_source = f"{kg_name}"
    S3_PATH_source = f"s3://{BUCKET_NAME}/{FOLDER_NAME_source}/source.txt"
    
    # Create the source.txt content
    urls_content = "\n".join(urls)
    
    with s3.open(S3_PATH_source, 'w') as f:
        f.write(urls_content)
    
    logging.info(f"Persisted source URLs to S3 at {S3_PATH_source}")

def load_source_data():
    BUCKET_NAME = 'knowledge-graph-data'
    FOLDER_NAME = 'kg_gh_subset'
    FILE_NAME = 'source.txt'
    S3_PATH = f"s3://{BUCKET_NAME}/{FOLDER_NAME}/{FILE_NAME}"
    s3 = s3fs.S3FileSystem(anon=False)
    
    with s3.open(S3_PATH, 'r') as file:
        repo_list = [line.strip() for line in file.readlines()]
        logging.info(f"Loaded {len(repo_list)} repositories from {FILE_NAME}")
        return repo_list

def extract_owner_repo(url):
    pattern = r'https:\/\/github\.com\/([^\/]+)\/([^\/]+)'
    match = re.search(pattern, url)
    if match:
        owner = match.group(1)
        repo = match.group(2)
        return owner, repo
    else:
        return None, None

def dump_documents_to_txt(documents, filename="all_documents.txt"):
  """
  Dumps the contents of the `documents` list to a text file.

  Args:
      documents: A list of strings representing the documents to dump.
      filename: The name of the output text file. Defaults to "all_documents.txt".
  """
  with open(filename, 'w') as f:
    f.write(str(documents))
  logging.info(f"Documents dumped to {filename}")

def main():
    #load keys
    openai_api_key, github_token = load_environment_variables()
    set_llms()

    all_repos = load_source_data()
    logging.info(f"Total repositories to process: {len(all_repos)}")
    gh_docs={}
    # Load the GitHub documents for each repo
    for repo in all_repos:
        logging.info(f"Processing repo: {repo}")
        owner, repo = extract_owner_repo(repo)
        if owner and repo:
            gh_docs[repo] = load_github_documents(github_token, owner, repo)
            if gh_docs[repo]:
                logging.info(f"Completed loading documents for repo: {owner}/{repo}, Number of documents: {len(gh_docs[repo])}")
            else:
                logging.warning(f"No documents loaded for repo: {owner}/{repo}")
        else:
            logging.warning(f"Invalid GitHub URL: {repo}")




    # Collapse all the docs into a single list
    documents = []
    for repo in gh_docs.keys():
        if gh_docs[repo] is not None:
            documents.extend(gh_docs[repo])
        else:
            logging.info(f"Document with None value!")


    #dumping the parsed documents
    dump_documents_to_txt(documents)  


    graph_output_directory = 'KG_repo_one_dump.html'
    storage_directory = "KG_repo_one_dump"
      
    logging.info("Creating the triplet extraction template ")

    triplet_template = create_kg_triplet_extraction_template()

    logging.info("Creating the index")
    index = create_knowledge_graph_index(documents, triplet_template)

    logging.info("Testing with a simple query the index")
    query = "Describe the data that are provided in your {{CONTEXT}}"
    response = query_knowledge_graph_index(index, query)
    logging.info(f"Query response: {response}")
    

    visualize_knowledge_graph(index, graph_output_directory)
    persist_knowledge_graph(index)

if __name__ == "__main__":
    main()

