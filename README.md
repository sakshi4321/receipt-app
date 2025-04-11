### Build and Run the Docker Container

To build the Docker image, open your terminal in the project directory (where the Dockerfile is located) and run:

```
docker build -t my-django-app .
```
```
docker run -it --rm -p 8000:8000 my-django-app
```

curl_requirements.py contains curl commands for the sample receipts