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
    currentStitchCount: number
    lastRowSide: 'RS' | 'WS' | null
  }>
}

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://localhost:8000'

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

