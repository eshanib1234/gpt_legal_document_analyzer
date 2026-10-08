import React, { useState } from 'react';
import Header from './components/Header';
import DocumentInput from './components/DocumentInput';
import AnalysisResult from './components/AnalysisResult';
import RawJsonModal from './components/RawJsonModal';
import { AlertCircle } from 'lucide-react';

const API_BASE_URL = 'http://127.0.0.1:8000';

const SAMPLE_DOCUMENT_TEXT = `EMPLOYMENT AGREEMENT

This Employment Agreement is between ABC Technologies Pvt. Ltd. and John Smith.

The employee will work as a Software Developer.

The employment period is 12 months starting from 01-07-2026.

The employee will receive a monthly salary of ₹50,000.

The employee must maintain confidentiality regarding company information.

The employee must perform assigned duties and follow company policies.

Either party may terminate the agreement by providing 30 days written notice.

Any intellectual property created during employment belongs to the company.

The agreement is governed by the applicable laws of India.`;

export default function App() {
  const [documentText, setDocumentText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStepText, setLoadingStepText] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [metadata, setMetadata] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const [isRawJsonOpen, setIsRawJsonOpen] = useState(false);

  // Load sample agreement
  const handleLoadSample = async () => {
    setErrorMessage(null);
    try {
      const response = await fetch(`${API_BASE_URL}/sample`);
      if (response.ok) {
        const data = await response.json();
        setDocumentText(data.sample_text || SAMPLE_DOCUMENT_TEXT);
      } else {
        setDocumentText(SAMPLE_DOCUMENT_TEXT);
      }
    } catch (err) {
      setDocumentText(SAMPLE_DOCUMENT_TEXT);
    }
  };

  // Clear text and results
  const handleClear = () => {
    setDocumentText('');
    setAnalysis(null);
    setMetadata(null);
    setErrorMessage(null);
  };

  // Run analysis
  const handleAnalyze = async () => {
    if (!documentText.trim()) {
      setErrorMessage('Please paste or upload a legal document before analyzing.');
      return;
    }

    setErrorMessage(null);
    setIsLoading(true);
    setLoadingStepText('Analyzing document with Ollama...');

    try {
      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          document_text: documentText
        })
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        const detail = data.detail || data.error || 'Failed to complete document analysis.';
        setErrorMessage(detail);
        return;
      }

      setAnalysis(data.analysis);
      setMetadata(data.metadata);

    } catch (err) {
      setErrorMessage(
        'Backend connection error: Ensure FastAPI backend is running on http://127.0.0.1:8000 and Ollama is active.'
      );
    } finally {
      setIsLoading(false);
      setLoadingStepText('');
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <Header />

      {/* Error Banner */}
      {errorMessage && (
        <div className="alert-box alert-danger">
          <AlertCircle size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <div className="alert-title">Analysis Error</div>
            <p style={{ color: '#fecdd3' }}>{errorMessage}</p>
          </div>
        </div>
      )}

      {/* Document Input Section */}
      <DocumentInput
        documentText={documentText}
        setDocumentText={setDocumentText}
        onAnalyze={handleAnalyze}
        onLoadSample={handleLoadSample}
        onClear={handleClear}
        isLoading={isLoading}
        loadingStepText={loadingStepText}
      />

      {/* Results Section */}
      <AnalysisResult
        analysis={analysis}
        metadata={metadata}
        onOpenRawJson={() => setIsRawJsonOpen(true)}
      />

      {/* Raw JSON Modal */}
      <RawJsonModal
        isOpen={isRawJsonOpen}
        onClose={() => setIsRawJsonOpen(false)}
        jsonData={analysis}
      />
    </div>
  );
}
