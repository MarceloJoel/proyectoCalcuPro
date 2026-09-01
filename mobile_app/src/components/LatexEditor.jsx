import React, { useState } from 'react';
import KatexMath from './KatexMath';
import { ArrowLeft, Check, Edit2, Play, Sparkles } from 'lucide-react';

export default function LatexEditor({ imagePreview, initialLatex, onSolve, onBack, isLoading }) {
  const [latex, setLatex] = useState(initialLatex || '');
  const [variable, setVariable] = useState('x');

  const symbolShortcuts = [
    { label: 'd/dx', insert: 'diff(x^2, x)' },
    { label: '∫ dx', insert: 'int(x^2, x)' },
    { label: '∇f', insert: 'grad(x^2*y + z)' },
    { label: '∇×F (Rot)', insert: 'curl(y, -x, z)' },
    { label: '∇·F (Div)', insert: 'div(x, y, z)' },
    { label: 'x²', insert: '^2' },
    { label: '√x', insert: 'sqrt(x)' },
    { label: 'sin(x)', insert: 'sin(x)' },
  ];

  const handleInsertSymbol = (text) => {
    setLatex((prev) => prev + (prev && !prev.endsWith(' ') ? ' ' : '') + text);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!latex.trim()) return;
    onSolve(latex.trim(), variable);
  };

  return (
    <div className="latex-editor-container">
      {/* Top Header */}
      <header className="editor-header">
        <button className="back-btn" onClick={onBack} disabled={isLoading}>
          <ArrowLeft size={20} />
          <span>Volver a Cámara</span>
        </button>
        <span className="editor-title">Revisar Ecuación</span>
      </header>

      {/* Captured Image Preview */}
      {imagePreview && (
        <div className="captured-image-box">
          <img src={imagePreview} alt="Captura matemática" className="captured-thumbnail" />
        </div>
      )}

      {/* KaTeX Live Render Box */}
      <div className="math-preview-card">
        <span className="card-label">Expresión Detectada:</span>
        <div className="katex-render-area">
          {latex.trim() ? (
            <KatexMath math={latex} displayMode={true} />
          ) : (
            <span className="placeholder-text">Escribe o escanea una expresión matemática...</span>
          )}
        </div>
      </div>

      {/* Symbol Shortcut Chips */}
      <div className="shortcuts-row">
        {symbolShortcuts.map((sym, idx) => (
          <button
            key={idx}
            className="symbol-chip"
            onClick={() => handleInsertSymbol(sym.insert)}
            type="button"
          >
            {sym.label}
          </button>
        ))}
      </div>

      {/* Latex Input Form */}
      <form onSubmit={handleSubmit} className="editor-form">
        <div className="input-group">
          <label htmlFor="latex-input">Editar código / expresión:</label>
          <div className="input-with-icon">
            <textarea
              id="latex-input"
              value={latex}
              onChange={(e) => setLatex(e.target.value)}
              placeholder="Ejemplo: 3*x^2 + 5*x - 2 = 0 ó curl(y, -x, z)"
              rows={3}
              className="latex-textarea"
            />
            <Edit2 className="input-icon" size={18} />
          </div>
        </div>

        <div className="variable-selector-row">
          <label htmlFor="var-select">Variable principal:</label>
          <select
            id="var-select"
            value={variable}
            onChange={(e) => setVariable(e.target.value)}
            className="variable-select"
          >
            <option value="x">x</option>
            <option value="y">y</option>
            <option value="z">z</option>
            <option value="t">t</option>
          </select>
        </div>

        <button
          type="submit"
          className="solve-submit-btn"
          disabled={isLoading || !latex.trim()}
        >
          {isLoading ? (
            <>
              <div className="spinner" />
              <span>Resolviendo con SymPy...</span>
            </>
          ) : (
            <>
              <Sparkles size={20} />
              <span>Resolver Paso a Paso</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}
