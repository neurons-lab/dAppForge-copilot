import os
import sys
import s3fs
import bcrypt
import asyncio
import logging
from fastapi import status
from fastapi.responses import StreamingResponse
from concurrent.futures import ProcessPoolExecutor
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials


# MODULE IMPORTS
from common.config import start_wandb_run
from common.models import CodeRequest, CodeResponse
from common.inference import claude_inference,claude_inference_streaming
from api.utils import check_and_trim_code_length, prepare_response, load_users_from_yaml
from caching.redis_cache import generate_cache_key, get_cached_result, set_cache_result

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


PERSIST_DIR = '/home/ubuntu/dApp/knowledge_graph_data/'

app = FastAPI()
start_wandb_run()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()

# Load users from YAML file
users = load_users_from_yaml('users.yaml')


# Initialize S3 filesystem
s3 = s3fs.S3FileSystem(anon=False)

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    hashed_password = users.get(credentials.username)
    if not hashed_password or not bcrypt.checkpw(credentials.password.encode('utf-8'), hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

async def async_generate_cache_key(prefix_code: str) -> str:
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor() as pool:
        return await loop.run_in_executor(pool, generate_cache_key, prefix_code)

async def async_get_cached_result(cache_key: str):
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor() as pool:
        return await loop.run_in_executor(pool, get_cached_result, cache_key)

async def async_set_cache_result(cache_key: str, result: dict):
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor() as pool:
        await loop.run_in_executor(pool, set_cache_result, cache_key, result)


@app.post("/v1/generate_stream_code")
async def generate_code(request: CodeRequest, username: str = Depends(authenticate)):
    """
    Generates code based on a defined prefix and streams the generated code as it is created.

    Args:
        request (CodeRequest): Request containing the prefix code for code generation.
        username (str): Authenticated username, provided by the dependency injection.

    Returns:
        StreamingResponse: A streaming response that outputs the generated code in real-time, with a media type of "text/event-stream".
        
    Examples:
        Request:
        ```
        {
            "prefix_code": "///The two components of a block are the header and the extrinsic. \\n pub struct Block<Header, Extrinsic> {"
        }
        ```

        Response:
        ```
        {
            "generated_code": "{ pub extrinsics: Vec<Extrinsic>}",
            "kg_context": [
                "('Parachain-template-1001.rs', 'Written in', 'Rust programming language')",
                "('Ink!', 'Enable', 'Write webassembly-based smart contracts using rust')",
                "['Substrate', 'Allows building', 'Application-specific blockchains']",
                "('Ink!', 'Is', 'Rust smart contract language for substrate chains')",
                "['Rust', 'Required for', 'Compiling node']",
                "['Rust', 'Logging api', 'Debug macros']"
            ],
            "subgraph_plot": "<iframe>< /iframe>"
        }
        ```
    """
    return StreamingResponse(
        claude_inference_streaming(request.prefix_code),
        media_type="text/event-stream")


@app.post("/v1/generate_code", response_model=CodeResponse)
async def generate_code(request: CodeRequest, username: str = Depends(authenticate)):
    """
    Generate code based on the provided prefix code. This endpoint receives a prefix code and returns the generated code completion,
    knowledge graph edges, and optionally a subgraph plot.

        Args:
            request (CodeRequest): A request containing the prefix code and a subgraph plot.

        Returns:
            CodeResponse: A response containing the generated code, knowledge graph edges, and subgraph plot.

        Raises:
            HTTPException: If an error occurs during code generation.

        Examples:
            Request:
            ```
            {
                "prefix_code": "///The two components of a block are the header and the extrinsic. \\n pub struct Block<Header, Extrinsic> {"
            }
            ```

            Response:
            ```
            {
                "generated_code": "{ pub extrinsics: Vec<Extrinsic>}",
                "kg_context": [
                    "('Parachain-template-1001.rs', 'Written in', 'Rust programming language')",
                    "('Ink!', 'Enable', 'Write webassembly-based smart contracts using rust')",
                    "['Substrate', 'Allows building', 'Application-specific blockchains']",
                    "('Ink!', 'Is', 'Rust smart contract language for substrate chains')",
                    "['Rust', 'Required for', 'Compiling node']",
                    "['Rust', 'Logging api', 'Debug macros']"
                ],
                "subgraph_plot": "<iframe>< /iframe>"
            }
            ```
    """
    prefix_code = check_and_trim_code_length(request.prefix_code)
               
    cache_key = await async_generate_cache_key(prefix_code)
    cached_result = await async_get_cached_result(cache_key)
    
    if cached_result:
        return CodeResponse(**cached_result)

    generated_code, sub_edges, subplot = claude_inference(prefix_code)    
    response = prepare_response(generated_code, sub_edges, subplot)
    
    await async_set_cache_result(cache_key, response.dict())
    
    return response

@app.get("/")
async def root():
    """
    Root endpoint that welcomes users to the API.

    Returns:
        dict: A welcome message.
    """
    return {"message": "Welcome to the dApp KG+LLM API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081, loop="asyncio", workers = 4)
