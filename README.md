# dots.ocr API Server

This project is a lightweight REST API server built using FastAPI that receives binary data from a file(pdf/image),
converts it to Markdown format using the [dots_ocr](https://github.com/rednote-hilab/dots.ocr) library, and returns the
Markdown content.

## Setup Instructions

1. Download Model Weights

https://github.com/rednote-hilab/dots.ocr#download-model-weights

2. Clone the repository:

   ```bash
   git clone https://github.com/Valdanitooooo/dots.ocr_fastapi.git
   ```

3. Navigate to the project directory:

   ```bash
   cd dots.ocr_fastapi
   ```

4. Run the vllm docker container

Change the volumes configuration in `docker_vllm.yml`

   ```bash
   docker compose -f docker_vllm.yml up -d
   ```

5. Build the api server docker image

   ```bash
   docker build -t dots_ocr-api:latest .
   ```

6. Run the api server docker container

   ```bash
   docker compose up -d
   ```

## Endpoints

The API offers two main endpoints:

### `/docs`

Provides an interactive documentation interface where you can:

- Read and explore the existing API endpoints
- View request/response schemas and examples

### `/parse`

Accepts a POST request containing a file to convert to markdown.

- **Method**: POST
- **Content-Type**: multipart/form-data
- **Parameter**: file (binary)
- **Accepted file types**: .pdf .jpg .jpeg .png .gif .bmp
- **Returns**: The string of the converted markdown content

For more information regarding valid file types, check the
official [dots.ocr](https://github.com/rednote-hilab/dots.ocr) project.

## Testing the application

You can quickly test that the application is running by uploading a file via `curl`, like so:

```sh
curl -X POST -F "file=@path/to/mypdf.pdf" http://localhost:8491/parse
```

The result should be a string like:

```
"Your content written in markdown..."
```

Here's a very simple example in Python:

```py
import requests

file_path = "/path/to/my.pdf"
with open(file_path, 'rb') as file:
    files = {'file': (file_path, file)}
    response = requests.post("http://localhost:8491/parse", files=files)
    print(response.text)

```

