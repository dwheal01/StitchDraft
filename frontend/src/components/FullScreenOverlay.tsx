import { useEffect, type ReactNode } from 'react'

type Props = {
  open: boolean
  onClose: () => void
  title?: string
  children: ReactNode
}

export function FullScreenOverlay({ open, onClose, title, children }: Props) {
  useEffect(() => {
    if (!open) return
    const handleKeyDown = (evt: KeyboardEvent) => {
      if (evt.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [open, onClose])

  if (!open) return null

  return (
    <div className="fullScreenOverlay" role="dialog" aria-modal="true" aria-label={title ?? 'Full screen'}>
      <div className="fullScreenOverlay__backdrop" onClick={onClose} aria-hidden />
      <div className="fullScreenOverlay__panel">
        <header className="fullScreenOverlay__header">
          {title ? <span className="fullScreenOverlay__title">{title}</span> : null}
          <button type="button" className="fullScreenOverlay__close" onClick={onClose}>
            Close
          </button>
        </header>
        <div className="fullScreenOverlay__content">{children}</div>
      </div>
    </div>
  )
}
