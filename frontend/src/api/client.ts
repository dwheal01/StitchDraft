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

export type TorsoSize = 'XS' | 'S' | 'M' | 'L' | 'XL' | '2XL' | '3XL' | '4XL' | '5XL'

export type TorsoSvgRequest =
  | { mode: 'size'; size: TorsoSize }
  | {
      mode: 'custom'
      measurements: {
        shoulder_width: number
        back_length: number
        bust_circ: number
        waist_circ: number
        hip_circ: number
        armhole_depth: number
        upper_arm_circ: number
        arm_length: number
        apex_depth?: number | null
        waist_to_hip: number
        top_padding: number
        ease: number
      }
    }

export type TorsoSvgResponse = {
  svg: string
  viewBox: string
  width: number
  height: number
}

export type TorsoSizesResponse = {
  sizes: Record<
    TorsoSize,
    {
      shoulder_width: number
      back_length: number
      bust_circ: number
      waist_circ: number
      hip_circ: number
      armhole_depth: number
      upper_arm_circ: number
      arm_length: number
    }
  >
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

export async function fetchTorsoSizes(signal?: AbortSignal): Promise<TorsoSizesResponse> {
  const res = await fetch(`${API_BASE_URL}/torso/sizes`, { signal })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`Torso sizes failed (${res.status}): ${text || res.statusText}`)
  }
  return (await res.json()) as TorsoSizesResponse
}

export async function fetchTorsoSvg(req: TorsoSvgRequest, signal?: AbortSignal): Promise<TorsoSvgResponse> {
  const res = await fetch(`${API_BASE_URL}/torso/svg`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(req),
    signal,
  })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`Torso SVG failed (${res.status}): ${text || res.statusText}`)
  }
  return (await res.json()) as TorsoSvgResponse
}

