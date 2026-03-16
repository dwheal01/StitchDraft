import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { chartToDataUrl, getChartExtent, getChartStyle } from '../utils/chartSnapshot'

type NodeVm = {
  id: string
  type: string
  x: number
  y: number
  row: number
}

type LinkVm = {
  source: string
  target: string
}

type Props = {
  nodes: NodeVm[]
  // Keep for future use; currently ignored
  links: LinkVm[]
  /** When true, left-drag pans the chart; Shift+drag measures. */
  allowPan?: boolean
}

export function NodeLinkView({ nodes, allowPan = false }: Props) {
  const svgRef = useRef<SVGSVGElement | null>(null)
  const pendingSelectionRef = useRef<{ x: number; y: number; width: number; height: number } | null>(null)
  const rafIdRef = useRef<number | null>(null)
  const panRafIdRef = useRef<number | null>(null)
  const pendingPanRef = useRef<{ x: number; y: number } | null>(null)

  const [dragging, setDragging] = useState(false)
  const [dragStart, setDragStart] = useState<{ x: number; y: number } | null>(null)
  const [selection, setSelection] = useState<{ x: number; y: number; width: number; height: number } | null>(null)
  const [measurement, setMeasurement] = useState<{
    numStitches: number
    numRows: number
    widthInches: number
    heightInches: number
  } | null>(null)

  const [noSelectionStitches, setNoSelectionStitches] = useState(false)

  const [panTranslate, setPanTranslate] = useState({ x: 0, y: 0 })
  const [panDragging, setPanDragging] = useState(false)
  const [panStart, setPanStart] = useState<{ x: number; y: number } | null>(null)
  const [panAtStart, setPanAtStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 })

  const chartStyle = useMemo(() => getChartStyle(nodes), [nodes])

  const { viewBox } = useMemo(() => {
    if (!nodes.length) return { viewBox: '0 0 200 150' }
    const { padding } = chartStyle
    const minX = Math.min(...nodes.map((n) => n.x))
    const maxX = Math.max(...nodes.map((n) => n.x))
    const minY = Math.min(...nodes.map((n) => n.y))
    const maxY = Math.max(...nodes.map((n) => n.y))
    const width = Math.max(200, maxX - minX + padding * 2)
    const height = Math.max(150, maxY - minY + padding * 2)
    return { viewBox: `${minX - padding} ${minY - padding} ${width} ${height}` }
  }, [nodes, chartStyle])

  const chartSnapshot = useMemo(() => {
    if (!allowPan || !nodes.length) return null
    const dataUrl = chartToDataUrl(nodes)
    const extent = getChartExtent(nodes)
    return dataUrl && extent ? { dataUrl, extent } : null
  }, [allowPan, nodes])

  const colorForType = (t: string) => {
    const key = t.toLowerCase()
    if (key === 'k') return '#4A90E2'
    if (key === 'p') return '#524be3'
    if (key === 'co') return '#4A90E2' // same as k so cast-on in row matches cast on additional
    if (key === 'inc') return '#85DCB0'
    if (key === 'dec') return '#E27D60'
    if (key === 'bo') return '#111827'
    if (key === 'strand') return '#9ca3af'
    return '#6b7280'
  }

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

  const computeMeasurement = useCallback(
    (box: { minX: number; maxX: number; minY: number; maxY: number }) => {
      const selectedNodes = nodes.filter((n) => {
        if (n.type.toLowerCase() === 'strand') return false
        return n.x >= box.minX && n.x <= box.maxX && n.y >= box.minY && n.y <= box.maxY
      })

      if (selectedNodes.length === 0) {
        setMeasurement(null)
        setNoSelectionStitches(true)
        return
      }

      setNoSelectionStitches(false)

      const rowSet = new Set<number>()
      const rowCounts: Record<number, number> = {}
      let minNodeX = Number.POSITIVE_INFINITY
      let maxNodeX = Number.NEGATIVE_INFINITY
      let minNodeY = Number.POSITIVE_INFINITY
      let maxNodeY = Number.NEGATIVE_INFINITY

      for (const n of selectedNodes) {
        rowSet.add(n.row)
        rowCounts[n.row] = (rowCounts[n.row] ?? 0) + 1
        if (n.x < minNodeX) minNodeX = n.x
        if (n.x > maxNodeX) maxNodeX = n.x
        if (n.y < minNodeY) minNodeY = n.y
        if (n.y > maxNodeY) maxNodeY = n.y
      }

      const numRows = rowSet.size
      const numStitches = Math.max(...Object.values(rowCounts))

      const widthUnits = maxNodeX - minNodeX
      const heightUnits = maxNodeY - minNodeY

      const UNITS_PER_INCH = 96
      // Report fabric width/height: center-to-center span plus one spacing at the end
      // so e.g. 44 sts at 22 sts/4" shows 8" not (44-1)/44 * 8" ≈ 7.82".
      const widthInches =
        numStitches > 1
          ? (Math.abs(widthUnits) / UNITS_PER_INCH) * (numStitches / (numStitches - 1))
          : Math.abs(widthUnits) / UNITS_PER_INCH
      const heightInches =
        numRows > 1
          ? (Math.abs(heightUnits) / UNITS_PER_INCH) * (numRows / (numRows - 1))
          : Math.abs(heightUnits) / UNITS_PER_INCH

      setMeasurement({
        numStitches,
        numRows,
        widthInches,
        heightInches,
      })
    },
    [nodes],
  )

  const handleMouseDown = useCallback(
    (evt: React.MouseEvent<SVGSVGElement, MouseEvent>) => {
      const pt = clientToSvgPoint(evt)
      if (!pt) return
      if (allowPan && !evt.shiftKey) {
        setPanDragging(true)
        setPanStart(pt)
        setPanAtStart(panTranslate)
      } else {
        setDragging(true)
        setDragStart(pt)
        setSelection({ x: pt.x, y: pt.y, width: 0, height: 0 })
      }
    },
    [allowPan, clientToSvgPoint, panTranslate],
  )

  const handleMouseMove = useCallback(
    (evt: React.MouseEvent<SVGSVGElement, MouseEvent>) => {
      const pt = clientToSvgPoint(evt)
      if (!pt) return
      if (panDragging && panStart) {
        const dx = pt.x - panStart.x
        const dy = pt.y - panStart.y
        pendingPanRef.current = { x: panAtStart.x + dx, y: panAtStart.y + dy }
        if (panRafIdRef.current === null) {
          panRafIdRef.current = requestAnimationFrame(() => {
            if (pendingPanRef.current) setPanTranslate(pendingPanRef.current)
            panRafIdRef.current = null
          })
        }
        return
      }
      if (!dragging || !dragStart) return
      const x1 = dragStart.x
      const y1 = dragStart.y
      const x2 = pt.x
      const y2 = pt.y
      const x = Math.min(x1, x2)
      const y = Math.min(y1, y2)
      const widthBox = Math.abs(x2 - x1)
      const heightBox = Math.abs(y2 - y1)
      pendingSelectionRef.current = { x, y, width: widthBox, height: heightBox }
      if (rafIdRef.current === null) {
        rafIdRef.current = requestAnimationFrame(() => {
          if (pendingSelectionRef.current) setSelection(pendingSelectionRef.current)
          rafIdRef.current = null
        })
      }
    },
    [clientToSvgPoint, dragging, dragStart, panAtStart.x, panAtStart.y, panDragging, panStart],
  )

  const stopPanDrag = useCallback(() => {
    if (panRafIdRef.current !== null) {
      cancelAnimationFrame(panRafIdRef.current)
      panRafIdRef.current = null
    }
    setPanDragging(false)
    setPanStart(null)
  }, [])

  const handleMouseUp = useCallback(
    (evt: React.MouseEvent<SVGSVGElement, MouseEvent>) => {
      if (panDragging) {
        stopPanDrag()
        return
      }
      if (!dragging || !dragStart) return
      if (rafIdRef.current !== null) {
        cancelAnimationFrame(rafIdRef.current)
        rafIdRef.current = null
      }
      const pt = clientToSvgPoint(evt) ?? dragStart
      setDragging(false)
      const x1 = dragStart.x
      const y1 = dragStart.y
      const x2 = pt.x
      const y2 = pt.y
      const minSelX = Math.min(x1, x2)
      const maxSelX = Math.max(x1, x2)
      const minSelY = Math.min(y1, y2)
      const maxSelY = Math.max(y1, y2)
      const widthBox = Math.abs(maxSelX - minSelX)
      const heightBox = Math.abs(maxSelY - minSelY)

      if (widthBox < 1 || heightBox < 1) {
        setSelection(null)
        setMeasurement(null)
        setNoSelectionStitches(false)
        setDragStart(null)
        return
      }

      setSelection({ x: minSelX, y: minSelY, width: widthBox, height: heightBox })
      computeMeasurement({ minX: minSelX, maxX: maxSelX, minY: minSelY, maxY: maxSelY })
      setDragStart(null)
    },
    [clientToSvgPoint, computeMeasurement, dragStart, dragging, panDragging, stopPanDrag],
  )

  useEffect(() => {
    if (!panDragging) return
    const onWindowMouseUp = () => stopPanDrag()
    window.addEventListener('mouseup', onWindowMouseUp)
    return () => window.removeEventListener('mouseup', onWindowMouseUp)
  }, [panDragging, stopPanDrag])

  const measurementLabel = useMemo(() => {
    if (noSelectionStitches) {
      return 'Measurement: no stitches in selection.'
    }
    if (!measurement) {
      return allowPan
        ? 'Measurement: Hold Shift and drag on the chart to measure an area.'
        : 'Measurement: drag on the chart to measure an area.'
    }
    const { numStitches, numRows, widthInches, heightInches } = measurement
    const widthCm = widthInches * 2.54
    const heightCm = heightInches * 2.54
    return `Measurement: ~${numStitches} sts × ${numRows} rows, ${widthInches.toFixed(
      2,
    )}" × ${heightInches.toFixed(2)}" (${widthCm.toFixed(1)} cm × ${heightCm.toFixed(1)} cm)`
  }, [allowPan, measurement, noSelectionStitches])

  if (!nodes.length) {
    return <div className="nodeLinkEmpty">No stitches to display yet.</div>
  }

  return (
    <div className="nodeLinkWrapper">
      <svg
        ref={svgRef}
        className="nodeLinkSvg"
        viewBox={viewBox}
        preserveAspectRatio="xMidYMid meet"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        style={allowPan ? { cursor: panDragging ? 'grabbing' : 'grab' } : undefined}
      >
        <g transform={`translate(${panTranslate.x} ${panTranslate.y})`}>
          {allowPan && chartSnapshot ? (
            <image
              href={chartSnapshot.dataUrl}
              x={chartSnapshot.extent.minX}
              y={chartSnapshot.extent.minY}
              width={chartSnapshot.extent.width}
              height={chartSnapshot.extent.height}
              preserveAspectRatio="xMidYMid meet"
            />
          ) : (
            <g className="nodeLinkNodes">
              {nodes.map((n) => (
                <circle
                  key={n.id}
                  cx={n.x}
                  cy={n.y}
                  r={
                    n.type === 'k' || n.type === 'p' || n.type === 'co' || n.type === 'inc' || n.type === 'dec'
                      ? chartStyle.radiusStitch
                      : chartStyle.radiusOther
                  }
                  fill={colorForType(n.type)}
                  stroke={n.type === 'strand' ? 'none' : '#111827'}
                  strokeWidth={0.5}
                  opacity={n.type === 'strand' ? 0.0 : 1}
                />
              ))}
            </g>
          )}
          {selection ? (
            <g className="nodeLinkMeasurementBox">
              <rect
                x={selection.x}
                y={selection.y}
                width={selection.width}
                height={selection.height}
                fill="rgba(52, 211, 153, 0.16)"
                stroke="#34d399"
                strokeWidth={1}
              />
            </g>
          ) : null}
        </g>
      </svg>
      <div className="nodeLinkMeasurement">{measurementLabel}</div>
    </div>
  )
}

