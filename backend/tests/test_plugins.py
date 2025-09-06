import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import sys

from infrastructure.plugins.base_plugin import IDataSourcePlugin
from infrastructure.plugins.plugin_manager import PluginManager


class TestPluginBase:
    def test_plugin_registration(self):
        # Clear registry first
        IDataSourcePlugin._registry.clear()
        
        class TestPlugin(IDataSourcePlugin):
            @staticmethod
            def get_name() -> str:
                return "test_plugin"
            
            @staticmethod
            def get_supported_identifiers():
                return [".test"]
            
            async def process(self, source_path: str):
                return [{"text_content": "test"}]
        
        # Plugin should be automatically registered
        assert "test_plugin" in IDataSourcePlugin._registry
        assert IDataSourcePlugin.get_plugin("test_plugin") == TestPlugin
    
    def test_get_all_plugins(self):
        IDataSourcePlugin._registry.clear()
        
        class Plugin1(IDataSourcePlugin):
            @staticmethod
            def get_name() -> str:
                return "plugin1"
            
            @staticmethod
            def get_supported_identifiers():
                return [".p1"]
            
            async def process(self, source_path: str):
                return []
        
        class Plugin2(IDataSourcePlugin):
            @staticmethod
            def get_name() -> str:
                return "plugin2"
            
            @staticmethod
            def get_supported_identifiers():
                return [".p2"]
            
            async def process(self, source_path: str):
                return []
        
        all_plugins = IDataSourcePlugin.get_all_plugins()
        assert len(all_plugins) == 2
        assert "plugin1" in all_plugins
        assert "plugin2" in all_plugins
    
    def test_find_plugin_for_identifier(self):
        IDataSourcePlugin._registry.clear()
        
        class PDFPlugin(IDataSourcePlugin):
            @staticmethod
            def get_name() -> str:
                return "pdf_plugin"
            
            @staticmethod
            def get_supported_identifiers():
                return [".pdf"]
            
            async def process(self, source_path: str):
                return []
        
        found_plugin = IDataSourcePlugin.find_plugin_for_identifier(".pdf")
        assert found_plugin == PDFPlugin
        
        not_found = IDataSourcePlugin.find_plugin_for_identifier(".unknown")
        assert not_found is None


class TestPluginManager:
    @pytest.fixture
    def temp_plugin_dir(self, tmp_path):
        plugin_dir = tmp_path / "plugins"
        plugin_dir.mkdir()
        return plugin_dir
    
    def test_initialization(self, temp_plugin_dir):
        manager = PluginManager(temp_plugin_dir)
        
        assert manager.plugins_directory == temp_plugin_dir
        assert manager.loaded_plugins == {}
    
    def test_discover_plugins_empty_directory(self, temp_plugin_dir):
        manager = PluginManager(temp_plugin_dir)
        
        manager.discover_and_load_plugins()
        
        assert len(manager.loaded_plugins) == 0
    
    def test_discover_and_load_plugin(self, temp_plugin_dir):
        # Create a test plugin file
        plugin_content = '''
from infrastructure.plugins.base_plugin import IDataSourcePlugin

class TestFilePlugin(IDataSourcePlugin):
    @staticmethod
    def get_name():
        return "test_file_plugin"
    
    @staticmethod
    def get_supported_identifiers():
        return [".test"]
    
    async def process(self, source_path):
        return [{"text_content": "processed"}]
'''
        plugin_file = temp_plugin_dir / "test_plugin.py"
        plugin_file.write_text(plugin_content)
        
        manager = PluginManager(temp_plugin_dir)
        
        with patch('infrastructure.plugins.plugin_manager.importlib.util.spec_from_file_location') as mock_spec:
            with patch('infrastructure.plugins.plugin_manager.importlib.util.module_from_spec') as mock_module:
                mock_spec_obj = Mock()
                mock_spec_obj.loader = Mock()
                mock_spec.return_value = mock_spec_obj
                
                manager.discover_and_load_plugins()
                
                assert mock_spec.called
                assert mock_module.called
    
    def test_get_plugin_instance(self, temp_plugin_dir):
        IDataSourcePlugin._registry.clear()
        
        class MockPlugin(IDataSourcePlugin):
            @staticmethod
            def get_name():
                return "mock_plugin"
            
            @staticmethod
            def get_supported_identifiers():
                return [".mock"]
            
            async def process(self, source_path):
                return []
        
        manager = PluginManager(temp_plugin_dir)
        
        instance = manager.get_plugin_instance("mock_plugin")
        assert isinstance(instance, MockPlugin)
        assert manager.loaded_plugins["mock_plugin"] == instance
        
        # Getting again should return the same instance
        instance2 = manager.get_plugin_instance("mock_plugin")
        assert instance is instance2
    
    def test_find_plugin_for_file(self, temp_plugin_dir):
        IDataSourcePlugin._registry.clear()
        
        class PDFPlugin(IDataSourcePlugin):
            @staticmethod
            def get_name():
                return "pdf_plugin"
            
            @staticmethod
            def get_supported_identifiers():
                return [".pdf"]
            
            async def process(self, source_path):
                return []
        
        manager = PluginManager(temp_plugin_dir)
        
        plugin = manager.find_plugin_for_file("/test/document.pdf")
        assert isinstance(plugin, PDFPlugin)
        
        no_plugin = manager.find_plugin_for_file("/test/file.unknown")
        assert no_plugin is None
    
    def test_list_available_plugins(self, temp_plugin_dir):
        IDataSourcePlugin._registry.clear()
        
        class Plugin1(IDataSourcePlugin):
            @staticmethod
            def get_name():
                return "plugin1"
            
            @staticmethod
            def get_supported_identifiers():
                return [".p1", ".p1x"]
            
            async def process(self, source_path):
                return []
        
        class Plugin2(IDataSourcePlugin):
            @staticmethod
            def get_name():
                return "plugin2"
            
            @staticmethod
            def get_supported_identifiers():
                return [".p2"]
            
            async def process(self, source_path):
                return []
        
        manager = PluginManager(temp_plugin_dir)
        manager.get_plugin_instance("plugin1")  # Load one plugin
        
        plugins_list = manager.list_available_plugins()
        
        assert len(plugins_list) == 2
        
        plugin1_info = next(p for p in plugins_list if p["name"] == "plugin1")
        assert plugin1_info["supported_formats"] == [".p1", ".p1x"]
        assert plugin1_info["loaded"] is True
        
        plugin2_info = next(p for p in plugins_list if p["name"] == "plugin2")
        assert plugin2_info["supported_formats"] == [".p2"]
        assert plugin2_info["loaded"] is False


