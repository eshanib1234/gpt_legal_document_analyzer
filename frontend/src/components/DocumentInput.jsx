import React, { useRef } from 'react';
import { 
  FileText, 
  Upload, 
  BookOpen, 
  Trash2, 
  Play, 
  Info
} from 'lucide-react';

export default function DocumentInput({
  documentText,
  setDocumentText,
  onAnalyze,
  onLoadSample,
  onClear,
  isLoading,
  loadingStepText
}) {
  const fileInputRef = useRef(null);

  const charCount = documentText.length;
  const wordCount = documentText.trim() ? documentText.trim().split(/\s+/).length : 0;
  const isChunkNeeded = charCount > 3000;

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.txt')) {
      alert('Please upload a plain text (.txt) file.');
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result;
      if (typeof content === 'string') {
        setDocumentText(content);
      }
    };
    reader.onerror = () => {
      alert('Failed to read the file.');
    };
    reader.readAsText(file);
    e.target.value = '';
  };

  return (
    <div className="glass-card document-input-card">
      <div className="card-header-row">
        <div className="card-title-group">
          <FileText size={22} className="card-title-icon" />
          <h2>Document Input</h2>
        </div>

        {/* Input Action Controls */}
        <div className="input-actions">
          <button
            type="button"
            className="btn btn-sample"
            onClick={onLoadSample}
            disabled={isLoading}
            title="Load Sample Document"
          >
            <BookOpen size={16} />
            <span>Sample Document</span>
          </button>

          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading}
            title="Upload TXT"
          >
            <Upload size={16} />
            <span>Upload TXT</span>
          </button>
          
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".txt"
            style={{ display: 'none' }}
          />

          {documentText && (
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={onClear}
              disabled={isLoading}
              title="Clear Document Text"
            >
              <Trash2 size={15} />
              <span>Clear</span>
            </button>
          )}
        </div>
      </div>

      {/* Textarea */}
      <div className="textarea-wrapper">
        <textarea
          className="legal-textarea"
          placeholder="Paste legal document text here (or click 'Sample Document' above)..."
          value={documentText}
          onChange={(e) => setDocumentText(e.target.value)}
          disabled={isLoading}
        />
        
        <div className="textarea-footer">
          <div className="meta-stats">
            <span><strong>Characters:</strong> {charCount.toLocaleString()}</span>
            <span><strong>Words:</strong> {wordCount.toLocaleString()}</span>
          </div>

          {isChunkNeeded && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#f59e0b' }}>
              <Info size={14} />
              <span>Long document detected: Chunking enabled</span>
            </div>
          )}
        </div>
      </div>

      {/* Action Bar Bottom */}
      <div className="action-bar-bottom">
        <div style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>
          {isLoading ? (
            <span style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#818cf8', fontWeight: 600 }}>
              <span className="spinner" />
              {loadingStepText || 'Analyzing with Ollama...'}
            </span>
          ) : (
            <span>Ready to analyze document.</span>
          )}
        </div>

        <button
          type="button"
          className="btn btn-primary"
          onClick={onAnalyze}
          disabled={isLoading || !documentText.trim()}
          style={{ minWidth: '180px' }}
        >
          {isLoading ? (
            <>
              <span className="spinner" />
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <Play size={18} />
              <span>Analyze Document</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
