FROM gdscyber/cyber-security-concourse-base-image
WORKDIR /usr/src/app

# Install python deps
COPY requirements-dev.txt .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONDONTWRITEBYTECODE=1

COPY . .