class TestPDFPlugin:
    @pytest.mark.asyncio
    async def test_pdf_plugin_process(self):
        with patch('fitz.open') as mock_fitz_open:
            # Import here to avoid issues if PyMuPDF isn't installed
            from plugins.pdf_pymupdf_plugin import PDFPyMuPDFPlugin
            
            mock_pdf = Mock()
            mock_page = Mock()
            mock_page.get_text.return_value = "Page content"
            mock_pdf.__len__.return_value = 2
            mock_pdf.__getitem__.return_value = mock_page
            mock_pdf.__enter__.return_value = mock_pdf
            mock_pdf.__exit__.return_value = None
            mock_fitz_open.return_value = mock_pdf
            
            plugin = PDFPyMuPDFPlugin()
            
            with patch('pathlib.Path.exists', return_value=True):
                result = await plugin.process("/test/document.pdf")
            
            assert len(result) == 2
            assert result[0]["text_content"] == "Page content"
            assert result[0]["metadata"]["page_number"] == 1
            assert result[0]["metadata"]["source_file"] == "document.pdf"
    
    @pytest.mark.asyncio
    async def test_pdf_plugin_file_not_found(self):
        from plugins.pdf_pymupdf_plugin import PDFPyMuPDFPlugin
        
        plugin = PDFPyMuPDFPlugin()
        
        with pytest.raises(FileNotFoundError):
            await plugin.process("/nonexistent/file.pdf")


class TestDOCXPlugin:
    @pytest.mark.asyncio
    async def test_docx_plugin_process(self):
        with patch('docx.Document') as mock_docx:
            from plugins.docx_textract_plugin import DOCXTextractPlugin
            
            mock_doc = Mock()
            mock_paragraph1 = Mock()
            mock_paragraph1.text = "Paragraph 1"
            mock_paragraph2 = Mock()
            mock_paragraph2.text = "Paragraph 2"
            mock_doc.paragraphs = [mock_paragraph1, mock_paragraph2]
            mock_doc.tables = []
            mock_docx.return_value = mock_doc
            
            plugin = DOCXTextractPlugin()
            
            with patch('pathlib.Path.exists', return_value=True):
                result = await plugin.process("/test/document.docx")
            
            assert len(result) == 1
            assert "Paragraph 1" in result[0]["text_content"]
            assert "Paragraph 2" in result[0]["text_content"]
    
    @pytest.mark.asyncio
    async def test_docx_plugin_with_tables(self):
        with patch('docx.Document') as mock_docx:
            from plugins.docx_textract_plugin import DOCXTextractPlugin
            
            mock_doc = Mock()
            mock_doc.paragraphs = []
            
            # Create mock table
            mock_table = Mock()
            mock_cell1 = Mock()
            mock_cell1.text = "Cell 1"
            mock_cell2 = Mock()
            mock_cell2.text = "Cell 2"
            mock_row = Mock()
            mock_row.cells = [mock_cell1, mock_cell2]
            mock_table.rows = [mock_row]
            mock_doc.tables = [mock_table]
            
            mock_docx.return_value = mock_doc
            
            plugin = DOCXTextractPlugin()
            
            with patch('pathlib.Path.exists', return_value=True):
                result = await plugin.process("/test/document.docx")
            
            assert len(result) == 1
            assert "Cell 1 | Cell 2" in result[0]["text_content"]
            assert result[0]["metadata"]["content_type"] == "table"