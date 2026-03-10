import './App.css'
import { useEffect, useState } from 'react'
import type { PreviewResponse } from './api/client'
import { fetchPreview } from './api/client'
import type { KnittingIR } from './ir/types'
import { BlocklyWorkspace } from './components/BlocklyWorkspace'
import { NodeLinkView } from './components/NodeLinkView'
import type { TorsoSvgResponse } from './api/client'
import { TorsoControls } from './components/TorsoControls'
import { TorsoOverlayView } from './components/TorsoOverlayView'
import { FullScreenOverlay } from './components/FullScreenOverlay'
import { chartToSvgString } from './utils/chartSnapshot'

function downloadChartAsSvg(chartName: string, nodes: PreviewResponse['charts'][0]['nodes']) {
  if (nodes.length === 0) return
  const svg = chartToSvgString(nodes)
  const blob = new Blob([svg], { type: 'image/svg+xml;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${chartName.replace(/[^a-zA-Z0-9_-]/g, '_')}.svg`
  a.click()
  URL.revokeObjectURL(url)
}

function App() {
  const [compiled, setCompiled] = useState<KnittingIR | null>(null)
  const [compileErrors, setCompileErrors] = useState<string[]>([])
  const [preview, setPreview] = useState<PreviewResponse | null>(null)
  const [previewError, setPreviewError] = useState<string>('')
  const [isPreviewLoading, setIsPreviewLoading] = useState(false)
  const [torsoByChart, setTorsoByChart] = useState<Record<string, TorsoSvgResponse | null>>({})
  const [torsoOpenByChart, setTorsoOpenByChart] = useState<Record<string, boolean>>({})
  const [collapsedByChart, setCollapsedByChart] = useState<Record<string, boolean>>({})
  const [fullScreenChartName, setFullScreenChartName] = useState<string | null>(null)
  const [fullScreenTorsoChartName, setFullScreenTorsoChartName] = useState<string | null>(null)

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
                <div
                  key={c.chartName}
                  className={`preview__chart${collapsedByChart[c.chartName] ? ' preview__chart--collapsed' : ''}`}
                >
                  <div className="preview__chartHeader">
                    <div className="preview__chartName">{c.chartName}</div>
                    <div className="preview__chartMeta">
                      {c.rows.length} row(s), {c.currentStitchCount} st(s)
                    </div>
                    {collapsedByChart[c.chartName] && (c.errors.length > 0 || c.warnings.length > 0) ? (
                      <div className="preview__chartMeta">
                        {c.errors.length > 0 ? `Errors: ${c.errors.length}` : null}
                        {c.errors.length > 0 && c.warnings.length > 0 ? ' | ' : null}
                        {c.warnings.length > 0 ? `Warnings: ${c.warnings.length}` : null}
                      </div>
                    ) : null}
                    <button
                      type="button"
                      className="torsoPanel__toggle"
                      onClick={() => setFullScreenChartName(c.chartName)}
                    >
                      Full screen
                    </button>
                    <button
                      type="button"
                      className="torsoPanel__toggle"
                      onClick={() => downloadChartAsSvg(c.chartName, c.nodes)}
                      disabled={c.nodes.length === 0}
                    >
                      Download chart
                    </button>
                    <button
                      type="button"
                      className="torsoPanel__toggle"
                      aria-expanded={!collapsedByChart[c.chartName]}
                      onClick={() =>
                        setCollapsedByChart((prev) => ({
                          ...prev,
                          [c.chartName]: !prev[c.chartName],
                        }))
                      }
                    >
                      {collapsedByChart[c.chartName] ? 'Expand' : 'Collapse'}
                    </button>
                  </div>

                  {!collapsedByChart[c.chartName] ? (
                    <>
                      {c.errors.length > 0 ? (
                        <div className="errors" role="alert">
                          <div className="errors__title">Execution errors</div>
                          <ul className="errors__list">
                            {c.errors.map((e) => (
                              <li
                                key={`${c.chartName}-${e.commandIndex}`}
                              >{`Command ${e.commandIndex}: ${e.message}`}</li>
                            ))}
                          </ul>
                        </div>
                      ) : null}

                      {c.warnings.length > 0 ? (
                        <div className="errors" role="status">
                          <div className="errors__title">Warnings</div>
                          <ul className="errors__list">
                            {c.warnings.map((w) => (
                              <li
                                key={`${c.chartName}-warn-${w.commandIndex}-${w.message}`}
                              >{`Command ${w.commandIndex}: ${w.message}`}</li>
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

                      <div className="torsoPanel">
                        <button
                          className="torsoPanel__toggle"
                          onClick={() =>
                            setTorsoOpenByChart((prev) => ({
                              ...prev,
                              [c.chartName]: !prev[c.chartName],
                            }))
                          }
                        >
                          {torsoOpenByChart[c.chartName] ? 'Hide torso view' : 'Show torso view'}
                        </button>

                        {torsoOpenByChart[c.chartName] ? (
                          <div className="torsoPanel__content">
                            <div className="torsoPanel__row">
                              <TorsoControls
                                onTorsoLoaded={(torso) =>
                                  setTorsoByChart((prev) => ({
                                    ...prev,
                                    [c.chartName]: torso,
                                  }))
                                }
                              />
                              <button
                                type="button"
                                className="torsoPanel__toggle"
                                onClick={() => setFullScreenTorsoChartName(c.chartName)}
                              >
                                Full screen
                              </button>
                            </div>
                            <TorsoOverlayView torso={torsoByChart[c.chartName] ?? null} nodes={c.nodes} />
                          </div>
                        ) : null}
                      </div>
                    </>
                  ) : null}

                  <FullScreenOverlay
                    open={fullScreenChartName === c.chartName}
                    onClose={() => setFullScreenChartName(null)}
                    title={c.chartName}
                  >
                    <div className="preview__rowMeta">
                      Markers RS: {c.markers.RS.join(', ') || '—'} | WS: {c.markers.WS.join(', ') || '—'}
                    </div>
                    <NodeLinkView nodes={c.nodes} links={c.links} allowPan />
                  </FullScreenOverlay>

                  <FullScreenOverlay
                    open={fullScreenTorsoChartName === c.chartName}
                    onClose={() => setFullScreenTorsoChartName(null)}
                    title={`${c.chartName} – Torso`}
                  >
                    <TorsoOverlayView torso={torsoByChart[c.chartName] ?? null} nodes={c.nodes} />
                  </FullScreenOverlay>
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
