# Time-Capsule Flask app, packaged to run on AWS Lambda via the AWS Lambda Web
# Adapter (LWA). LWA is a Lambda extension that translates Function URL / API GW
# events into plain HTTP requests to a normal web server (gunicorn) on $PORT,
# so the Flask app runs unchanged. The same image also runs locally / on ECS.
FROM python:3.11-slim

WORKDIR /app

# AWS Lambda Web Adapter extension (pinned). Free, adds no per-request cost.
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.8.4 /lambda-adapter /opt/extensions/lambda-adapter

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . /app

# LWA serves the app on this port and holds traffic until the readiness path is
# healthy (the app's existing /_meta route returns 200).
ENV PORT=8080
ENV AWS_LWA_READINESS_CHECK_PATH=/_meta

# One worker per container (Lambda handles one request per instance; scale via
# concurrency/memory, not workers). Timeout aligns with the Lambda timeout.
CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "1", "--timeout", "30", "routes:app"]
