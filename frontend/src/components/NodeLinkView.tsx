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
  links: LinkVm[]
}

export function NodeLinkView({ nodes, links }: Props) {
  if (!nodes.length) {
    return <div className="nodeLinkEmpty">No stitches to display yet.</div>
  }

  const minX = Math.min(...nodes.map((n) => n.x))
  const maxX = Math.max(...nodes.map((n) => n.x))
  const minY = Math.min(...nodes.map((n) => n.y))
  const maxY = Math.max(...nodes.map((n) => n.y))

  const padding = 40
  const width = Math.max(200, maxX - minX + padding * 2)
  const height = Math.max(150, maxY - minY + padding * 2)

  const viewBox = `${minX - padding} ${minY - padding} ${width} ${height}`

  const byId = new Map(nodes.map((n) => [n.id, n]))

  const colorForType = (t: string) => {
    const key = t.toLowerCase()
    if (key === 'k') return '#4A90E2'
    if (key === 'p') return '#524be3'
    if (key === 'inc') return '#85DCB0'
    if (key === 'dec') return '#E27D60'
    if (key === 'bo') return '#111827'
    if (key === 'strand') return '#9ca3af'
    return '#6b7280'
  }

  return (
    <div className="nodeLinkWrapper">
      <svg className="nodeLinkSvg" viewBox={viewBox} preserveAspectRatio="xMidYMid meet">
        <g className="nodeLinkLinks">
          {links.map((l) => {
            const s = byId.get(l.source)
            const t = byId.get(l.target)
            if (!s || !t) return null
            return (
              <line
                key={`${l.source}->${l.target}`}
                x1={s.x}
                y1={s.y}
                x2={t.x}
                y2={t.y}
                stroke="#9ca3af"
                strokeWidth={1}
              />
            )
          })}
        </g>
        <g className="nodeLinkNodes">
          {nodes.map((n) => (
            <circle
              key={n.id}
              cx={n.x}
              cy={n.y}
              r={n.type === 'k' || n.type === 'p' || n.type === 'inc' || n.type === 'dec' ? 5 : 3}
              fill={colorForType(n.type)}
              stroke={n.type === 'strand' ? 'none' : '#111827'}
              strokeWidth={0.5}
              opacity={n.type === 'strand' ? 0.0 : 1}
            />
          ))}
        </g>
      </svg>
    </div>
  )
}

