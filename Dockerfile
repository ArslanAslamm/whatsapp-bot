# Use an official Python runtime as a base image
FROM python:3.10.11

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

#libglfw
RUN apt-get update && apt-get install -y libglfw3-dev libgl1-mesa-glx

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt



# Make port 8082 available to the world outside this container
EXPOSE 8082

# Run app.py when the container launches
CMD ["python", "run.py"]