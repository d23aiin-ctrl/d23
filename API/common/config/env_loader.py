"""
Environment Configuration Loader

Dynamically loads the appropriate .env file based on the ENVIRONMENT variable.
Supports: development, qa, production
"""

import os
import sys
from pathlib import Path
from typing import Optional, Literal
from dotenv import load_dotenv

EnvType = Literal["development", "qa", "production"]


class EnvironmentLoader:
    """Handles loading of environment-specific configuration files."""

    VALID_ENVIRONMENTS = ["development", "qa", "production"]
    ENV_ALIASES = {
        "dev": "development",
        "develop": "development",
        "staging": "qa",
        "stage": "qa",
        "prod": "production",
    }

    def __init__(self):
        """Initialize the environment loader."""
        self.project_root = self._find_project_root()
        self.current_env: Optional[EnvType] = None
        self.env_file_path: Optional[Path] = None

    def _find_project_root(self) -> Path:
        """Find the project root directory (where .env files are located)."""
        current = Path(__file__).resolve()

        # Search up the directory tree for .env.example or main.py
        for parent in [current] + list(current.parents):
            if (parent / ".env.example").exists() or (parent / "main.py").exists():
                return parent

        # Fallback: assume 2 levels up from this file
        return current.parent.parent.parent

    def _normalize_env_name(self, env: str) -> str:
        """Normalize environment name using aliases."""
        env_lower = env.lower().strip()
        return self.ENV_ALIASES.get(env_lower, env_lower)

    def _validate_environment(self, env: str) -> bool:
        """Check if environment name is valid."""
        normalized = self._normalize_env_name(env)
        return normalized in self.VALID_ENVIRONMENTS

    def detect_environment(self) -> EnvType:
        """
        Detect which environment to use.

        Priority order:
        1. ENVIRONMENT environment variable
        2. Check if .env exists (load it to get ENVIRONMENT)
        3. Default to 'development'
        """
        # Check environment variable first
        env = os.getenv("ENVIRONMENT", "").strip()

        if env:
            normalized = self._normalize_env_name(env)
            if self._validate_environment(env):
                return normalized  # type: ignore
            else:
                print(f"⚠️  Warning: Invalid ENVIRONMENT '{env}'. Must be one of: {', '.join(self.VALID_ENVIRONMENTS)}")

        # Try to load from .env file if it exists
        default_env_path = self.project_root / ".env"
        if default_env_path.exists():
            load_dotenv(default_env_path)
            env = os.getenv("ENVIRONMENT", "").strip()
            if env:
                normalized = self._normalize_env_name(env)
                if self._validate_environment(env):
                    return normalized  # type: ignore

        # Default to development
        return "development"

    def get_env_file_path(self, env: EnvType) -> Path:
        """Get the path to the environment-specific .env file."""
        env_file_map = {
            "development": ".env.dev",
            "qa": ".env.qa",
            "production": ".env.prod",
        }

        file_name = env_file_map[env]
        return self.project_root / file_name

    def load_environment(self, env: Optional[str] = None, override: bool = True) -> EnvType:
        """
        Load environment configuration.

        Args:
            env: Environment name (development, qa, production). If None, auto-detect.
            override: Whether to override existing environment variables

        Returns:
            The loaded environment name

        Raises:
            FileNotFoundError: If the environment file doesn't exist
            ValueError: If invalid environment name provided
        """
        # Detect or validate environment
        if env is None:
            detected_env = self.detect_environment()
        else:
            normalized = self._normalize_env_name(env)
            if not self._validate_environment(env):
                raise ValueError(
                    f"Invalid environment '{env}'. Must be one of: {', '.join(self.VALID_ENVIRONMENTS)}"
                )
            detected_env = normalized  # type: ignore

        # Get environment file path
        env_file = self.get_env_file_path(detected_env)

        # Check if file exists
        if not env_file.exists():
            # Fallback to default .env
            fallback_env_file = self.project_root / ".env"
            if fallback_env_file.exists():
                print(f"⚠️  Warning: {env_file.name} not found, using .env instead")
                env_file = fallback_env_file
            else:
                raise FileNotFoundError(
                    f"Environment file not found: {env_file}\n"
                    f"Please create it by copying .env.example:\n"
                    f"  cp .env.example {env_file.name}"
                )

        # Load the environment file
        load_dotenv(env_file, override=override)

        # Store current configuration
        self.current_env = detected_env
        self.env_file_path = env_file

        # Set ENVIRONMENT variable
        os.environ["ENVIRONMENT"] = detected_env

        return detected_env

    def print_environment_info(self):
        """Print information about the loaded environment."""
        if self.current_env and self.env_file_path:
            print(f"\n{'='*60}")
            print(f"🌍 Environment: {self.current_env.upper()}")
            print(f"📄 Config file: {self.env_file_path.name}")
            print(f"📂 Location: {self.env_file_path.parent}")
            print(f"{'='*60}\n")
        else:
            print("⚠️  No environment loaded yet. Call load_environment() first.")

    def get_current_environment(self) -> Optional[EnvType]:
        """Get the currently loaded environment."""
        return self.current_env

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.current_env == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.current_env == "development"

    def is_qa(self) -> bool:
        """Check if running in QA environment."""
        return self.current_env == "qa"


# Global environment loader instance
_env_loader: Optional[EnvironmentLoader] = None


def get_env_loader() -> EnvironmentLoader:
    """Get or create the global environment loader instance."""
    global _env_loader
    if _env_loader is None:
        _env_loader = EnvironmentLoader()
    return _env_loader


def load_environment(env: Optional[str] = None, override: bool = True, verbose: bool = True) -> EnvType:
    """
    Convenience function to load environment configuration.

    Args:
        env: Environment name (development, qa, production). If None, auto-detect.
        override: Whether to override existing environment variables
        verbose: Whether to print environment info

    Returns:
        The loaded environment name

    Example:
        >>> load_environment("production")
        'production'

        >>> load_environment()  # Auto-detect from ENVIRONMENT variable
        'development'
    """
    loader = get_env_loader()
    loaded_env = loader.load_environment(env, override)

    if verbose:
        loader.print_environment_info()

    return loaded_env


def get_current_environment() -> Optional[EnvType]:
    """Get the currently loaded environment name."""
    loader = get_env_loader()
    return loader.get_current_environment()


def is_production() -> bool:
    """Check if running in production environment."""
    loader = get_env_loader()
    return loader.is_production()


def is_development() -> bool:
    """Check if running in development environment."""
    loader = get_env_loader()
    return loader.is_development()


def is_qa() -> bool:
    """Check if running in QA/staging environment."""
    loader = get_env_loader()
    return loader.is_qa()


# Auto-load environment on import (can be disabled by setting SKIP_AUTO_LOAD_ENV=1)
if not os.getenv("SKIP_AUTO_LOAD_ENV"):
    try:
        load_environment(verbose=False)
    except Exception as e:
        print(f"⚠️  Warning: Could not auto-load environment: {e}")
        print("   This is normal if you haven't set up environment files yet.")
