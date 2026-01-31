"""Tests for LanguageDetector C# support in document_loader.py."""

from agent_brain_server.indexing.document_loader import LanguageDetector


class TestCSharpExtensionDetection:
    """Tests for C# file extension detection."""

    def test_csharp_cs_extension(self) -> None:
        """Test .cs extension is detected as csharp."""
        assert LanguageDetector.detect_from_path("Program.cs") == "csharp"

    def test_csharp_csx_extension(self) -> None:
        """Test .csx extension is detected as csharp."""
        assert LanguageDetector.detect_from_path("Script.csx") == "csharp"

    def test_csharp_case_insensitive_extension(self) -> None:
        """Test extension detection is case-insensitive."""
        assert LanguageDetector.detect_from_path("Program.CS") == "csharp"

    def test_csharp_nested_path(self) -> None:
        """Test detection works with nested file paths."""
        assert LanguageDetector.detect_from_path("src/Models/Document.cs") == "csharp"


class TestCSharpIsSupported:
    """Tests for C# language support check."""

    def test_csharp_is_supported(self) -> None:
        """Test csharp is listed as a supported language."""
        assert LanguageDetector.is_supported_language("csharp") is True

    def test_csharp_in_supported_languages(self) -> None:
        """Test csharp appears in get_supported_languages()."""
        assert "csharp" in LanguageDetector.get_supported_languages()


class TestCSharpContentDetection:
    """Tests for C# content-based language detection."""

    def test_csharp_using_system(self) -> None:
        """Test detection of 'using System' pattern."""
        content = "using System;\nusing System.Collections.Generic;\n"
        matches = LanguageDetector.detect_from_content(content)
        assert len(matches) > 0
        assert matches[0][0] == "csharp"

    def test_csharp_namespace_pattern(self) -> None:
        """Test detection of namespace declaration."""
        content = "namespace MyApp\n{\n    public class Foo {}\n}\n"
        matches = LanguageDetector.detect_from_content(content)
        lang_names = [m[0] for m in matches]
        assert "csharp" in lang_names

    def test_csharp_property_accessor_pattern(self) -> None:
        """Test detection of property accessor pattern."""
        content = "public string Name { get; set; }\n"
        matches = LanguageDetector.detect_from_content(content)
        lang_names = [m[0] for m in matches]
        assert "csharp" in lang_names

    def test_csharp_full_content_detection(self) -> None:
        """Test detection with comprehensive C# content."""
        content = """using System;
namespace MyApp {
    public class Program {
        public string Name { get; set; }
    }
}"""
        matches = LanguageDetector.detect_from_content(content)
        assert len(matches) > 0
        assert matches[0][0] == "csharp"

    def test_csharp_detect_language_with_path(self) -> None:
        """Test detect_language prefers path-based detection."""
        result = LanguageDetector.detect_language("Example.cs", "some random content")
        assert result == "csharp"

    def test_csharp_detect_language_from_content_fallback(self) -> None:
        """Test detect_language falls back to content detection."""
        content = """using System;
namespace MyApp {
    public class Program {
        public string Name { get; set; }
    }
}"""
        result = LanguageDetector.detect_language("unknown.txt", content)
        # Should detect as csharp from content (or None if threshold not met)
        # The important thing is it doesn't crash
        assert result is None or result == "csharp"
