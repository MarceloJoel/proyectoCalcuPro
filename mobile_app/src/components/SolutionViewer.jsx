import React, { useEffect } from 'react';
import KatexMath from './KatexMath';
import confetti from 'canvas-confetti';
import { ArrowLeft, CheckCircle2, ChevronRight, Layers, Sparkles, RefreshCw } from 'lucide-react';

export default function SolutionViewer({ solutionData, onReset }) {
  useEffect(() => {
    // Trigger celebratory confetti on successful solution load
    confetti({
      particleCount: 50,
      spread: 60,
      origin: { y: 0.6 }
    });
  }, []);

  if (!solutionData) return null;

  const { problem_type, original_expression_latex, result_latex, steps } = solutionData;

  return (
    <div className="solution-viewer-container">
      {/* Top Header */}
      <header className="solution-header">
        <button className="back-btn" onClick={onReset}>
          <ArrowLeft size={20} />
          <span>Escanear Otro</span>
        </button>
        <div className="status-badge">
          <CheckCircle2 size={16} />
          <span>Resuelto Exitosamente</span>
        </div>
      </header>

      {/* Problem Type Card */}
      <div className="problem-type-card">
        <div className="type-meta">
          <Layers size={18} />
          <span>{problem_type || 'Problema Matemático'}</span>
        </div>

        {original_expression_latex && (
          <div className="original-expr">
            <span className="expr-label">Problema original:</span>
            <div className="math-display">
              <KatexMath math={original_expression_latex} displayMode={true} />
            </div>
          </div>
        )}
      </div>

      {/* Highlighted Final Result Box */}
      <div className="final-result-card">
        <div className="result-header">
          <Sparkles size={20} />
          <span>Resultado Final</span>
        </div>
        <div className="result-math">
          <KatexMath math={result_latex} displayMode={true} />
        </div>
      </div>

      {/* Step-by-Step Explanation List */}
      <div className="steps-section">
        <h3 className="steps-heading">
          Pasos de la Resolución ({steps ? steps.length : 0})
        </h3>

        <div className="steps-timeline">
          {steps && steps.map((step, idx) => (
            <div key={idx} className="step-card">
              <div className="step-number-badge">
                <span>{idx + 1}</span>
              </div>
              <div className="step-content">
                <h4 className="step-title">{step.title}</h4>
                {step.description && (
                  <p className="step-description">{step.description}</p>
                )}
                {step.latex && (
                  <div className="step-math">
                    <KatexMath math={step.latex} displayMode={true} />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Action Footer */}
      <div className="solution-footer">
        <button className="primary-action-btn" onClick={onReset}>
          <RefreshCw size={20} />
          <span>Resolver Nuevo Ejercicio</span>
        </button>
      </div>
    </div>
  );
}
