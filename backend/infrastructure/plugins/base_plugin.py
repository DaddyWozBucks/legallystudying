from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class IDataSourcePlugin(ABC):
    """
    Abstract base class for all data source plugins.
    
    Each plugin is responsible for processing a specific type of data source
    (e.g., a file type, a web URL, an API connection) and breaking it down
    into processable text chunks.
    """
    
    _registry: Dict[str, type["IDataSourcePlugin"]] = {}
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        plugin_name = cls.get_name()
        if plugin_name and plugin_name != "base":
            IDataSourcePlugin._registry[plugin_name] = cls

    @staticmethod
    @abstractmethod
    def get_name() -> str:
        """
        Returns the unique, machine-readable name of the plugin.
        e.g., 'pdf_pymupdf_parser', 'docx_textract_parser'
        """
        pass

    @staticmethod
    @abstractmethod
    def get_supported_identifiers() -> List[str]:
        """
        Returns a list of identifiers this plugin can handle.
        For file-based plugins, this would be file extensions (e.g., ['.pdf']).
        For web-based plugins, this could be domain names (e.g., ['en.wikipedia.org']).
        """
        pass

    @abstractmethod
    async def process(self, source_path: str) -> List[Dict[str, Any]]:
        """
        Processes a given data source and returns a list of data chunks.
        
        Args:
            source_path: The path to the data source (e.g., a local file path, a URL).
            
        Returns:
            A list of dictionaries, where each dictionary represents a single
            text chunk. Each dictionary must contain at least a 'text_content'
            key with the chunk's text, and can contain an optional 'metadata' key
            with additional information (e.g., page_number).
        """
        pass

    @classmethod
    def get_plugin(cls, name: str) -> type["IDataSourcePlugin"]:
        """Get a registered plugin by name."""
        return cls._registry.get(name)
    
    @classmethod
    def get_all_plugins(cls) -> Dict[str, type["IDataSourcePlugin"]]:
        """Get all registered plugins."""
        return cls._registry.copy()
    
    @classmethod
    def find_plugin_for_identifier(cls, identifier: str) -> Optional[type["IDataSourcePlugin"]]:
        """Find a plugin that supports the given identifier."""
        for plugin_class in cls._registry.values():
            if identifier in plugin_class.get_supported_identifiers():
                return plugin_class
        return None