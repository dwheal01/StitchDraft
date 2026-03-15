import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { TorsoSvgResponse } from '../api/client'
import { chartToDataUrl, chartToPngDataUrl, getChartExtent } from '../utils/chartSnapshot'

type NodeVm = {
  id: string
  type: string
  x: number
  y: number
  row: number
}

type Props = {
  torso: TorsoSvgResponse | null
  nodes: NodeVm[]
}

function extractSvgInner(svgString: string): { inner: string; viewBox?: string } {
  try {
    const doc = new DOMParser().parseFromString(svgString, 'image/svg+xml')
    const svgEl = doc.documentElement
    const viewBox = svgEl.getAttribute('viewBox') ?? undefined
    return { inner: svgEl.innerHTML, viewBox }
  } catch {
    // Fallback: naive extraction
    const start = svgString.indexOf('>') + 1
    const end = svgString.lastIndexOf('</svg>')
    const inner = start > 0 && end > start ? svgString.slice(start, end) : svgString
    return { inner }
  }
}

function parseViewBox(viewBox: string): { minX: number; minY: number; width: number; height: number } | null {
  const parts = viewBox
    .trim()
    .split(/\s+/)
    .map((v) => Number(v))
  if (parts.length !== 4 || parts.some((n) => !Number.isFinite(n))) return null
  const [minX, minY, width, height] = parts
  return { minX, minY, width, height }
}

function colorForType(t: string) {
  const key = t.toLowerCase()
  if (key === 'k') return '#4A90E2'
  if (key === 'p') return '#524be3'
  if (key === 'co') return '#4A90E2'
  if (key === 'inc') return '#85DCB0'
  if (key === 'dec') return '#E27D60'
  if (key === 'bo') return '#111827'
  if (key === 'strand') return '#9ca3af'
  return '#6b7280'
}

