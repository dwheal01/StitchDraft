import { useEffect, useMemo, useState } from 'react'
import type { TorsoSize, TorsoSvgRequest, TorsoSvgResponse } from '../api/client'
import { fetchTorsoSizes, fetchTorsoSvg } from '../api/client'

type Props = {
  onTorsoLoaded: (torso: TorsoSvgResponse) => void
}

type Mode = 'size' | 'custom'

const DEFAULT_CUSTOM = {
  shoulder_width: 15,
  back_length: 17,
  bust_circ: 35,
  waist_circ: 27,
  hip_circ: 40,
  armhole_depth: 6.75,
  upper_arm_circ: 11,
  arm_length: 20,
  apex_depth: 10,
  waist_to_hip: 8,
  top_padding: 2,
  ease: 0,
}

function asNumber(value: string): number {
  const n = Number(value)
  return Number.isFinite(n) ? n : 0
}

export function TorsoControls({ onTorsoLoaded }: Props) {
  const [mode, setMode] = useState<Mode>('size')
  const [size, setSize] = useState<TorsoSize>('M')
  const [custom, setCustom] = useState({ ...DEFAULT_CUSTOM })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string>('')

  const [sizesLoaded, setSizesLoaded] = useState<Record<string, unknown> | null>(null)

  useEffect(() => {
    // Optional: fetch sizes for validation/future UI help. Fallback to hardcoded list if it fails.
    const controller = new AbortController()
    fetchTorsoSizes(controller.signal)
      .then((data) => setSizesLoaded(data.sizes))
      .catch(() => setSizesLoaded(null))
    return () => controller.abort()
  }, [])

  const canGenerate = useMemo(() => {
    if (mode === 'size') return Boolean(size)
    return true
  }, [mode, size])

  async function generate() {
    if (!canGenerate) return
    setIsLoading(true)
    setError('')
    try {
      let req: TorsoSvgRequest
      if (mode === 'size') {
        req = { mode: 'size', size }
      } else {
        req = {
          mode: 'custom',
          measurements: {
            shoulder_width: custom.shoulder_width,
            back_length: custom.back_length,
            bust_circ: custom.bust_circ,
            waist_circ: custom.waist_circ,
            hip_circ: custom.hip_circ,
            armhole_depth: custom.armhole_depth,
            upper_arm_circ: custom.upper_arm_circ,
            arm_length: custom.arm_length,
            apex_depth: custom.apex_depth,
            waist_to_hip: custom.waist_to_hip,
            top_padding: custom.top_padding,
            ease: custom.ease,
          },
        }
      }

      const torso = await fetchTorsoSvg(req)
      onTorsoLoaded(torso)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="torsoControls">
      <div className="torsoControls__row">
        <label className="torsoControls__label">
          Mode
          <select value={mode} onChange={(e) => setMode(e.target.value as Mode)} className="torsoControls__select">
            <option value="size">Craft Yarn Council size</option>
            <option value="custom">Custom</option>
          </select>
        </label>

        {mode === 'size' ? (
          <label className="torsoControls__label">
            Size
            <select value={size} onChange={(e) => setSize(e.target.value as TorsoSize)} className="torsoControls__select">
              {(['XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '5XL'] as TorsoSize[]).map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </label>
        ) : null}

        <button className="torsoControls__btn" onClick={generate} disabled={!canGenerate || isLoading}>
          {isLoading ? 'Generating…' : 'Generate torso'}
        </button>
      </div>

      {sizesLoaded ? <div className="torsoControls__hint">Sizes loaded: {Object.keys(sizesLoaded).join(', ')}</div> : null}

      {mode === 'custom' ? (
        <div className="torsoControls__grid">
          {(
            [
              ['shoulder_width', 'Shoulder width'],
              ['back_length', 'Back length'],
              ['bust_circ', 'Bust circumference'],
              ['waist_circ', 'Waist circumference'],
              ['hip_circ', 'Hip circumference'],
              ['armhole_depth', 'Armhole depth'],
              ['upper_arm_circ', 'Upper arm circumference'],
              ['arm_length', 'Arm length'],
              ['apex_depth', 'Apex depth'],
              ['waist_to_hip', 'Waist to hip'],
              ['top_padding', 'Top padding'],
              ['ease', 'Ease'],
            ] as const
          ).map(([key, label]) => (
            <label key={key} className="torsoControls__label">
              {label} (in)
              <input
                className="torsoControls__input"
                value={String(custom[key])}
                onChange={(e) =>
                  setCustom((prev) => ({
                    ...prev,
                    [key]: asNumber(e.target.value),
                  }))
                }
                inputMode="decimal"
              />
            </label>
          ))}
        </div>
      ) : null}

      {error ? <div className="torsoControls__error">{error}</div> : null}
    </div>
  )
}

