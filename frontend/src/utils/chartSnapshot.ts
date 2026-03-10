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

const PADDING = 40

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

  const minX = Math.min(...nodes.map((n) => n.x))
  const maxX = Math.max(...nodes.map((n) => n.x))
  const minY = Math.min(...nodes.map((n) => n.y))
  const maxY = Math.max(...nodes.map((n) => n.y))
  const width = Math.max(200, maxX - minX + PADDING * 2)
  const height = Math.max(150, maxY - minY + PADDING * 2)
  const viewBox = `${minX - PADDING} ${minY - PADDING} ${width} ${height}`

  const circles = nodes
    .filter((n) => n.type.toLowerCase() !== 'strand')
    .map((n) => {
      const r = ['k', 'p', 'co', 'inc', 'dec'].includes(n.type.toLowerCase()) ? 5 : 3
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
  const minX = Math.min(...nodes.map((n) => n.x))
  const maxX = Math.max(...nodes.map((n) => n.x))
  const minY = Math.min(...nodes.map((n) => n.y))
  const maxY = Math.max(...nodes.map((n) => n.y))
  const width = Math.max(200, maxX - minX + PADDING * 2)
  const height = Math.max(150, maxY - minY + PADDING * 2)
  return {
    minX: minX - PADDING,
    minY: minY - PADDING,
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
