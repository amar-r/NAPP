# 1. Use an official Python runtime as a parent image
FROM python:3.13-slim

# 2. Set the working directory in the container
WORKDIR /app

# 3. Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the application's code
COPY ./app /app/app

# 5. Make port 8000 available to the world outside this container
EXPOSE 8000

# 6. Run the app when the container launches
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 