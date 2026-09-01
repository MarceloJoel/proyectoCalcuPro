import React, { useEffect, useRef } from 'react';
import katex from 'katex';
import 'katex/dist/katex.min.css';

export default function KatexMath({ math, displayMode = false, className = '' }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (containerRef.current && math) {
      try {
        katex.render(math, containerRef.current, {
          displayMode: displayMode,
          throwOnError: false,
          output: 'htmlAndMathml',
        });
      } catch (err) {
        console.error("KaTeX rendering error:", err);
        if (containerRef.current) {
          containerRef.current.innerText = math;
        }
      }
    }
  }, [math, displayMode]);

  return <span ref={containerRef} className={`katex-container ${className}`} />;
}
