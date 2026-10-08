import React from 'react';
import {
  FileText,
  Users,
  Target,
  CheckSquare,
  Shield,
  CreditCard,
  Clock,
  XCircle,
  Lock,
  Calendar,
  Gavel,
  BookOpen,
  AlertTriangle,
  FileCheck2,
  Copy,
  Printer,
  Code2
} from 'lucide-react';

export default function AnalysisResult({
  analysis,
  metadata,
  onOpenRawJson
}) {
  if (!analysis) return null;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(JSON.stringify(analysis, null, 2));
    alert('Analysis JSON copied to clipboard!');
  };

  const handlePrint = () => {
    window.print();
  };

  // Helper to render string or "Not specified"
  const renderString = (val) => {
    if (!val || val === 'Not specified in the document.') {
      return <span className="not-specified">Not specified in the document.</span>;
    }
    return <span>{val}</span>;
  };

  // Helper to render lists
  const renderList = (items, itemClass = '', isDanger = false) => {
    if (!items || !Array.isArray(items) || items.length === 0) {
      return <span className="not-specified">Not specified in the document.</span>;
    }
    if (items.length === 1 && items[0] === 'Not specified in the document.') {
      return <span className="not-specified">Not specified in the document.</span>;
    }

    return (
      <ul className="result-list">
        {items.map((item, idx) => (
          <li key={idx} className={`result-list-item ${itemClass}`}>
            {isDanger ? <AlertTriangle size={15} style={{ color: '#f43f5e', flexShrink: 0, marginTop: '2px' }} /> : null}
            <span>{item}</span>
          </li>
        ))}
      </ul>
    );
  };

  // Helper to render parties as tags
  const renderParties = (parties) => {
    if (!parties || !Array.isArray(parties) || parties.length === 0) {
      return <span className="not-specified">Not specified in the document.</span>;
    }
    if (parties.length === 1 && parties[0] === 'Not specified in the document.') {
      return <span className="not-specified">Not specified in the document.</span>;
    }

    return (
      <div className="tag-cloud">
        {parties.map((p, idx) => (
          <span key={idx} className="party-tag">
            <Users size={13} />
            <span>{p}</span>
          </span>
        ))}
      </div>
    );
  };

  return (
    <div className="glass-card" style={{ marginTop: '28px' }}>
      {/* Results Header */}
      <div className="results-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <FileCheck2 size={24} style={{ color: 'var(--accent-emerald)' }} />
            <h2>Structured Legal Analysis</h2>
          </div>
          <p style={{ fontSize: '0.86rem', marginTop: '4px' }}>
            Extracted strictly using local Llama 3.2 model inference.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button className="btn btn-secondary btn-sm" onClick={onOpenRawJson}>
            <Code2 size={15} />
            <span>View Raw JSON</span>
          </button>
          <button className="btn btn-secondary btn-sm" onClick={copyToClipboard}>
            <Copy size={15} />
            <span>Copy JSON</span>
          </button>
          <button className="btn btn-secondary btn-sm" onClick={handlePrint}>
            <Printer size={15} />
            <span>Print Report</span>
          </button>
        </div>
      </div>

      {/* Summary Hero Card */}
      <div className="summary-hero-card">
        <div className="hero-title">
          <FileText size={18} />
          <span>Executive Document Summary</span>
        </div>
        <div className="hero-body">
          {renderString(analysis.summary)}
        </div>
      </div>

      {/* Grid of Extracted Information Cards */}
      <div className="analysis-grid">
        {/* 1. Document Type */}
        <div className="result-card">
          <div className="result-card-header">
            <span className="result-label highlight-purple">
              <FileText size={16} />
              <span>Document Type</span>
            </span>
            <span className="result-badge">Classification</span>
          </div>
          <div className="result-content" style={{ fontWeight: 600, fontSize: '1rem', color: '#c084fc' }}>
            {renderString(analysis.document_type)}
          </div>
        </div>

        {/* 2. Parties */}
        <div className="result-card">
          <div className="result-card-header">
            <span className="result-label highlight-cyan">
              <Users size={16} />
              <span>Parties Involved</span>
            </span>
            <span className="result-badge">Entities</span>
          </div>
          <div className="result-content">
            {renderParties(analysis.parties)}
          </div>
        </div>

        {/* 3. Purpose */}
        <div className="result-card">
          <div className="result-card-header">
            <span className="result-label highlight-blue">
              <Target size={16} />
              <span>Purpose</span>
            </span>
            <span className="result-badge">Intent</span>
          </div>
          <div className="result-content">
            {renderString(analysis.purpose)}
          </div>
        </div>

        {/* 4. Obligations */}
        <div className="result-card">
          <div className="result-card-header">
            <span className="result-label highlight-amber">
              <CheckSquare size={16} />
              <span>Obligations</span>
            </span>
            <span className="result-badge">Duties</span>
          </div>
          <div className="result-content">
            {renderList(analysis.obligations)}
          </div>
        </div>

        {/* 5. Rights */}
        <div className="result-card">
          <div className="result-card-header">
            <span className="result-label highlight-emerald">
              <Shield size={16} />
              <span>Rights</span>
            </span>
            <span className="result-badge">Entitlements</span>
          </div>
          <div className="result-content">
            {renderList(analysis.rights)}
          </div>
        </div>

        {/* 6. Payment Terms */}
        <div className="result-card">
          <div className="result-card-header">
            <span className="result-label highlight-emerald">
              <CreditCard size={16} />
              <span>Payment Terms</span>
            </span>
            <span className="result-badge">Financials</span>
          </div>
          <div className="result-content">
            {renderString(analysis.payment_terms)}
          </div>
        </div>

        {/* 7. Duration */}
        <div className="result-card">
          <div className="result-card-header">
            <span className="result-label highlight-blue">
              <Clock size={16} />
              <span>Duration / Term</span>
            </span>
            <span className="result-badge">Timeline</span>
          </div>
          <div className="result-content">
            {renderString(analysis.duration)}
          </div>
        </div>

        {/* 8. Termination */}
        <div className="result-card">
          <div className="result-card-header">
            <span className="result-label highlight-rose">
              <XCircle size={16} />
              <span>Termination Conditions</span>
            </span>
            <span className="result-badge">Exit Clause</span>
          </div>
          <div className="result-content">
            {renderString(analysis.termination)}
          </div>
        </div>

        {/* 9. Confidentiality */}
        <div className="result-card">
          <div className="result-card-header">
            <span className="result-label highlight-purple">
              <Lock size={16} />
              <span>Confidentiality</span>
            </span>
            <span className="result-badge">NDA / Secrecy</span>
          </div>
          <div className="result-content">
            {renderString(analysis.confidentiality)}
          </div>
        </div>

        {/* 10. Important Dates */}
        <div className="result-card">
          <div className="result-card-header">
            <span className="result-label highlight-cyan">
              <Calendar size={16} />
              <span>Important Dates</span>
            </span>
            <span className="result-badge">Deadlines</span>
          </div>
          <div className="result-content">
            {renderList(analysis.important_dates)}
          </div>
        </div>

        {/* 11. Governing Law */}
        <div className="result-card">
          <div className="result-card-header">
            <span className="result-label highlight-amber">
              <Gavel size={16} />
              <span>Governing Law</span>
            </span>
            <span className="result-badge">Jurisdiction</span>
          </div>
          <div className="result-content">
            {renderString(analysis.governing_law)}
          </div>
        </div>

        {/* 12. Key Clauses */}
        <div className="result-card">
          <div className="result-card-header">
            <span className="result-label highlight-blue">
              <BookOpen size={16} />
              <span>Key Clauses</span>
            </span>
            <span className="result-badge">Core Provisions</span>
          </div>
          <div className="result-content">
            {renderList(analysis.key_clauses)}
          </div>
        </div>

        {/* 13. Potentially Important / Risk Clauses */}
        <div className="result-card" style={{ borderColor: 'rgba(245, 158, 11, 0.3)' }}>
          <div className="result-card-header">
            <span className="result-label highlight-amber">
              <AlertTriangle size={16} style={{ color: 'var(--accent-amber)' }} />
              <span>Potentially Important Clauses</span>
            </span>
            <span className="result-badge" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fcd34d' }}>
              Special Notice
            </span>
          </div>
          <div className="result-content">
            {renderList(analysis.potentially_important_clauses, 'warn-item', true)}
          </div>
        </div>
      </div>

      {/* Metadata Info Footer */}
      {metadata && (
        <div style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-muted)', flexWrap: 'wrap', gap: '8px' }}>
          <span>Input Size: {metadata.word_count} words ({metadata.character_count} chars)</span>
          <span>Chunking: {metadata.is_chunked ? `Enabled (${metadata.chunk_count} chunks processed)` : 'Single Pass (No chunking required)'}</span>
        </div>
      )}
    </div>
  );
}
