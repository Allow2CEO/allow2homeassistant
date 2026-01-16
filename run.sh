#!/usr/bin/env bash
# Allow2 Home Assistant Add-on Startup Script
# This script copies the integration to Home Assistant and monitors health

set -e

# Configuration from environment
CONFIG_PATH="/data/options.json"
HA_CONFIG_DIR="/config"
CUSTOM_COMPONENTS_DIR="${HA_CONFIG_DIR}/custom_components"
ALLOW2_SOURCE_DIR="/app/custom_components/allow2"
ALLOW2_DEST_DIR="${CUSTOM_COMPONENTS_DIR}/allow2"

# Logging functions
log_info() {
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo "[WARNING] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Read add-on options
get_option() {
    local key=$1
    local default=$2
    if [ -f "$CONFIG_PATH" ]; then
        local value
        value=$(jq -r ".$key // empty" "$CONFIG_PATH" 2>/dev/null)
        if [ -n "$value" ] && [ "$value" != "null" ]; then
            echo "$value"
            return
        fi
    fi
    echo "$default"
}

# Health check endpoint
start_health_server() {
    log_info "Starting health check server on port 8099..."
    while true; do
        echo -e "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\nOK" | nc -l -p 8099 -q 1 2>/dev/null || true
    done &
    HEALTH_PID=$!
    log_info "Health server started with PID $HEALTH_PID"
}

# Copy integration files to Home Assistant
copy_integration() {
    log_info "Copying Allow2 integration to Home Assistant..."

    # Ensure custom_components directory exists
    if [ ! -d "$CUSTOM_COMPONENTS_DIR" ]; then
        log_info "Creating custom_components directory..."
        mkdir -p "$CUSTOM_COMPONENTS_DIR"
    fi

    # Check if source exists
    if [ ! -d "$ALLOW2_SOURCE_DIR" ]; then
        log_error "Source integration not found at $ALLOW2_SOURCE_DIR"
        return 1
    fi

    # Remove existing installation if present
    if [ -d "$ALLOW2_DEST_DIR" ]; then
        log_info "Removing existing Allow2 installation..."
        rm -rf "$ALLOW2_DEST_DIR"
    fi

    # Copy the integration
    log_info "Installing Allow2 to $ALLOW2_DEST_DIR..."
    cp -r "$ALLOW2_SOURCE_DIR" "$ALLOW2_DEST_DIR"

    # Remove pycache directories
    find "$ALLOW2_DEST_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

    # Set permissions
    chmod -R 755 "$ALLOW2_DEST_DIR"

    # Verify installation
    if [ -f "$ALLOW2_DEST_DIR/__init__.py" ] && [ -f "$ALLOW2_DEST_DIR/manifest.json" ]; then
        log_info "Allow2 integration installed successfully!"
        return 0
    else
        log_error "Integration installation verification failed"
        return 1
    fi
}

# Verify integration installation
verify_installation() {
    log_info "Verifying Allow2 integration installation..."

    local required_files=(
        "__init__.py"
        "manifest.json"
        "config_flow.py"
        "api.py"
        "const.py"
        "sensor.py"
        "binary_sensor.py"
        "strings.json"
    )

    local missing=0
    for file in "${required_files[@]}"; do
        if [ ! -f "$ALLOW2_DEST_DIR/$file" ]; then
            log_warning "Missing file: $file"
            missing=$((missing + 1))
        fi
    done

    if [ $missing -gt 0 ]; then
        log_warning "$missing required files missing"
        return 1
    fi

    log_info "All required files present"
    return 0
}

# Main startup sequence
main() {
    log_info "=========================================="
    log_info "Allow2 Home Assistant Add-on Starting"
    log_info "=========================================="

    # Get configuration options
    LOG_LEVEL=$(get_option "log_level" "info")
    UPDATE_INTERVAL=$(get_option "update_interval" "300")
    COPY_ON_START=$(get_option "copy_on_start" "true")

    log_info "Configuration:"
    log_info "  Log Level: $LOG_LEVEL"
    log_info "  Update Interval: ${UPDATE_INTERVAL}s"
    log_info "  Copy on Start: $COPY_ON_START"

    # Start health check server
    start_health_server

    # Copy integration files if enabled
    if [ "$COPY_ON_START" = "true" ]; then
        if copy_integration; then
            verify_installation
        else
            log_error "Failed to copy integration files"
        fi
    else
        log_info "Skipping integration copy (copy_on_start disabled)"
        if [ -d "$ALLOW2_DEST_DIR" ]; then
            verify_installation
        else
            log_warning "Allow2 integration not found in Home Assistant"
            log_warning "Enable copy_on_start or manually install the integration"
        fi
    fi

    log_info "=========================================="
    log_info "Allow2 Add-on Running"
    log_info "Integration Location: $ALLOW2_DEST_DIR"
    log_info "=========================================="
    log_info ""
    log_info "To use Allow2:"
    log_info "1. Restart Home Assistant to load the integration"
    log_info "2. Go to Settings > Devices & Services"
    log_info "3. Click '+ Add Integration' and search for 'Allow2'"
    log_info "4. Enter your Allow2 credentials to pair"
    log_info ""

    # Keep the container running
    log_info "Monitoring Allow2 integration..."
    while true; do
        # Periodic health check
        if [ ! -d "$ALLOW2_DEST_DIR" ]; then
            log_warning "Allow2 integration directory missing, attempting reinstall..."
            copy_integration || true
        fi

        sleep "$UPDATE_INTERVAL"
    done
}

# Signal handlers
cleanup() {
    log_info "Shutting down Allow2 add-on..."
    if [ -n "$HEALTH_PID" ]; then
        kill "$HEALTH_PID" 2>/dev/null || true
    fi
    exit 0
}

trap cleanup SIGTERM SIGINT SIGHUP

# Run main function
main "$@"
