using System;
using System.Collections.Generic;
using System.Linq;

namespace DocServe.Models
{
    /// <summary>
    /// Represents a document that can be indexed and searched.
    /// </summary>
    public interface IDocument
    {
        /// <summary>Gets the unique identifier of the document.</summary>
        string Id { get; }

        /// <summary>Gets the title of the document.</summary>
        string Title { get; }

        /// <summary>Returns the content of the document as plain text.</summary>
        string GetContent();
    }

    /// <summary>
    /// Represents the type of a document in the system.
    /// </summary>
    public enum DocumentType
    {
        PlainText,
        Markdown,
        SourceCode,
        Pdf
    }

    /// <summary>
    /// Represents a 2D position in the document.
    /// </summary>
    public struct Position
    {
        public int Line { get; set; }
        public int Column { get; set; }

        public Position(int line, int column)
        {
            Line = line;
            Column = column;
        }

        public override string ToString()
        {
            return $"({Line}, {Column})";
        }
    }

    /// <summary>
    /// Immutable record representing document metadata.
    /// </summary>
    public record DocumentMetadata(
        string Author,
        DateTime CreatedAt,
        IReadOnlyList<string> Tags
    );

    /// <summary>
    /// A searchable document with full-text indexing support.
    /// </summary>
    [Serializable]
    public class SearchableDocument : IDocument
    {
        private readonly List<string> _chunks;

        /// <summary>Gets or sets the unique identifier.</summary>
        public string Id { get; set; }

        /// <summary>Gets or sets the document title.</summary>
        public string Title { get; set; }

        /// <summary>Gets or sets the raw content of the document.</summary>
        public string Content { get; set; }

        /// <summary>Gets or sets the document type.</summary>
        public DocumentType Type { get; set; }

        public DocumentMetadata? Metadata { get; set; }

        public int ChunkCount => _chunks.Count;

        /// <summary>
        /// Initializes a new SearchableDocument.
        /// </summary>
        public SearchableDocument(string id, string title, string content)
        {
            Id = id;
            Title = title;
            Content = content;
            Type = DocumentType.PlainText;
            _chunks = new List<string>();
        }

        /// <summary>Returns the content of the document.</summary>
        public string GetContent()
        {
            return Content;
        }

        /// <summary>Splits the document content into chunks for indexing.</summary>
        public List<string> ChunkContent(int chunkSize)
        {
            _chunks.Clear();
            if (string.IsNullOrEmpty(Content))
            {
                return _chunks;
            }
            for (int i = 0; i < Content.Length; i += chunkSize)
            {
                int length = Math.Min(chunkSize, Content.Length - i);
                _chunks.Add(Content.Substring(i, length));
            }
            return new List<string>(_chunks);
        }

        /// <summary>Searches for a query string within the document content.</summary>
        public bool Search(string query, bool caseSensitive = false)
        {
            if (string.IsNullOrEmpty(query))
            {
                return false;
            }
            var comparison = caseSensitive
                ? StringComparison.Ordinal
                : StringComparison.OrdinalIgnoreCase;
            return Content.Contains(query, comparison);
        }

        public override string ToString()
        {
            return $"Document[{Id}]: {Title} ({Type}, {Content.Length} chars)";
        }
    }
}