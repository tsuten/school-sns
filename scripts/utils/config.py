#!/usr/bin/env python3
"""
Configuration management utilities for SNS-for-U22 startup scripts.
Handles loading, parsing, and validation of configuration files.
"""

import os
import sys
import configparser
from pathlib import Path
from typing import Dict, Any, Optional, Union
import json


class ConfigManager:
    """Manages configuration loading and validation for startup scripts."""
    
    def __init__(self, base_path: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            base_path: Base path for the project (defaults to current working directory)
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.config_dir = self.base_path / "scripts" / "config"
        self.config = {}
        self.env_config = {}
        
    def load_default_config(self) -> Dict[str, Any]:
        """Load default configuration from default.conf file.
        
        Returns:
            Dictionary containing default configuration values
            
        Raises:
            FileNotFoundError: If default.conf file is not found
            configparser.Error: If configuration file is malformed
        """
        default_conf_path = self.config_dir / "default.conf"
        
        if not default_conf_path.exists():
            raise FileNotFoundError(f"Default configuration file not found: {default_conf_path}")
        
        parser = configparser.ConfigParser()
        try:
            parser.read(default_conf_path)
            
            # Convert ConfigParser to dictionary
            config = {}
            for section_name in parser.sections():
                config[section_name] = {}
                for key, value in parser.items(section_name):
                    # Try to convert values to appropriate types
                    config[section_name][key] = self._convert_value(value)
                    
            self.config = config
            return config
            
        except configparser.Error as e:
            raise configparser.Error(f"Error parsing default configuration: {e}")
    
    def load_env_config(self, environment: str = "dev") -> Dict[str, str]:
        """Load environment-specific configuration from .env file.
        
        Args:
            environment: Environment name (dev, prod, test)
            
        Returns:
            Dictionary containing environment variables
            
        Raises:
            FileNotFoundError: If environment file is not found
        """
        env_file_path = self.config_dir / f"{environment}.env"
        
        if not env_file_path.exists():
            raise FileNotFoundError(f"Environment file not found: {env_file_path}")
        
        env_config = {}
        try:
            with open(env_file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse key=value pairs
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        env_config[key] = value
                    else:
                        print(f"Warning: Invalid line {line_num} in {env_file_path}: {line}")
            
            self.env_config = env_config
            return env_config
            
        except Exception as e:
            raise Exception(f"Error reading environment file {env_file_path}: {e}")
    
    def get_config_value(self, key: str, section: str = None, default: Any = None) -> Any:
        """Get configuration value with fallback to defaults.
        
        Args:
            key: Configuration key name
            section: Configuration section (for default.conf)
            default: Default value if key is not found
            
        Returns:
            Configuration value
        """
        # First check environment variables
        env_key = key.upper()
        if env_key in self.env_config:
            return self._convert_value(self.env_config[env_key])
        
        # Then check default configuration
        if section and section in self.config and key in self.config[section]:
            return self.config[section][key]
        
        # Finally return default
        return default
    
    def validate_config(self) -> Dict[str, list]:
        """Validate current configuration.
        
        Returns:
            Dictionary with 'errors' and 'warnings' lists
        """
        errors = []
        warnings = []
        
        # Validate required paths
        required_paths = [
            ('FRONTEND_PATH', 'frontend_default'),
            ('BACKEND_PATH', 'backend_default'),
            ('REQUIREMENTS_FILE', 'requirements_default')
        ]
        
        for env_key, default_key in required_paths:
            path_value = self.get_config_value(env_key.lower(), 'paths', None)
            if path_value:
                full_path = self.base_path / path_value
                if not full_path.exists():
                    errors.append(f"Path does not exist: {full_path}")
        
        # Validate port numbers
        ports_to_check = [
            ('DJANGO_PORT', 'django_default'),
            ('SVELTEKIT_PORT', 'sveltekit_dev_default')
        ]
        
        for env_key, default_key in ports_to_check:
            port = self.get_config_value(env_key.lower(), 'ports', None)
            if port:
                try:
                    port_num = int(port)
                    if not (1024 <= port_num <= 65535):
                        warnings.append(f"Port {port_num} is outside recommended range (1024-65535)")
                except ValueError:
                    errors.append(f"Invalid port number: {port}")
        
        # Validate version requirements
        python_version = self.get_config_value('python_min_version', 'dependencies', '3.8')
        node_version = self.get_config_value('node_min_version', 'dependencies', '16.0')
        
        try:
            python_parts = [int(x) for x in python_version.split('.')]
            if len(python_parts) < 2:
                errors.append(f"Invalid Python version format: {python_version}")
        except ValueError:
            errors.append(f"Invalid Python version: {python_version}")
        
        try:
            node_parts = [int(x) for x in node_version.split('.')]
            if len(node_parts) < 1:
                errors.append(f"Invalid Node.js version format: {node_version}")
        except ValueError:
            errors.append(f"Invalid Node.js version: {node_version}")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _convert_value(self, value: str) -> Union[str, int, float, bool]:
        """Convert string value to appropriate Python type.
        
        Args:
            value: String value to convert
            
        Returns:
            Converted value
        """
        if not isinstance(value, str):
            return value
        
        # Boolean conversion
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        elif value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # Numeric conversion
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def get_merged_config(self, environment: str = "dev") -> Dict[str, Any]:
        """Get merged configuration from all sources.
        
        Args:
            environment: Environment name
            
        Returns:
            Merged configuration dictionary
        """
        # Load configurations
        self.load_default_config()
        self.load_env_config(environment)
        
        # Create merged config
        merged = {
            'django_port': self.get_config_value('django_port', 'ports', 8000),
            'sveltekit_port': self.get_config_value('sveltekit_port', 'ports', 5173),
            'venv_path': self.get_config_value('venv_path', 'paths', '.venv'),
            'frontend_path': self.get_config_value('frontend_path', 'paths', 'web-frontend/app'),
            'backend_path': self.get_config_value('backend_path', 'paths', 'sns'),
            'requirements_file': self.get_config_value('requirements_file', 'paths', 'requirements.txt'),
            'python_min_version': self.get_config_value('python_min_version', 'dependencies', '3.8'),
            'node_min_version': self.get_config_value('node_min_version', 'dependencies', '16.0'),
            'log_level': self.get_config_value('log_level', 'logging', 'INFO'),
            'log_file': self.get_config_value('log_file', 'logging', 'scripts/logs/startup.log'),
            'auto_migrate': self.get_config_value('auto_migrate', 'database', True),
            'backup_before_reset': self.get_config_value('backup_before_reset', 'database', True),
        }
        
        return merged
    
    def create_directories(self) -> None:
        """Create necessary directories for the project."""
        directories = [
            self.base_path / "scripts" / "logs",
            self.base_path / "scripts" / "backups",
            self.base_path / "scripts" / "db",
            self.base_path / "scripts" / "utils"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {directory}")


def main():
    """Main function for testing configuration management."""
    config_manager = ConfigManager()
    
    try:
        # Test configuration loading
        print("Loading default configuration...")
        default_config = config_manager.load_default_config()
        print(f"Loaded {len(default_config)} configuration sections")
        
        print("\nLoading development environment...")
        env_config = config_manager.load_env_config("dev")
        print(f"Loaded {len(env_config)} environment variables")
        
        print("\nValidating configuration...")
        validation = config_manager.validate_config()
        
        if validation['errors']:
            print("Configuration errors:")
            for error in validation['errors']:
                print(f"  - {error}")
        
        if validation['warnings']:
            print("Configuration warnings:")
            for warning in validation['warnings']:
                print(f"  - {warning}")
        
        if not validation['errors'] and not validation['warnings']:
            print("Configuration validation passed!")
        
        print("\nMerged configuration:")
        merged = config_manager.get_merged_config()
        for key, value in merged.items():
            print(f"  {key}: {value}")
        
        print("\nCreating directories...")
        config_manager.create_directories()
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()