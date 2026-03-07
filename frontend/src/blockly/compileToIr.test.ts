/**
 * Compiler tests for IR generation, including Milestone D blocks (holds, join).
 * Uses a mock workspace to avoid Blockly's DOM/canvas requirements in Node.
 */
import { describe, it, expect } from 'vitest'
import { compileWorkspaceToIr } from './compileToIr'
import { BlockTypes } from './registerBlocks'

type MockBlock = {
  type: string
  getFieldValue: (name: string) => string | number | undefined
  getInputTargetBlock: () => MockBlock | null
  getNextBlock: () => MockBlock | null
}

/** Minimal mock for a Blockly block - compiler only needs type, getFieldValue, getInputTargetBlock, getNextBlock */
function mockBlock(
  type: string,
  fields: Record<string, string | number> = {},
  inputBlock?: MockBlock | null,
  nextBlock?: MockBlock | null
): MockBlock {
  return {
    type,
    getFieldValue: (name: string) => fields[name],
    getInputTargetBlock: () => inputBlock ?? null,
    getNextBlock: () => nextBlock ?? null,
  }
}

/** Build a chain of command blocks */
function mockCommandChain(commands: Array<{ type: string; fields?: Record<string, string | number>; patterns?: string[]; times?: number }>) {
  let prev: MockBlock | null = null
  for (let i = commands.length - 1; i >= 0; i--) {
    const cmd = commands[i]
    const block = mockBlock(
      cmd.type,
      {
        ...cmd.fields,
        ...(cmd.times !== undefined && { TIMES: cmd.times }),
      },
      cmd.patterns
        ? (() => {
            let pPrev: MockBlock | null = null
            for (let j = cmd.patterns!.length - 1; j >= 0; j--) {
              const p = mockBlock(BlockTypes.PATTERN_ROW, { PATTERN: cmd.patterns![j] }, null, pPrev)
              pPrev = p
            }
            return pPrev
          })()
        : undefined,
      prev
    )
    prev = block
  }
  return prev
}

/** Mock workspace with one chart */
function mockWorkspace(chartName: string, commands: Array<{ type: string; fields?: Record<string, string | number>; patterns?: string[]; times?: number }>) {
  const commandChain = mockCommandChain(commands)
  const chartBlock = mockBlock(
    BlockTypes.CHART,
    { NAME: chartName, START_SIDE: 'RS', STS: 22, ROWS: 28 },
    commandChain
  )
  return {
    getTopBlocks: () => [chartBlock],
  }
}

/** Mock workspace with multiple charts */
function mockWorkspaceMulti(
  charts: Array<{ name: string; commands: Array<{ type: string; fields?: Record<string, string | number>; patterns?: string[]; times?: number }> }>
) {
  const chartBlocks = charts.map((c) => {
    const commandChain = mockCommandChain(c.commands)
    return mockBlock(BlockTypes.CHART, { NAME: c.name, START_SIDE: 'RS', STS: 22, ROWS: 28 }, commandChain)
  })
  return {
    getTopBlocks: () => chartBlocks,
  }
}

describe('compileToIr', () => {
  it('compiles place_on_hold to IR', () => {
    const workspace = mockWorkspace('hold_chart', [
      { type: BlockTypes.CAST_ON_START, fields: { COUNT: 10 } },
      { type: BlockTypes.ADD_ROW, fields: { PATTERN: 'repeat(k1)' } },
      { type: BlockTypes.PLACE_ON_HOLD },
    ])

    const result = compileWorkspaceToIr(workspace as never)
    expect(result.errors).toHaveLength(0)
    const chart = result.ir.charts[0]
    expect(chart.commands).toContainEqual({ op: 'place_on_hold' })
  })

  it('compiles place_on_needle with join_side to IR', () => {
    const workspace = mockWorkspace('needle_chart', [
      { type: BlockTypes.CAST_ON_START, fields: { COUNT: 10 } },
      { type: BlockTypes.PLACE_ON_HOLD },
      { type: BlockTypes.PLACE_ON_NEEDLE, fields: { JOIN_SIDE: 'WS' } },
    ])

    const result = compileWorkspaceToIr(workspace as never)
    expect(result.errors).toHaveLength(0)
    const chart = result.ir.charts[0]
    expect(chart.commands).toContainEqual({
      op: 'place_on_needle',
      join_side: 'WS',
      source: 'last',
    })
  })

  it('compiles join charts to IR', () => {
    const workspace = mockWorkspaceMulti([
      {
        name: 'left_chart',
        commands: [
          { type: BlockTypes.CAST_ON_START, fields: { COUNT: 10 } },
          {
            type: BlockTypes.JOIN_CHARTS,
            fields: { CHART_NAME: 'right_chart' },
          },
        ],
      },
      {
        name: 'right_chart',
        commands: [{ type: BlockTypes.CAST_ON_START, fields: { COUNT: 10 } }],
      },
    ])

    const result = compileWorkspaceToIr(workspace as never)
    expect(result.errors).toHaveLength(0)
    const leftChart = result.ir.charts.find((c) => c.name === 'left_chart')
    expect(leftChart?.commands).toContainEqual({
      op: 'join',
      left_chart_name: 'left_chart',
      right_chart_name: 'right_chart',
    })
  })
})
