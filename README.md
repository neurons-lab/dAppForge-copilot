# dApp Code Generation

This repository demonstrates the use of a code generation capabilities for blockchain developers. The application uses a Large Language Model for code completion in the Rust programming language and the Substrate framework. Additionally, it is enhanced with a Knowledge Graph and leverages a RAG architecture for improved performance.

## Prerequisites

- Python 3.x
- Pip package manager
- `requirements.txt`
- `.env` file with your necessary access keys
- `.pem` keys for SSH access to the EC2 instance

## EC2 Instance Access

To log into the running EC2 instance, use the `.pem` file containing the keys with the following command:

```bash
ssh -i "<path_to_your_pem_file_keys>.pem" ubuntu@ec2-23-20-247-78.compute-1.amazonaws.com
```

## Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/neurons-lab/dApp-codegen.git
   cd dApp-codegen
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
   OPENAI_API_KEY=<open_ai_key_here>
   GITHUB_TOKEN=<github_token_here>
   ```

## Usage

To start the FastAPI endpoint, run the following commands:

```bash
cd api
uvicorn api.main:app --host 0.0.0.0 --port 8081
```

## Directory Descriptions

### `api`

Contains the FastAPI endpoint. Start it using the command mentioned in the Usage section.

### `common`

1. **`config.py`**: Configurations for setting up the LLM settings and Weights & Biases (wandb).
2. **`inference.py`**: Loads the Knowledge Graph from an S3 bucket and contains the inference function for the LLM for code generation.
3. **`models.py`**: Pydantic models for AnswerFormat and API code responses.
4. **`utils.py`**: Helper functions for the Knowledge Graph.
5. **`config.json`**: Config file containing static variables of AWS S3 information, LLM models, and Wandb infos.

### `code_generation`

#### `kg_construction`

Contains scripts for creating the Knowledge Graph from GitHub repositories and persisting it into an AWS S3 bucket. It also includes scripts for creating the Knowledge Graph from website documentation and loading Knowledge Graphs from the S3 bucket to the local disk.

#### `prompts`

- **`code_completion.prompt`**: Prompt used for code generation to LLM.
- **`kg_triplets_template.prompt`**: Prompt used to create triplets for the Knowledge Graph.
- **`text_qa_template.prompt`**: Prompt template for text QA from Llamaindex.

#### `caching`

Contains all the necessary scripts for implementing the Redis caching mechanism.

### `services`

Directory for managing different services that run on the EC2 instance.

## Additional Files

- **`.env.example`**: Example of the `.env` file that needs to be set up.
- **`.gitignore`**: Specifies files and directories to be ignored by git.
- **`requirements.txt`**: List of Python dependencies required for the project.
