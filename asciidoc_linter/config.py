# config.py - Configuration system for the linter

import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from .rules.base import Severity

class LinterConfig:
    """Configuration handler for the AsciiDoc linter"""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration with optional config file
        
        Args:
            config_file: Optional path to a YAML configuration file
        """
        self.config = self._load_default_config()
        if config_file:
            self._update_config(self._load_config_file(config_file))
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            'rules': {
                'WS001': {'enabled': True, 'severity': 'warning'},
                'HEAD001': {'enabled': True, 'severity': 'error'},
                'HEAD002': {'enabled': True, 'severity': 'error'},
                'HEAD003': {'enabled': True, 'severity': 'error'},
                'BLOCK001': {'enabled': True, 'severity': 'error'},
                'BLOCK002': {'enabled': True, 'severity': 'warning'},
                'IMG001': {'enabled': True, 'severity': 'warning'}
            }
        }
    
    def _load_config_file(self, config_file: Path) -> Dict[str, Any]:
        """
        Load configuration from a YAML file
        
        Args:
            config_file: Path to the YAML configuration file
            
        Returns:
            Dict containing the configuration, or empty dict on error
        """
        try:
            if not config_file.exists():
                print(f"Warning: Config file {config_file} does not exist")
                return {}
                
            with open(config_file) as f:
                config = yaml.safe_load(f)
                return config if config else {}
        except Exception as e:
            print(f"Warning: Could not load config file {config_file}: {e}")
            return {}
            
    def _update_config(self, new_config: Dict[str, Any]) -> None:
        """
        Update configuration with new values, preserving defaults for unspecified values
        
        Args:
            new_config: New configuration to merge with current config
        """
        if 'rules' in new_config:
            for rule_id, rule_config in new_config['rules'].items():
                if rule_id in self.config['rules']:
                    self.config['rules'][rule_id].update(rule_config)
                else:
                    self.config['rules'][rule_id] = rule_config
    
    def is_rule_enabled(self, rule_id: str) -> bool:
        """
        Check if a rule is enabled
        
        Args:
            rule_id: ID of the rule to check
            
        Returns:
            True if the rule is enabled, False otherwise
        """
        return self.config.get('rules', {}).get(rule_id, {}).get('enabled', True)
    
    def get_rule_severity(self, rule_id: str) -> str:
        """
        Get the severity level for a rule
        
        Args:
            rule_id: ID of the rule
            
        Returns:
            Severity level as string ('error' or 'warning')
        """
        return self.config.get('rules', {}).get(rule_id, {}).get('severity', 'warning')
    
    def get_severity_enum(self, rule_id: str) -> Severity:
        """
        Get the severity level for a rule as Severity enum
        
        Args:
            rule_id: ID of the rule
            
        Returns:
            Severity enum value
        """
        severity_str = self.get_rule_severity(rule_id)
        return Severity.ERROR if severity_str.lower() == 'error' else Severity.WARNING