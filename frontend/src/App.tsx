import './App.css'
import { useEffect, useMemo, useState } from 'react'
import type { PreviewResponse } from './api/client'
import { fetchPreview } from './api/client'
import type { KnittingIR } from './ir/types'
import { BlocklyWorkspace } from './components/BlocklyWorkspace'

function App() {
  const [compiled, setCompiled] = useState<KnittingIR | null>(null)
  const [compileErrors, setCompileErrors] = useState<string[]>([])
  const [exportText, setExportText] = useState<string>('')
  const [copyStatus, setCopyStatus] = useState<string>('')
  const [preview, setPreview] = useState<PreviewResponse | null>(null)
  const [previewError, setPreviewError] = useState<string>('')
  const [isPreviewLoading, setIsPreviewLoading] = useState(false)

  const exportDisabled = useMemo(() => compiled === null, [compiled])

  const onExport = () => {
    if (!compiled) return
    setCopyStatus('')
    setExportText(JSON.stringify(compiled, null, 2))
  }

  const onCopy = async () => {
    if (!exportText) return
    try {
      await navigator.clipboard.writeText(exportText)
      setCopyStatus('Copied.')
      window.setTimeout(() => setCopyStatus(''), 1500)
    } catch {
      setCopyStatus('Copy failed (browser permissions).')
    }
  }

  useEffect(() => {
    if (!compiled) return
    if (compileErrors.length > 0) return

    const controller = new AbortController()
    const timeout = window.setTimeout(() => {
      setIsPreviewLoading(true)
      setPreviewError('')
      fetchPreview(compiled, controller.signal)
        .then((data) => setPreview(data))
        .catch((e: unknown) => {
          if (controller.signal.aborted) return
          setPreview(null)
          setPreviewError(e instanceof Error ? e.message : String(e))
        })
        .finally(() => {
          if (!controller.signal.aborted) setIsPreviewLoading(false)
        })
    }, 450)

    return () => {
      controller.abort()
      window.clearTimeout(timeout)
    }
  }, [compiled, compileErrors])

  return (
    <div className="app">
      <header className="header">
        <div className="title">
          <div className="title__name">Knitting Pattern Builder (MVP)</div>
          <div className="title__subtitle">Blockly → IR export</div>
        </div>
        <div className="header__actions">
          <button onClick={onExport} disabled={exportDisabled}>
            Export IR
          </button>
          <button onClick={onCopy} disabled={!exportText}>
            Copy
          </button>
          <span className="copyStatus" aria-live="polite">
            {copyStatus}
          </span>
        </div>
      </header>

      <main className="main">
        <section className="panel panel--workspace" aria-label="Blockly workspace">
          <BlocklyWorkspace
            onCompiled={(result) => {
              setCompiled(result.ir)
              setCompileErrors(result.errors)
            }}
          />
        </section>

        <section className="panel panel--ir" aria-label="IR export">
          <div className="panel__header">
            <div className="panel__title">IR JSON</div>
            <div className="panel__meta">
              {compiled ? `${compiled.charts.length} chart(s)` : 'No IR yet'}
            </div>
          </div>

          {compileErrors.length > 0 ? (
            <div className="errors" role="alert">
              <div className="errors__title">Compile errors</div>
              <ul className="errors__list">
                {compileErrors.map((e) => (
                  <li key={e}>{e}</li>
                ))}
              </ul>
            </div>
          ) : null}

          <pre className="code">{exportText || 'Click “Export IR” to generate JSON.'}</pre>

          <div className="panel__header">
            <div className="panel__title">Preview</div>
            <div className="panel__meta">{isPreviewLoading ? 'Loading…' : preview ? 'Ready' : '—'}</div>
          </div>

          {previewError ? (
            <div className="errors" role="alert">
              <div className="errors__title">Backend error</div>
              <div>{previewError}</div>
            </div>
          ) : null}

          {preview ? (
            <div className="preview">
              {preview.charts.map((c) => (
                <div key={c.chartName} className="preview__chart">
                  <div className="preview__chartHeader">
                    <div className="preview__chartName">{c.chartName}</div>
                    <div className="preview__chartMeta">
                      {c.rows.length} row(s), {c.currentStitchCount} st(s)
                    </div>
                  </div>

                  {c.errors.length > 0 ? (
                    <div className="errors" role="alert">
                      <div className="errors__title">Execution errors</div>
                      <ul className="errors__list">
                        {c.errors.map((e) => (
                          <li key={`${c.chartName}-${e.commandIndex}`}>{`Command ${e.commandIndex}: ${e.message}`}</li>
                        ))}
                      </ul>
                    </div>
                  ) : null}

                  <div className="preview__small">
                    <div className="preview__rowMeta">
                      Markers RS: {c.markers.RS.join(', ') || '—'} | WS: {c.markers.WS.join(', ') || '—'}
                    </div>
                    <div className="preview__rowMeta">Showing first 5 rows (tokens)</div>
                    <ol className="preview__rows">
                      {c.rows.slice(0, 5).map((row, idx) => (
                        <li key={idx}>
                          <code>{row.join(', ')}</code>
                        </li>
                      ))}
                    </ol>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="preview preview--empty">Add a chart + commands to see a preview.</div>
          )}
        </section>
      </main>
    </div>
  )
}

export default App
