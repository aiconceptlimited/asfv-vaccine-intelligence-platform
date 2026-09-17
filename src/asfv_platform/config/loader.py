#!/usr/bin/env python3
"""
Configuration Loader
Merges modular YAML configuration files
"""

import os
import sys
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

def load_config(config_dir="config", master_file="pipeline.yaml"):
    """Load and merge configuration files"""
    config_path = PROJECT_ROOT / config_dir / master_file
    
    if not config_path.exists():
        raise FileNotFoundError(f"Master config not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Process includes
    if 'include' in config:
        included_files = config.pop('include')
        for include_file in included_files:
            include_path = PROJECT_ROOT / config_dir / include_file
            if include_path.exists():
                with open(include_path, 'r') as f:
                    included_config = yaml.safe_load(f)
                    for key, value in included_config.items():
                        if key in config and isinstance(config[key], dict) and isinstance(value, dict):
                            config[key].update(value)
                        else:
                            config[key] = value
            else:
                print(f"Warning: Included config not found: {include_path}")
    
    return config

def get_config():
    """Convenience function to get configuration"""
    return load_config()
