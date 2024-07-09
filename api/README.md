## API endpoints

## Running the app
```bash
    uvicorn app:app --host 0.0.0.0 --port 8081 --loop asyncio
```

### "/v1/generate_code"
```bash
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
```
### "/v1/generate_stream_code"
```bash
Generates code based on a defined prefix and streams the generated code as it is created.

Args:
request (CodeRequest): Request containing the prefix code for code generation.
username (str): Authenticated username, provided by the dependency injection.
Returns: StreamingResponse: A streaming response that outputs the generated code in real-time, with a media type of "text/event-stream".
```
### "/v1/create_kg"
```bash
Create a Knowledge Graph (KG) from provided URLs.

Args:
request (KGCreationRequest): Request containing URLs and optional KG name.
Returns: dict: A message and the S3 directory where the KG data is stored.
```
### "//v1/merge_kg"
```bash
Merge two or more existing Knowledge Graphs (KGs) from S3 based on their names and persist the merged KG to S3.

Args:
request (MergeKGRequest): Request containing the names of the KGs to be merged and the prefix code for the merged KG.
username (str): The username of the authenticated user (injected by the authenticate dependency).
Returns: CodeResponse: A response containing the generated code, knowledge graph edges, and subgraph plot.
```
### "/"
```bash
Root endpoint that welcomes users to the API.

Returns: dict: A welcome message.
```
