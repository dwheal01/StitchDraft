import { useEffect, useRef } from 'react'

type ChartCanvasProps = {
  rows: string[][]
  maxRows?: number
  maxCols?: number
  cellSize?: number
}

const DEFAULT_CELL_SIZE = 12
const DEFAULT_MAX_ROWS = 80
const DEFAULT_MAX_COLS = 120

function colourForStitch(stitch: string): string {
  const s = stitch.toLowerCase()
  if (s.startsWith('k')) return '#22c55e' // knit
  if (s.startsWith('p')) return '#0ea5e9' // purl
  if (s.startsWith('inc')) return '#eab308'
  if (s.startsWith('dec')) return '#f97316'
  if (s.startsWith('bo')) return '#f43f5e'
  if (s.startsWith('co')) return '#a855f7'
  return '#6b7280' // fallback
}

export function ChartCanvas({ rows, maxRows, maxCols, cellSize }: ChartCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const size = cellSize ?? DEFAULT_CELL_SIZE
    const rowLimit = maxRows ?? DEFAULT_MAX_ROWS
    const colLimit = maxCols ?? DEFAULT_MAX_COLS

    const limitedRows = rows.slice(0, rowLimit)
    const widthCols = Math.min(
      colLimit,
      limitedRows.reduce((max, r) => (r.length > max ? r.length : max), 0),
    )
    const heightRows = limitedRows.length

    if (widthCols === 0 || heightRows === 0) {
      const ctx = canvas.getContext('2d')
      if (ctx) {
        canvas.width = 0
        canvas.height = 0
      }
      return
    }

    const pixelWidth = widthCols * size
    const pixelHeight = heightRows * size
    canvas.width = pixelWidth
    canvas.height = pixelHeight

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    ctx.clearRect(0, 0, pixelWidth, pixelHeight)

    for (let rowIdx = 0; rowIdx < heightRows; rowIdx += 1) {
      const row = limitedRows[rowIdx]
      const y = rowIdx * size
      for (let colIdx = 0; colIdx < Math.min(row.length, widthCols); colIdx += 1) {
        const stitch = row[colIdx]
        const x = colIdx * size
        ctx.fillStyle = colourForStitch(stitch)
        ctx.fillRect(x, y, size - 1, size - 1)
      }
    }
  }, [rows, maxRows, maxCols, cellSize])

  return (
    <div className="chartCanvasWrapper">
      <canvas ref={canvasRef} />
    </div>
  )
}

