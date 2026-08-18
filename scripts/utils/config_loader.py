#!/usr/bin/env python3
"""
Configuration Loader Utility
Merges modular YAML configuration files into a single config object
Following Section 3.2.2: Configuration file contains all adjustable thresholds
"""

import os
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

def load_config(config_dir="config", master_file="pipeline.yaml"):
    """
    Load master configuration and merge all included YAML files
    
    Args:
        config_dir: Directory containing config files
        master_file: Name of the master config file
        
    Returns:
        dict: Merged configuration
    """
    config_path = PROJECT_ROOT / config_dir / master_file
    
    if not config_path.exists():
        raise FileNotFoundError(f"Master config not found: {config_path}")
    
    # Load master config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Check for includes
    if 'include' in config:
        included_files = config.pop('include')
        for include_file in included_files:
            include_path = PROJECT_ROOT / config_dir / include_file
            if include_path.exists():
                with open(include_path, 'r') as f:
                    included_config = yaml.safe_load(f)
                    # Merge included config
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

if __name__ == "__main__":
    try:
        config = load_config()
        print("Configuration loaded successfully!")
        print(f"Project: {config.get('project', {}).get('name', 'Unknown')}")
        print(f"Genomes: {len(config.get('genomes', []))}")
        print(f"Target Proteins: {len(config.get('target_proteins', []))}")
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)
