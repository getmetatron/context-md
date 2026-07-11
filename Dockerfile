# Artifact image for "The Repository Context Layer" (paper Section 11).
# Tier 1 (default): reproduce every paper number from the committed run data.
#   docker build -t rcl-artifact . && docker run --rm rcl-artifact
# Tier 2/3 (episodes/evaluation) additionally need Docker + model access;
# see ARTIFACT.md.
FROM python:3.12-slim
WORKDIR /artifact
COPY requirements-artifact.txt .
RUN pip install --no-cache-dir -r requirements-artifact.txt
COPY data/ data/
COPY harness/ harness/
COPY analysis/ analysis/
COPY runs/ runs/
COPY seeds/ seeds/
COPY PREREGISTRATION.md ARTIFACT.md ./
CMD ["python", "analysis/reproduce_paper.py"]
