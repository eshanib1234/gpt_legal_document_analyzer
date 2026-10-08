import React from 'react';
import { Scale } from 'lucide-react';

export default function Header() {
  return (
    <header className="header-bar">
      <div className="header-top">
        <div className="brand-section">
          <div className="brand-icon-box">
            <Scale size={26} />
          </div>
          <div>
            <h1 className="brand-title">Automated Legal Document Analyzer</h1>
            <p className="brand-subtitle">
              Automated contract analysis and information extraction using local LLM
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}
