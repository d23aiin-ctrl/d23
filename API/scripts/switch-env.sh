#!/bin/bash

# ===========================================
# Environment Switcher Script
# ===========================================
# Switches between development, QA, and production environments
# by symlinking .env to the appropriate environment file
#
# Usage: ./switch-env.sh [dev|qa|prod]
# ===========================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Environment files
ENV_FILE="${SCRIPT_DIR}/.env"
ENV_DEV="${SCRIPT_DIR}/.env.dev"
ENV_QA="${SCRIPT_DIR}/.env.qa"
ENV_PROD="${SCRIPT_DIR}/.env.prod"
ENV_EXAMPLE="${SCRIPT_DIR}/.env.example"

# ===========================================
# Functions
# ===========================================

print_header() {
    echo -e "${BLUE}==========================================${NC}"
    echo -e "${BLUE}   Environment Switcher${NC}"
    echo -e "${BLUE}==========================================${NC}"
}

print_usage() {
    echo ""
    echo "Usage: $0 [environment]"
    echo ""
    echo "Environments:"
    echo "  dev, development    - Switch to development environment"
    echo "  qa, staging         - Switch to QA/staging environment"
    echo "  prod, production    - Switch to production environment"
    echo "  status              - Show current environment"
    echo ""
    echo "Examples:"
    echo "  $0 dev              # Switch to development"
    echo "  $0 qa               # Switch to QA"
    echo "  $0 prod             # Switch to production"
    echo "  $0 status           # Show current environment"
    echo ""
}

get_current_env() {
    if [ -L "${ENV_FILE}" ]; then
        # .env is a symlink
        local target=$(readlink "${ENV_FILE}")
        echo "$(basename "${target}")"
    elif [ -f "${ENV_FILE}" ]; then
        # .env is a regular file, check ENVIRONMENT variable inside
        if grep -q "^ENVIRONMENT=" "${ENV_FILE}"; then
            grep "^ENVIRONMENT=" "${ENV_FILE}" | cut -d'=' -f2 | tr -d ' "'
        else
            echo "unknown"
        fi
    else
        echo "none"
    fi
}

show_status() {
    local current_env=$(get_current_env)

    echo ""
    echo -e "${BLUE}Current Environment Status:${NC}"
    echo -e "─────────────────────────────────────────"

    if [ "${current_env}" = "none" ]; then
        echo -e "Status: ${RED}No environment configured${NC}"
        echo -e "File: ${RED}.env not found${NC}"
    else
        echo -e "Environment: ${GREEN}${current_env}${NC}"

        if [ -L "${ENV_FILE}" ]; then
            local target=$(readlink "${ENV_FILE}")
            echo -e "Type: ${GREEN}Symlink${NC}"
            echo -e "Target: ${YELLOW}${target}${NC}"
        else
            echo -e "Type: ${YELLOW}Regular file${NC}"
        fi
    fi

    echo -e "─────────────────────────────────────────"
    echo ""
    echo "Available environment files:"
    [ -f "${ENV_DEV}" ] && echo -e "  ${GREEN}✓${NC} .env.dev (development)" || echo -e "  ${RED}✗${NC} .env.dev (missing)"
    [ -f "${ENV_QA}" ] && echo -e "  ${GREEN}✓${NC} .env.qa (QA/staging)" || echo -e "  ${RED}✗${NC} .env.qa (missing)"
    [ -f "${ENV_PROD}" ] && echo -e "  ${GREEN}✓${NC} .env.prod (production)" || echo -e "  ${RED}✗${NC} .env.prod (missing)"
    echo ""
}

backup_env() {
    if [ -f "${ENV_FILE}" ] && [ ! -L "${ENV_FILE}" ]; then
        local backup_file="${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
        echo -e "${YELLOW}Backing up current .env to ${backup_file}${NC}"
        cp "${ENV_FILE}" "${backup_file}"
    fi
}

