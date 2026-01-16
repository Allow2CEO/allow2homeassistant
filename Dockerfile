# Allow2 Home Assistant Add-on
# Multi-architecture Dockerfile
# Supports: armhf, armv7, aarch64, amd64, i386

ARG BUILD_FROM
FROM ${BUILD_FROM}

# Build arguments
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_REF
ARG BUILD_VERSION
ARG BUILD_REPOSITORY
ARG BUILD_DESCRIPTION

# Environment configuration
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apk add --no-cache \
    bash \
    ca-certificates \
    curl \
    tzdata \
    && rm -rf /var/cache/apk/*

# Install Python dependencies
RUN pip3 install --no-cache-dir \
    aiohttp>=3.8.0 \
    aiofiles>=23.0.0

# Create directories
RUN mkdir -p /app/custom_components/allow2 \
    && mkdir -p /data

# Copy custom_components
COPY custom_components/allow2/ /app/custom_components/allow2/

# Copy run script
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

# Set working directory
WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -sf http://localhost:8099/health || exit 1

# Labels
LABEL \
    io.hass.name="Allow2" \
    io.hass.description="${BUILD_DESCRIPTION}" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version="${BUILD_VERSION}" \
    org.opencontainers.image.title="Allow2 for Home Assistant" \
    org.opencontainers.image.description="Parental controls integration with Allow2 service" \
    org.opencontainers.image.vendor="Allow2" \
    org.opencontainers.image.authors="Allow2 <support@allow2.com>" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.url="https://github.com/Allow2/allow2homeassistant" \
    org.opencontainers.image.source="https://github.com/Allow2/allow2homeassistant" \
    org.opencontainers.image.documentation="https://github.com/Allow2/allow2homeassistant/blob/main/README.md" \
    org.opencontainers.image.created="${BUILD_DATE}" \
    org.opencontainers.image.revision="${BUILD_REF}" \
    org.opencontainers.image.version="${BUILD_VERSION}"

# Run the startup script
CMD ["/app/run.sh"]
