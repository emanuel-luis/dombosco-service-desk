FROM python:3.11-slim
USER root

# Set the working directory environment variable
ARG WORK_DIR=/app/project/
ENV WORK_DIR=$WORK_DIR
ARG BACKEND_HOST=0.0.0.0
ENV BACKEND_HOST=$BACKEND_HOST

SHELL ["/bin/bash", "-c"]

# Install system dependencies
RUN echo "deb http://deb.debian.org/debian bullseye main" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y git --no-install-recommends; \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN echo "source /usr/share/bash-completion/completions/git" >> ~/.bashrc

# Set up working directory
RUN mkdir -p $WORK_DIR
WORKDIR $WORK_DIR

# Copy the project files to the working directory
COPY . .

# Install Poetry
RUN pip install -r requirements.txt --no-cache-dir

RUN git config --global --add safe.directory $WORK_DIR

# Expose the port the app runs on
EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "${BACKEND_HOST}:8000"]