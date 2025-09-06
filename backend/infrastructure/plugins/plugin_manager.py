import importlib.util
import sys
from pathlib import Path
from typing import Dict, Optional, List
import logging

from infrastructure.plugins.base_plugin import IDataSourcePlugin

logger = logging.getLogger(__name__)


class PluginManager:
    """Manages the discovery, loading, and lifecycle of plugins."""
    
    def __init__(self, plugins_directory: Optional[Path] = None):
        self.plugins_directory = plugins_directory or Path(__file__).parent.parent.parent / "plugins"
        self.loaded_plugins: Dict[str, IDataSourcePlugin] = {}
        
    def discover_and_load_plugins(self) -> None:
        """Scan the plugins directory and load all valid plugins."""
        if not self.plugins_directory.exists():
            logger.warning(f"Plugins directory not found: {self.plugins_directory}")
            self.plugins_directory.mkdir(parents=True, exist_ok=True)
            return
            
        for plugin_file in self.plugins_directory.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue
                
            try:
                self._load_plugin_module(plugin_file)
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_file.name}: {e}")
    
    def _load_plugin_module(self, plugin_path: Path) -> None:
        """Dynamically load a plugin module from a file path."""
        module_name = f"plugins.{plugin_path.stem}"
        
        spec = importlib.util.spec_from_file_location(module_name, plugin_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load spec for {plugin_path}")
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        logger.info(f"Successfully loaded plugin module: {module_name}")
    
    def get_plugin_instance(self, plugin_name: str) -> Optional[IDataSourcePlugin]:
        """Get or create an instance of a plugin by name."""
        if plugin_name in self.loaded_plugins:
            return self.loaded_plugins[plugin_name]
            
        plugin_class = IDataSourcePlugin.get_plugin(plugin_name)
        if plugin_class:
            instance = plugin_class()
            self.loaded_plugins[plugin_name] = instance
            return instance
            
        return None
    
    def find_plugin_for_file(self, file_path: str) -> Optional[IDataSourcePlugin]:
        """Find and instantiate a plugin that can handle the given file."""
        file_extension = Path(file_path).suffix.lower()
        
        plugin_class = IDataSourcePlugin.find_plugin_for_identifier(file_extension)
        if plugin_class:
            plugin_name = plugin_class.get_name()
            return self.get_plugin_instance(plugin_name)
            
        return None
    
    def list_available_plugins(self) -> List[Dict[str, any]]:
        """List all available plugins with their metadata."""
        plugins_info = []
        
        for name, plugin_class in IDataSourcePlugin.get_all_plugins().items():
            plugins_info.append({
                "name": name,
                "supported_formats": plugin_class.get_supported_identifiers(),
                "loaded": name in self.loaded_plugins,
            })
            
        return plugins_info