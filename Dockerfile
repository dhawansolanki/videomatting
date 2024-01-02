# Use an official PyTorch image with CUDA support as a parent image
FROM python:3.10-bullseye

# Set the working directory in the container
WORKDIR /usr/src/app

# Install necessary Python packages specified in requirements.txt
# Notice that you may need to list torch and any other required packages
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD [ "python", "./app.py" ]