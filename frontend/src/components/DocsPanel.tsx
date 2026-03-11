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

          <Section title="Block categories">
            <h3 className="docsPanel__subheading">Chart setup</h3>
            <ul>
              <li>
                <strong>Chart:</strong> Defines a chart section: name, starting side (RS/WS), base stitch count, and row
                count. Commands attached below describe how stitches evolve over time.
              </li>
              <li>
                <strong>cast on start:</strong> Sets the initial number of stitches for the chart before any rows or
                rounds are worked.
              </li>
            </ul>

            <h3 className="docsPanel__subheading">Stitch patterns</h3>
            <ul>
              <li>
                <strong>pattern:</strong> A single row or round pattern, written in the engine DSL
                (e.g. <code>repeat(k1)</code> or <code>k2, inc, repeat(k1)</code>).
              </li>
              <li>
                <strong>add row / add round:</strong> Apply a single flat row or circular round using a pattern string.
              </li>
              <li>
                <strong>repeat rows / repeat rounds:</strong> Repeat a sequence of pattern blocks a given number of times.
              </li>
              <li>
                <strong>cast on additional:</strong> Cast on more stitches after the initial chart setup (for example,
                when joining pieces or adding underarm stitches).
              </li>
            </ul>

            <h3 className="docsPanel__subheading">Structure &amp; markers</h3>
            <ul>
              <li>
                <strong>place marker:</strong> Place a marker at a specific stitch index on the RS or WS. Markers appear
                in the preview metadata.
              </li>
              <li>
                <strong>place on hold:</strong> Move the remaining live stitches into a named hold slot (for example
                <code>left</code> or <code>right</code>).
              </li>
              <li>
                <strong>place on needle:</strong> Bring stitches back from a named hold onto the needle. Optionally cast
                on stitches in between to create joins or gaps.
              </li>
              <li>
                <strong>join chart:</strong> Join another chart to the right of the current one and describe how to work
                the joined stitches.
              </li>
            </ul>
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
                If the preview shows execution errors, hover the messages to see which command index triggered the
                problem.
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

