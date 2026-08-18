#!/usr/bin/env python3
"""
Adapter registry for tool adapters.
"""

from typing import Dict, Type
from .base import BaseAdapter
from ..enums import ToolName


class AdapterRegistry:
    """Registry for tool adapters."""

    _registry: Dict[ToolName, Type[BaseAdapter]] = {}

    @classmethod
    def register(cls, tool_name: ToolName, adapter_class: Type[BaseAdapter]) -> None:
        """Register an adapter for a tool."""
        cls._registry[tool_name] = adapter_class

    @classmethod
    def get_adapter(cls, tool_name: ToolName) -> BaseAdapter:
        """Get an adapter instance for a tool."""
        if tool_name not in cls._registry:
            raise ValueError(f"No adapter registered for: {tool_name}")
        return cls._registry[tool_name]()

    @classmethod
    def list_adapters(cls) -> list:
        """List all registered tool names."""
        return list(cls._registry.keys())
