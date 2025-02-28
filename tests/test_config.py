# test_config.py - Tests for the configuration system

import pytest
from pathlib import Path
from asciidoc_linter.config import LinterConfig
from asciidoc_linter.rules.base import Severity

def test_default_config():
    """Test that default configuration is loaded correctly"""
    config = LinterConfig()
    
    # Test default rule states
    assert config.is_rule_enabled('WS001')
    assert config.is_rule_enabled('HEAD001')
    assert config.is_rule_enabled('HEAD002')
    assert config.is_rule_enabled('HEAD003')
    assert config.is_rule_enabled('BLOCK001')
    assert config.is_rule_enabled('BLOCK002')
    assert config.is_rule_enabled('IMG001')
    
    # Test default severities
    assert config.get_rule_severity('WS001') == 'warning'
    assert config.get_rule_severity('HEAD001') == 'error'
    assert config.get_rule_severity('HEAD002') == 'error'

def test_config_file_loading(tmp_path):
    """Test loading configuration from a file"""
    config_content = """
    rules:
      WS001:
        enabled: false
        severity: error
      HEAD001:
        enabled: true
        severity: warning
    """
    config_file = tmp_path / ".asciidoc-lint.yml"
    config_file.write_text(config_content)
    
    config = LinterConfig(config_file)
    
    # Test overridden values
    assert not config.is_rule_enabled('WS001')
    assert config.get_rule_severity('WS001') == 'error'
    assert config.is_rule_enabled('HEAD001')
    assert config.get_rule_severity('HEAD001') == 'warning'
    
    # Test that non-overridden values keep defaults
    assert config.is_rule_enabled('HEAD002')
    assert config.get_rule_severity('HEAD002') == 'error'

def test_invalid_config_file():
    """Test handling of invalid configuration file"""
    config = LinterConfig(Path('nonexistent.yml'))
    
    # Should fall back to defaults
    assert config.is_rule_enabled('WS001')
    assert config.get_rule_severity('WS001') == 'warning'

def test_invalid_yaml_content(tmp_path):
    """Test handling of invalid YAML content"""
    config_content = """
    rules:
      WS001: invalid: yaml: content
    """
    config_file = tmp_path / ".asciidoc-lint.yml"
    config_file.write_text(config_content)
    
    config = LinterConfig(config_file)
    
    # Should fall back to defaults
    assert config.is_rule_enabled('WS001')
    assert config.get_rule_severity('WS001') == 'warning'

def test_empty_config_file(tmp_path):
    """Test handling of empty configuration file"""
    config_file = tmp_path / ".asciidoc-lint.yml"
    config_file.write_text("")
    
    config = LinterConfig(config_file)
    
    # Should use defaults
    assert config.is_rule_enabled('WS001')
    assert config.get_rule_severity('WS001') == 'warning'

def test_partial_rule_config(tmp_path):
    """Test handling of partial rule configuration"""
    config_content = """
    rules:
      WS001:
        enabled: false
    """
    config_file = tmp_path / ".asciidoc-lint.yml"
    config_file.write_text(config_content)
    
    config = LinterConfig(config_file)
    
    # Test that specified values are used
    assert not config.is_rule_enabled('WS001')
    # Test that unspecified values use defaults
    assert config.get_rule_severity('WS001') == 'warning'