# dAppForge Copilot

This repository demonstrates the use of a code generation capabilities for blockchain developers. The application uses a Large Language Model for code completion in the Rust programming language and the Substrate framework. Additionally, it is enhanced with a Knowledge Graph and leverages a RAG architecture for improved performance.

# Architecture 
<img width="7792" alt="dAPP" src="https://github.com/neurons-lab/dAppForge-copilot/assets/5167126/5c3e1ad3-1737-48b7-971a-534a46c54f77">

## Prerequisites

- Python 3.x
- Pip package manager
- `requirements.txt`
- `.env` file with your necessary access keys
- `.pem` keys for SSH access to the EC2 instance

## EC2 Instance Access

To log into the running EC2 instance, use the `.pem` file containing the keys with the following command:

```bash
ssh -i "<path_to_your_pem_file_keys>.pem" ubuntu@xxx-xx-xxx-xxx-xxx.compute-x.amazonaws.com
```

## Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/neurons-lab/dAppForge-copilot.git
   cd dAppForge-copilot
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```
3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up the environment variables:**
   ```bash
   cp .env.example .env
   ```
   Structure your `.env` file as follows:
   ```bash
   WANDB_API_KEY=<your_wandb_key_here>
   AWS_ACCESS_KEY_ID=<aws_access_key_here>
   AWS_SECRET_ACCESS_KEY=<aws_secret_access_key_here>
   GITHUB_TOKEN=<github_token_here>
   ```

## Usage

To start the FastAPI endpoint, run the following commands:

```bash
cd api
uvicorn api.main:app --host 0.0.0.0 --port 8081
```

## Directory Descriptions
```
├── api : Contains the FastAPI endpoint. Start it using the command mentioned in the Usage section. 
├── common
│   ├── config.py : Configurations for setting up the LLM settings and Weights & Biases (wandb)
│   ├── inference.py : Loads the Knowledge Graph from an S3 bucket and contains the inference function for the LLM for code generation.
│   ├── models.py : Pydantic models for AnswerFormat and API code responses.
│   ├── utils.py : Helper functions for the Knowledge Graph.
│   └── config.json : Config file containing static variables of AWS S3 information, LLM models, and Wandb infos.
├── code_generation : Creating the Knowledge Graph from GitHub repositories and websites.
│   ├── kg_construction 
│   │   ├── create_kg_from_github.py
│   │   ├── create_kg_from_docs.py
│   │   └── load_kg_from_s3.py
│   ├── prompts : Prompt used for code generation
│   │   ├── code_completion.prompt
│   │   ├── kg_triplets_template.prompt
│   │   └── text_qa_template.prompt
│   └── caching : Contains all the necessary scripts for implementing the Redis caching mechanism.
│       └── redis_caching.py
├── services : Directory for managing different services that run on the EC2 instance.
│   └── service_manager.py
├── .env.example :Example of the `.env` file that needs to be set up.
├── .gitignore :Specifies files and directories to be ignored by git.
└── requirements.txt : List of Python dependencies required for the project.
```
