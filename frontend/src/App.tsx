import './App.css'
import { useEffect, useState } from 'react'
import type { PreviewResponse } from './api/client'
import { fetchPreview } from './api/client'
import type { KnittingIR } from './ir/types'
import { BlocklyWorkspace } from './components/BlocklyWorkspace'
import { NodeLinkView } from './components/NodeLinkView'

function App() {
  const [compiled, setCompiled] = useState<KnittingIR | null>(null)
  const [compileErrors, setCompileErrors] = useState<string[]>([])
  const [preview, setPreview] = useState<PreviewResponse | null>(null)
  const [previewError, setPreviewError] = useState<string>('')
  const [isPreviewLoading, setIsPreviewLoading] = useState(false)

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
          <div className="title__subtitle">Build patterns in blocks, see them as charts.</div>
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

                  {c.warnings.length > 0 ? (
                    <div className="errors" role="status">
                      <div className="errors__title">Warnings</div>
                      <ul className="errors__list">
                        {c.warnings.map((w) => (
                          <li key={`${c.chartName}-warn-${w.commandIndex}-${w.message}`}>{`Command ${w.commandIndex}: ${w.message}`}</li>
                        ))}
                      </ul>
                    </div>
                  ) : null}

                  <div className="preview__viz">
                    <div className="preview__rowMeta">
                      Markers RS: {c.markers.RS.join(', ') || '—'} | WS: {c.markers.WS.join(', ') || '—'}
                    </div>
                    <NodeLinkView nodes={c.nodes} links={c.links} />
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
