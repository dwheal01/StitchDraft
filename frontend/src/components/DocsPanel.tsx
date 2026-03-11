import type { ReactNode } from 'react'

type Props = {
  open: boolean
  onClose: () => void
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="docsPanel__section">
      <h2 className="docsPanel__sectionTitle">{title}</h2>
      {children}
    </section>
  )
}

export function DocsPanel({ open, onClose }: Props) {
  if (!open) return null

  return (
    <div className="docsPanel" role="dialog" aria-modal="true" aria-label="StitchDraft documentation">
      <div className="docsPanel__backdrop" onClick={onClose} />
      <aside className="docsPanel__content">
        <header className="docsPanel__header">
          <div>
            <h1 className="docsPanel__title">StitchDraft docs</h1>
            <p className="docsPanel__subtitle">How to build and inspect knitted garment charts.</p>
          </div>
          <button type="button" className="docsPanel__close" onClick={onClose}>
            Close
          </button>
        </header>

        <div className="docsPanel__body">
          <Section title="Overview">
            <p>
              StitchDraft lets you build knitting charts using drag-and-drop blocks, then preview the resulting stitch
              graph and an approximate torso overlay. The left side of the app is the block workspace; the right side
              shows chart previews, warnings, and torso views.
            </p>
          </Section>

          <Section title="App layout">
            <ul>
              <li>
                <strong>Chart builder (left):</strong> Blockly workspace where you assemble chart, pattern, and structure
                blocks. The workspace automatically recompiles as you edit.
              </li>
              <li>
                <strong>Preview panel (right):</strong> For each chart, shows stitch counts, warnings/errors, and a
                node-link visualization of stitches.
              </li>
              <li>
                <strong>Measurement tool:</strong> In the chart view, drag to select an area (or Shift+drag in full-screen
                mode) to see approximate stitch/row counts and real-world dimensions.
              </li>
              <li>
                <strong>Torso view:</strong> \"Show torso view\" requests a torso overlay from the backend so you can
                compare the chart to a garment outline.
              </li>
            </ul>
          </Section>

          <Section title="Supported commands">
            <p>
              Each chart is built by a list of commands. Below are all supported commands in order of execution.
            </p>

            <h3 className="docsPanel__subheading">Chart (setup)</h3>
            <ul>
              <li>
                <strong>Chart:</strong> Defines one chart: name, starting side (RS or WS), base stitch count, and row
                count. All commands listed below are attached to this chart and run in order.
              </li>
            </ul>

            <h3 className="docsPanel__subheading">Cast on</h3>
            <ul>
              <li>
                <strong>cast on start:</strong> Sets the initial number of stitches on the needle before any rows or
                rounds. Required before working rows. Parameter: <code>count</code> (number of stitches).
              </li>
              <li>
                <strong>cast on additional:</strong> Adds more stitches to the needle after some rows/rounds (e.g. for
                underarm or join). Parameter: <code>count</code> (number to cast on).
              </li>
            </ul>

            <h3 className="docsPanel__subheading">Rows and rounds</h3>
            <ul>
              <li>
                <strong>add row:</strong> Works one flat (back-and-forth) row using a pattern string. Parameter:{' '}
                <code>pattern</code> (see Pattern syntax below).
              </li>
              <li>
                <strong>add round:</strong> Works one circular round using a pattern string. Parameter:{' '}
                <code>pattern</code>.
              </li>
              <li>
                <strong>repeat rows:</strong> Repeats a sequence of row patterns a given number of times. Parameters:{' '}
                <code>times</code>, <code>patterns</code> (list of pattern blocks).
              </li>
              <li>
                <strong>repeat rounds:</strong> Repeats a sequence of round patterns a given number of times.
                Parameters: <code>times</code>, <code>patterns</code>.
              </li>
            </ul>

            <h3 className="docsPanel__subheading">Markers</h3>
            <ul>
              <li>
                <strong>place marker:</strong> Places a marker at a stitch index on the RS or WS. Shown in preview
                metadata. Parameters: <code>side</code> (RS/WS), <code>position</code> (stitch index).
              </li>
            </ul>

            <h3 className="docsPanel__subheading">Holds and joins</h3>
            <ul>
              <li>
                <strong>place on hold:</strong> Moves the current live stitches into a named hold (e.g. <code>left</code>,{' '}
                <code>right</code>). Parameter: <code>name</code>.
              </li>
              <li>
                <strong>place on needle:</strong> Returns stitches from a named hold to the needle. Parameters:{' '}
                <code>from_hold</code> (hold name), <code>join_side</code> (RS/WS), <code>cast on between</code> (optional
                stitches to cast on between, e.g. for a gap).
              </li>
              <li>
                <strong>join chart:</strong> Joins another chart to the right of this one. You specify the other chart
                by name and a pattern for how to work the joined stitches. Parameters: <code>chart name</code>,{' '}
                <code>pattern</code> (e.g. <code>repeat(k1)</code>).
              </li>
            </ul>
          </Section>

          <Section title="Pattern syntax">
            <p>
              Row and round pattern fields accept only the operations listed below. Any other token will produce an
              error that includes the invalid token and the allowed list.
            </p>
            <ul>
              <li>
                <strong>Stitches:</strong> <code>k</code>, <code>p</code>, <code>inc</code>, <code>dec</code>,{' '}
                <code>bo</code>, <code>co</code> (with optional counts, e.g. <code>k2</code>, <code>p1</code>).
              </li>
              <li>
                <strong>Markers:</strong> <code>pm</code> (place marker), <code>rm</code> (remove marker),{' '}
                <code>sm</code> (slip marker).
              </li>
              <li>
                <strong>Work as established:</strong> <code>work est</code>, <code>work established</code>,{' '}
                <code>est</code>, <code>cont as est</code>, <code>cont as established</code>.
              </li>
              <li>
                <strong>Structure:</strong> <code>repeat(...)</code> — e.g. <code>repeat(k1)</code>,{' '}
                <code>repeat(k2, p2)</code>.
              </li>
            </ul>
            <p>
              <strong>Examples:</strong> <code>k2, inc, repeat(k1)</code> — <code>repeat(k1), sm, repeat(k1)</code>
            </p>
          </Section>

          <Section title="Backend interaction">
            <ul>
              <li>
                <strong>/preview:</strong> Takes the compiled intermediate representation (IR) from the Blockly workspace
                and returns chart nodes, links, errors, warnings, and marker positions for each chart.
              </li>
              <li>
                <strong>/torso:</strong> Generates a torso overlay SVG based on the current chart selection and options
                from the Torso controls panel.
              </li>
            </ul>
          </Section>

          <Section title="Tips &amp; troubleshooting">
            <ul>
              <li>Fix any compile errors in the IR panel before trusting preview or torso results.</li>
              <li>
                Execution errors show as &quot;Command N: message&quot; — N is the 0-based index of the command block
                (e.g. Command 1 is the second block). Pattern errors include the invalid token and the list of allowed
                operations.
              </li>
              <li>
                Use full-screen chart/torso modes for detailed inspection; the measurement tool is easiest to use there.
              </li>
            </ul>
          </Section>
        </div>
      </aside>
    </div>
  )
}

