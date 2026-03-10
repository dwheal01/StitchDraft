import { useEffect, useMemo, useRef } from 'react'
import * as Blockly from 'blockly/core'

import { compileWorkspaceToIr, type CompileResult } from '../blockly/compileToIr'
import { registerKnittingBlocks } from '../blockly/registerBlocks'
import { pastelTheme } from '../blockly/pastelTheme'
import { toolbox } from '../blockly/toolbox'

type Props = {
  onCompiled: (result: CompileResult) => void
}

export function BlocklyWorkspace({ onCompiled }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const workspaceRef = useRef<Blockly.WorkspaceSvg | null>(null)
  const onCompiledRef = useRef<Props['onCompiled']>(onCompiled)

  useEffect(() => {
    onCompiledRef.current = onCompiled
  }, [onCompiled])

  const injectOptions = useMemo<Blockly.BlocklyOptions>(
    () => ({
      toolbox,
      theme: pastelTheme,
      trashcan: true,
      // Use geras renderer; zelos can trigger a context menu DOM bug (MenuItem createDom / appendChild).
      renderer: 'geras',
      grid: { spacing: 20, length: 3, colour: '#b8c4d4', snap: true },
      zoom: { controls: true, wheel: true, startScale: 0.9, maxScale: 2, minScale: 0.3 },
    }),
    [],
  )

  useEffect(() => {
    registerKnittingBlocks()

    const el = containerRef.current
    if (!el) return

    const workspace = Blockly.inject(el, injectOptions)
    workspaceRef.current = workspace

    const emit = () => onCompiledRef.current(compileWorkspaceToIr(workspace))

    const listener = (e: Blockly.Events.Abstract) => {
      if (
        e.type === Blockly.Events.BLOCK_CHANGE ||
        e.type === Blockly.Events.BLOCK_CREATE ||
        e.type === Blockly.Events.BLOCK_DELETE ||
        e.type === Blockly.Events.BLOCK_MOVE
      ) {
        emit()
      }
    }

    workspace.addChangeListener(listener)
    emit()

    const resizeObserver = new ResizeObserver(() => {
      Blockly.svgResize(workspace)
    })
    resizeObserver.observe(el)

    return () => {
      resizeObserver.disconnect()
      workspace.removeChangeListener(listener)
      workspace.dispose()
      workspaceRef.current = null
    }
  }, [injectOptions])

  return <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
}

