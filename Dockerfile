# ===================
# Stage 1: Builder
# ===================
FROM python:3.11-slim AS builder

WORKDIR /app
COPY  ./src /app

# Install build dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ===================
# Stage 2: Final
# ===================
FROM python:3.11-slim AS final

# Create a non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# Copy only necessary runtime files from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages \
                    /usr/local/lib/python3.11/site-packages
COPY ./src /app
# **Key step: ensure the non-root user can write to all .db files**
RUN chown -R appuser:appgroup /app/database_service/database_file/
RUN chmod -R u+rw /app/database_service/database_file/

# Switch to non-root user
USER appuser

EXPOSE 5000

# Set environment variables (can also come from .env)
# ENV FLASK_ENV=production

CMD ["python", "app.py"]