export function TorsoOverlayView({ torso, nodes }: Props) {
  const svgRef = useRef<SVGSVGElement | null>(null)
  const pendingOffsetRef = useRef<{ dx: number; dy: number } | null>(null)
  const rafIdRef = useRef<number | null>(null)

  const [dragging, setDragging] = useState(false)
  const [dragStart, setDragStart] = useState<{ x: number; y: number } | null>(null)
  const [offset, setOffset] = useState<{ dx: number; dy: number }>({ dx: 0, dy: 0 })
  const [offsetAtStart, setOffsetAtStart] = useState<{ dx: number; dy: number }>({ dx: 0, dy: 0 })
  const [rotation, setRotation] = useState(0) // degrees

  const { inner: torsoInner, viewBox: torsoViewBoxFromSvg } = useMemo(() => {
    if (!torso?.svg) return { inner: '', viewBox: undefined as string | undefined }
    return extractSvgInner(torso.svg)
  }, [torso?.svg])

  const viewBox = torso?.viewBox || torsoViewBoxFromSvg || '0 0 100 100'
  const vb = useMemo(() => parseViewBox(viewBox), [viewBox])

  const engineUnitsToInches = useCallback((v: number) => v / 96, [])

  const chartNodesInInches = useMemo(() => {
    return nodes
      .filter((n) => n.type.toLowerCase() !== 'strand')
      .map((n) => ({
        ...n,
        xIn: engineUnitsToInches(n.x),
        yIn: engineUnitsToInches(n.y),
      }))
  }, [engineUnitsToInches, nodes])

  const chartSnapshotSvg = useMemo(() => {
    const dataUrl = chartToDataUrl(nodes)
    const extent = getChartExtent(nodes)
    return dataUrl && extent ? { dataUrl, extent } : null
  }, [nodes])

  const [chartPngSnapshot, setChartPngSnapshot] = useState<{
    dataUrl: string
    extent: { minX: number; minY: number; width: number; height: number }
  } | null>(null)

  useEffect(() => {
    if (!nodes.length) {
      setChartPngSnapshot(null)
      return
    }
    const extent = getChartExtent(nodes)
    if (!extent) {
      setChartPngSnapshot(null)
      return
    }
    let cancelled = false
    chartToPngDataUrl(nodes).then((dataUrl) => {
      if (cancelled || !dataUrl) return
      setChartPngSnapshot({ dataUrl, extent })
    })
    return () => {
      cancelled = true
    }
  }, [nodes])

  const chartSnapshot = chartPngSnapshot ?? chartSnapshotSvg

  const chartCenterInInches = useMemo(() => {
    const ext = chartSnapshot?.extent ?? getChartExtent(nodes)
    if (!ext || (!chartSnapshot && nodes.length === 0)) return { cx: 0, cy: 0 }
    return {
      cx: (ext.minX + ext.width / 2) / 96,
      cy: (ext.minY + ext.height / 2) / 96,
    }
  }, [chartSnapshot, nodes])

  const clientToSvgPoint = useCallback((evt: React.MouseEvent<SVGSVGElement, MouseEvent>) => {
    const svg = svgRef.current
    if (!svg) return null
    const pt = svg.createSVGPoint()
    pt.x = evt.clientX
    pt.y = evt.clientY
    const ctm = svg.getScreenCTM()
    if (!ctm) return null
    const svgPt = pt.matrixTransform(ctm.inverse())
    return { x: svgPt.x, y: svgPt.y }
  }, [])

  const onMouseDown = useCallback(
    (evt: React.MouseEvent<SVGGElement, MouseEvent>) => {
      evt.preventDefault()
      evt.stopPropagation()
      const pt = clientToSvgPoint(evt as unknown as React.MouseEvent<SVGSVGElement, MouseEvent>)
      if (!pt) return
      setDragging(true)
      setDragStart(pt)
      setOffsetAtStart(offset)
    },
    [clientToSvgPoint, offset],
  )

  const onMouseMove = useCallback(
    (evt: React.MouseEvent<SVGSVGElement, MouseEvent>) => {
      if (!dragging || !dragStart) return
      const pt = clientToSvgPoint(evt)
      if (!pt) return
      const dx = pt.x - dragStart.x
      const dy = pt.y - dragStart.y
      pendingOffsetRef.current = { dx: offsetAtStart.dx + dx, dy: offsetAtStart.dy + dy }
      if (rafIdRef.current === null) {
        rafIdRef.current = requestAnimationFrame(() => {
          if (pendingOffsetRef.current) setOffset(pendingOffsetRef.current)
          rafIdRef.current = null
        })
      }
    },
    [clientToSvgPoint, dragStart, dragging, offsetAtStart.dx, offsetAtStart.dy],
  )

  const stopDrag = useCallback(() => {
    if (rafIdRef.current !== null) {
      cancelAnimationFrame(rafIdRef.current)
      rafIdRef.current = null
    }
    setDragging(false)
    setDragStart(null)
  }, [])

  useEffect(() => {
    if (!dragging) return
    const onWindowMouseUp = () => stopDrag()
    window.addEventListener('mouseup', onWindowMouseUp)
    return () => window.removeEventListener('mouseup', onWindowMouseUp)
  }, [dragging, stopDrag])

  if (!torso) {
    return <div className="torsoOverlayEmpty">Generate a torso to view the overlay.</div>
  }

  return (
    <div className="torsoOverlayWrapper">
      <svg
        ref={svgRef}
        className="torsoOverlaySvg"
        viewBox={viewBox}
        preserveAspectRatio="xMidYMid meet"
        onMouseMove={onMouseMove}
        onMouseUp={stopDrag}
        onMouseLeave={stopDrag}
      >
        {/* Torso base (in inches coordinate space) */}
        <g className="torsoOverlayTorso" dangerouslySetInnerHTML={{ __html: torsoInner }} />

        {/* Chart overlay, draggable as a group: snapshot image when available, else circles. Rotate around chart center. */}
        <g
          className="torsoOverlayChart"
          transform={`translate(${offset.dx} ${offset.dy}) translate(${chartCenterInInches.cx} ${chartCenterInInches.cy}) rotate(${rotation}) translate(${-chartCenterInInches.cx} ${-chartCenterInInches.cy})`}
          onMouseDown={onMouseDown}
          style={{
            cursor: dragging ? 'grabbing' : 'grab',
            willChange: dragging ? 'transform' : 'auto',
          }}
        >
          {chartSnapshot ? (
            <image
              href={chartSnapshot.dataUrl}
              x={chartSnapshot.extent.minX / 96}
              y={chartSnapshot.extent.minY / 96}
              width={chartSnapshot.extent.width / 96}
              height={chartSnapshot.extent.height / 96}
              preserveAspectRatio="xMidYMid meet"
            />
          ) : (
            chartNodesInInches.map((n) => (
              <circle
                key={n.id}
                cx={n.xIn}
                cy={n.yIn}
                r={n.type === 'k' || n.type === 'p' || n.type === 'co' || n.type === 'inc' || n.type === 'dec' ? 0.12 : 0.08}
                fill={colorForType(n.type)}
                stroke="#111827"
                strokeWidth={0.02}
                opacity={0.9}
              />
            ))
          )}
        </g>

        {/* Optional: a subtle border using viewBox extents */}
        {vb ? (
          <rect
            x={vb.minX}
            y={vb.minY}
            width={vb.width}
            height={vb.height}
            fill="none"
            stroke="rgba(148, 163, 184, 0.25)"
            strokeWidth={0.05}
          />
        ) : null}
      </svg>
      <div className="torsoOverlayMeta">
        <span>
          Torso: {torso.width.toFixed(2)}&quot; × {torso.height.toFixed(2)}&quot; | Chart: engine units ÷ 96
        </span>
        {nodes.length > 0 ? (
          <span className="torsoOverlayMeta__rotate">
            Rotate chart:{' '}
            <button
              type="button"
              className="torsoOverlayMeta__btn"
              onClick={() => setRotation((r) => r - 15)}
              title="Rotate left 15°"
              aria-label="Rotate chart left 15 degrees"
            >
              ←
            </button>
            <button
              type="button"
              className="torsoOverlayMeta__btn"
              onClick={() => setRotation((r) => r + 15)}
              title="Rotate right 15°"
              aria-label="Rotate chart right 15 degrees"
            >
              →
            </button>
            <span className="torsoOverlayMeta__angle">{rotation}°</span>
          </span>
        ) : null}
      </div>
    </div>
  )
}

