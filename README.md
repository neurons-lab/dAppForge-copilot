# dApp Code Generation

This repository demonstrates the use of a code generation app, which is served as API endpoint and as Gradio demo app. The application uses Large Language Model for code completion in Rust Programming language and Substrate framework. Further, this app is enhanced with Knwoledge Graph and leverages a RAG system for better performance.


## Prerequisites

- Python 3.x
- Pip package manager
- requirements.txt
- `.env` file with your necessary access keys
- `.pem` keys for SSH access to the EC2 instance

## EC2 instance

You need to have the .pem file that contains the keys for logging into the running instance on ec2. To login you can use the following command:
```bash
ssh -i "<path_to_your_pem_file_keys>.pem" ubuntu@ec2-23-20-247-78.compute-1.amazonaws.com
```


## Setup and Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/neurons-lab/dApp-codegen.git
   cd dApp-codegen
   ```
2. Create and activate a virtual environment:
 ```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```
3.Install the required dependencies:
 ```bash
pip install -r requirements.txt
```
4.Set up the environment variables:
 ```bash
cp .env.example .env
```
The structure of .env file is as follows:
```bash
   WANDB_API_KEY= <your_wandb_key_here>
   AWS_ACCESS_KEY_ID= <aws_access_key_here>
   AWS_SECRET_ACCESS_KEY= <aws_secret_access_key_here>
   OPENAI_API_KEY= <open_ai_key_here>
   GITHUB_TOKEN= <github_token_here>
```

## Usage
Running the API
To start the FastAPI endpoint:
 ```bash
cd api
uvicorn api.main:app --host 0.0.0.0 --port 8081
```

## Running the Demos

Gradio Demo App:
   Navigate to the ```demos/gradio_app``` directory and follow the instructions in the README file within that directory.

Streamlit Demo App:
  Navigate to the ```demos/streamlit_app ``` directory and follow the instructions in the README file within that directory.

## Directory Descriptions
### api
Contains the FastAPI endpoint. It can be started using the following command:
### common
   -  ``` 1. config.py: ``` Configurations for setting up the LLM settings and Weights & Biases (wandb).
   - ``` 2. inference.py: ``` Loads the Knowledge Graph from an S3 bucket and contains the inference function for the LLM for code generation.
   - ``` 3. models.py:``` Pydantic models for AnswerFormat and API code responses.
   - ``` 4. utils.py: ``` Helper functions for the Knowledge Graph.
   - ``` 5. config.json: ``` Config file that contains static variables of AWS S3 information, LLM models and Wandb infos.

### code_generation
#### kg_construction:
   It contains the necessart ccript for creating the Knowledge Graph from GitHub repositories and persisting the file into an AWS S3 bucket.
   Also it has the script for creating Knwoledge Graph from website documentations. Inside the directory, you can also find the script for loading knowledge graphs from s3 bucket and persisting them into local disk.
##### notebooks/: 
   Jupyter notebooks for different Knowledge Graph creations.
```substrate_kg_creation.ipynb ```:
   Notebook for creating the Knowledge Graph from all Substrate documentation.

#### prompts:
```code_completion.prompt:``` Prompt used for code generation to LLM.
```kg_triplets_template.prompt``` Prompt used to create triplets for Knowledge Graph.
```text_qa_template.prompt``` Prompt template for text QA from Llamaindex.

#### caching
Here you find all the necessary scripts for implementation of Redis caching mechanism.

## demos
   #### gradio_app:
   New version of the demo app for code completion, sub-plotting of the Knowledge Graph, and full Knowledge Graph plotting features.
   #### streamlit_app: 
   First version of the demo app, that contains predefined examples for testing code completion and has different input options.

## experiments
Folder containing various Jupyter notebooks and scripts used for different development purposes.

## services
Directory for managing different services that run on the EC2 instance.

## .env.example
Example of the ``` .env ``` file that needs to be set up.

## .gitignore
Specifies files and directories to be ignored by git.

## requirements.txt
List of Python dependencies required for the project.
