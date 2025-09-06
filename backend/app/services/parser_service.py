from typing import Optional, List, Dict, Any
from pathlib import Path
import logging

from infrastructure.plugins.plugin_manager import PluginManager

logger = logging.getLogger(__name__)


class ParserService:
    """Service for parsing documents using the plugin system."""
    
    def __init__(self, plugin_manager: PluginManager):
        self.plugin_manager = plugin_manager
    
    async def parse(
        self,
        file_path: str,
        parser_plugin_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Parse a document using the appropriate plugin."""
        
        if parser_plugin_id:
            plugin = self.plugin_manager.get_plugin_instance(parser_plugin_id)
            if not plugin:
                raise ValueError(f"Plugin not found: {parser_plugin_id}")
        else:
            plugin = self.plugin_manager.find_plugin_for_file(file_path)
            if not plugin:
                file_ext = Path(file_path).suffix.lower()
                raise ValueError(f"No parser plugin found for file type: {file_ext}")
        
        logger.info(f"Using plugin {plugin.get_name()} to parse {file_path}")
        
        try:
            parsed_content = await plugin.process(file_path)
            return parsed_content
        except Exception as e:
            logger.error(f"Error parsing file with {plugin.get_name()}: {e}")
            raise
    
    def get_supported_formats(self) -> List[str]:
        """Get list of all supported file formats."""
        formats = set()
        
        for plugin_info in self.plugin_manager.list_available_plugins():
            formats.update(plugin_info["supported_formats"])
        
        return sorted(list(formats))