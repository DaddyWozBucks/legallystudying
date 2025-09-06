from fastapi import APIRouter, Request
from typing import List

router = APIRouter()


@router.get("/")
async def list_plugins(request: Request):
    """List all available plugins."""
    
    plugins = request.app.state.plugin_manager.list_available_plugins()
    
    return {
        "plugins": plugins,
        "total": len(plugins),
        "supported_formats": request.app.state.parser_service.get_supported_formats(),
    }


@router.get("/{plugin_name}")
async def get_plugin_info(request: Request, plugin_name: str):
    """Get information about a specific plugin."""
    
    plugins = request.app.state.plugin_manager.list_available_plugins()
    
    for plugin in plugins:
        if plugin["name"] == plugin_name:
            return plugin
    
    return {"error": f"Plugin not found: {plugin_name}"}