switch_environment() {
    local env=$1
    local env_file=""
    local env_name=""

    # Normalize environment name
    case "${env}" in
        dev|development)
            env_file="${ENV_DEV}"
            env_name="development"
            ;;
        qa|staging|stage)
            env_file="${ENV_QA}"
            env_name="qa"
            ;;
        prod|production)
            env_file="${ENV_PROD}"
            env_name="production"
            ;;
        *)
            echo -e "${RED}Error: Invalid environment '${env}'${NC}"
            print_usage
            exit 1
            ;;
    esac

    # Check if environment file exists
    if [ ! -f "${env_file}" ]; then
        echo -e "${RED}Error: Environment file ${env_file} not found!${NC}"
        echo ""
        echo "To create it, copy the example file:"
        echo -e "  ${YELLOW}cp ${ENV_EXAMPLE} $(basename ${env_file})${NC}"
        echo ""
        echo "Then edit it with your credentials for ${env_name}:"
        echo -e "  ${YELLOW}nano $(basename ${env_file})${NC}"
        exit 1
    fi

    # Backup existing .env if it's a regular file
    backup_env

    # Remove existing .env (whether symlink or file)
    if [ -e "${ENV_FILE}" ] || [ -L "${ENV_FILE}" ]; then
        rm "${ENV_FILE}"
    fi

    # Create symlink to the target environment file
    ln -s "$(basename ${env_file})" "${ENV_FILE}"

    # Verify the switch
    if [ -L "${ENV_FILE}" ]; then
        echo -e "${GREEN}✓ Successfully switched to ${env_name} environment${NC}"
        echo -e "  ${BLUE}.env${NC} → ${YELLOW}$(basename ${env_file})${NC}"

        # Set ENVIRONMENT variable in the env file if not present
        if ! grep -q "^ENVIRONMENT=" "${env_file}"; then
            echo "" >> "${env_file}"
            echo "ENVIRONMENT=${env_name}" >> "${env_file}"
            echo -e "${GREEN}✓ Added ENVIRONMENT=${env_name} to ${env_file}${NC}"
        fi

        echo ""
        echo -e "${BLUE}ℹ  Remember to restart your application for changes to take effect!${NC}"
        echo ""
    else
        echo -e "${RED}✗ Failed to create symlink${NC}"
        exit 1
    fi
}

create_missing_files() {
    local missing=()

    [ ! -f "${ENV_DEV}" ] && missing+=("dev")
    [ ! -f "${ENV_QA}" ] && missing+=("qa")
    [ ! -f "${ENV_PROD}" ] && missing+=("prod")

    if [ ${#missing[@]} -gt 0 ]; then
        echo -e "${YELLOW}⚠  Missing environment files detected${NC}"
        echo ""
        echo "The following files are missing:"
        for env in "${missing[@]}"; do
            echo "  - .env.${env}"
        done
        echo ""
        echo "Would you like to create them from .env.example? (y/n)"
        read -r response

        if [[ "$response" =~ ^[Yy]$ ]]; then
            for env in "${missing[@]}"; do
                local target=".env.${env}"
                cp "${ENV_EXAMPLE}" "${target}"
                echo -e "${GREEN}✓ Created ${target}${NC}"
                echo -e "${YELLOW}  → Edit this file with ${env} credentials${NC}"
            done
            echo ""
            echo -e "${GREEN}✓ All missing files created!${NC}"
            echo -e "${BLUE}ℹ  Remember to update each file with the appropriate credentials${NC}"
        fi
    fi
}

# ===========================================
# Main Script
# ===========================================

print_header

# Check if .env.example exists
if [ ! -f "${ENV_EXAMPLE}" ]; then
    echo -e "${RED}Error: .env.example not found!${NC}"
    echo "This file is required as a template for environment files."
    exit 1
fi

# Parse command
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}No environment specified${NC}"
    show_status
    print_usage
    exit 0
fi

case "$1" in
    status|info|show)
        show_status
        ;;
    create|init|setup)
        create_missing_files
        ;;
    dev|development|qa|staging|stage|prod|production)
        switch_environment "$1"
        ;;
    help|-h|--help)
        print_usage
        ;;
    *)
        echo -e "${RED}Error: Unknown command '$1'${NC}"
        print_usage
        exit 1
        ;;
esac

exit 0
