/**
 * Builds a chart SVG from nodes (same look as NodeLinkView) and returns a data URL
 * for use as an image overlay (e.g. on the torso). Exclude strand or match NodeLinkView.
 */

export type ChartNode = {
  id: string
  type: string
  x: number
  y: number
  row: number
}

const DEFAULT_PADDING = 40
const MIN_PADDING = 12
const MAX_PADDING = 32

export type ChartStyle = {
  padding: number
  radiusStitch: number
  radiusOther: number
}

/**
 * Derives padding and circle radii from chart density so nodes scale with gauge
 * and there is less white space when the chart is dense.
 */
export function getChartStyle(nodes: ChartNode[]): ChartStyle {
  const stitchNodes = nodes.filter((n) => n.type.toLowerCase() !== 'strand')
  if (stitchNodes.length === 0) {
    return { padding: DEFAULT_PADDING, radiusStitch: 5, radiusOther: 3 }
  }
  const minX = Math.min(...stitchNodes.map((n) => n.x))
  const maxX = Math.max(...stitchNodes.map((n) => n.x))
  const minY = Math.min(...stitchNodes.map((n) => n.y))
  const maxY = Math.max(...stitchNodes.map((n) => n.y))
  const contentWidth = maxX - minX
  const contentHeight = maxY - minY
  const rowCounts: Record<number, number> = {}
  for (const n of stitchNodes) {
    rowCounts[n.row] = (rowCounts[n.row] ?? 0) + 1
  }
  const numRows = Object.keys(rowCounts).length
  const numStitches = Math.max(0, ...Object.values(rowCounts))
  const spacingX = numStitches > 1 ? contentWidth / (numStitches - 1) : contentWidth || 20
  const spacingY = numRows > 1 ? contentHeight / (numRows - 1) : contentHeight || 20
  const baseSpacing = Math.min(spacingX, spacingY) || 20
  const radiusStitch = Math.max(2, Math.min(14, baseSpacing * 0.42))
  const radiusOther = radiusStitch * 0.6
  const contentMin = Math.min(contentWidth, contentHeight)
  const padding = Math.max(MIN_PADDING, Math.min(MAX_PADDING, Math.max(16, contentMin * 0.06)))
  return { padding, radiusStitch, radiusOther }
}

function colorForType(t: string): string {
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

function escapeXml(unsafe: string): string {
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')
}

/**
 * Returns SVG string for the chart (nodes as circles, same viewBox and colors as NodeLinkView).
 * Strand nodes are excluded so the snapshot matches the visible chart form.
 */
export function chartToSvgString(nodes: ChartNode[]): string {
  if (nodes.length === 0) {
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 150"></svg>`
  }

  const { padding, radiusStitch, radiusOther } = getChartStyle(nodes)
  const minX = Math.min(...nodes.map((n) => n.x))
  const maxX = Math.max(...nodes.map((n) => n.x))
  const minY = Math.min(...nodes.map((n) => n.y))
  const maxY = Math.max(...nodes.map((n) => n.y))
  const width = Math.max(200, maxX - minX + padding * 2)
  const height = Math.max(150, maxY - minY + padding * 2)
  const viewBox = `${minX - padding} ${minY - padding} ${width} ${height}`

  const circles = nodes
    .filter((n) => n.type.toLowerCase() !== 'strand')
    .map((n) => {
      const r = ['k', 'p', 'co', 'inc', 'dec'].includes(n.type.toLowerCase()) ? radiusStitch : radiusOther
      const fill = colorForType(n.type)
      return `<circle cx="${n.x}" cy="${n.y}" r="${r}" fill="${escapeXml(fill)}" stroke="#111827" stroke-width="0.5" opacity="0.9"/>`
    })
    .join('')

  return `<?xml version="1.0" encoding="UTF-8"?><svg xmlns="http://www.w3.org/2000/svg" viewBox="${escapeXml(viewBox)}">${circles}</svg>`
}

export type ChartExtent = {
  minX: number
  minY: number
  width: number
  height: number
}

/**
 * Computes chart extent in engine units (same as NodeLinkView viewBox extent).
 */
export function getChartExtent(nodes: ChartNode[]): ChartExtent | null {
  if (nodes.length === 0) return null
  const { padding } = getChartStyle(nodes)
  const minX = Math.min(...nodes.map((n) => n.x))
  const maxX = Math.max(...nodes.map((n) => n.x))
  const minY = Math.min(...nodes.map((n) => n.y))
  const maxY = Math.max(...nodes.map((n) => n.y))
  const width = Math.max(200, maxX - minX + padding * 2)
  const height = Math.max(150, maxY - minY + padding * 2)
  return {
    minX: minX - padding,
    minY: minY - padding,
    width,
    height,
  }
}

/**
 * Returns a data URL for the chart SVG (for use in <image href={...}>).
 */
export function chartToDataUrl(nodes: ChartNode[]): string | null {
  if (nodes.length === 0) return null
  const svg = chartToSvgString(nodes)
  const encoded = encodeURIComponent(svg)
  return `data:image/svg+xml;charset=utf-8,${encoded}`
}

const DEFAULT_PNG_MAX_SIZE = 2048

/**
 * Rasterizes the chart SVG to a PNG data URL for use as a bitmap overlay.
 * Caps canvas size at maxSize (default 2048) on the longer side so the bitmap stays manageable.
 */
export function chartToPngDataUrl(
  nodes: ChartNode[],
  maxSize: number = DEFAULT_PNG_MAX_SIZE,
): Promise<string | null> {
  if (nodes.length === 0) return Promise.resolve(null)
  const svgDataUrl = chartToDataUrl(nodes)
  if (!svgDataUrl) return Promise.resolve(null)
  const extent = getChartExtent(nodes)
  if (!extent) return Promise.resolve(null)

  return new Promise((resolve) => {
    const img = new Image()
    img.onload = () => {
      try {
        let w = extent!.width
        let h = extent!.height
        if (w > maxSize || h > maxSize) {
          const scale = maxSize / Math.max(w, h)
          w = Math.round(w * scale)
          h = Math.round(h * scale)
        }
        const canvas = document.createElement('canvas')
        canvas.width = w
        canvas.height = h
        const ctx = canvas.getContext('2d')
        if (!ctx) {
          resolve(null)
          return
        }
        ctx.drawImage(img, 0, 0, w, h)
        resolve(canvas.toDataURL('image/png'))
      } catch {
        resolve(null)
      }
    }
    img.onerror = () => resolve(null)
    img.src = svgDataUrl
  })
}
