import type { KnittingIR } from '../ir/types'

export type PreviewResponse = {
  charts: Array<{
    chartName: string
    rows: string[][]
    rowMeta: Array<{
      rowIndex: number
      side: 'RS' | 'WS'
      isRound: boolean
      stitchCountBefore: number
      stitchCountAfter: number
    }>
    markers: { RS: number[]; WS: number[] }
    errors: Array<{ commandIndex: number; message: string }>
    warnings: Array<{ commandIndex: number; message: string }>
    currentStitchCount: number
    lastRowSide: 'RS' | 'WS' | null
    nodes: Array<{
      id: string
      type: string
      x: number
      y: number
      row: number
    }>
    links: Array<{
      source: string
      target: string
    }>
  }>
}

// In dev, use relative URL so Vite can proxy to the backend (avoids CORS). Override with VITE_API_BASE_URL when needed.
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? ''

export async function fetchPreview(ir: KnittingIR, signal?: AbortSignal): Promise<PreviewResponse> {
  const res = await fetch(`${API_BASE_URL}/preview`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(ir),
    signal,
  })

  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`Preview failed (${res.status}): ${text || res.statusText}`)
  }

  return (await res.json()) as PreviewResponse
}

