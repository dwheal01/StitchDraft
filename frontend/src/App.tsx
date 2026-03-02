import './App.css'
import { useMemo, useState } from 'react'
import type { KnittingIR } from './ir/types'
import { BlocklyWorkspace } from './components/BlocklyWorkspace'

function App() {
  const [compiled, setCompiled] = useState<KnittingIR | null>(null)
  const [compileErrors, setCompileErrors] = useState<string[]>([])
  const [exportText, setExportText] = useState<string>('')
  const [copyStatus, setCopyStatus] = useState<string>('')

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
        </section>
      </main>
    </div>
  )
}

export default App
