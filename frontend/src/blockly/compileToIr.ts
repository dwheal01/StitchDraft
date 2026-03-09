import type * as Blockly from 'blockly/core'
import { IR_VERSION, type ChartProgram, type KnittingIR, type StartSide } from '../ir/types'
import { BlockTypes } from './registerBlocks'

export type CompileResult = {
  ir: KnittingIR
  errors: string[]
}

function asNumber(value: unknown): number {
  const n = typeof value === 'number' ? value : Number(value)
  return Number.isFinite(n) ? n : 0
}

export function compileWorkspaceToIr(workspace: Blockly.Workspace): CompileResult {
  const errors: string[] = []

  const topBlocks = workspace.getTopBlocks(true)
  const chartBlocks = topBlocks.filter((b) => b.type === BlockTypes.CHART)

  if (chartBlocks.length === 0) {
    errors.push('Add a “Chart” block to generate IR.')
  }

  const charts: ChartProgram[] = chartBlocks.map((chartBlock) => {
    const name = String(chartBlock.getFieldValue('NAME') ?? '').trim() || 'chart'
    const start_side = (chartBlock.getFieldValue('START_SIDE') ?? 'RS') as StartSide
    const sts = asNumber(chartBlock.getFieldValue('STS'))
    const rows = asNumber(chartBlock.getFieldValue('ROWS'))

    const commands: ChartProgram['commands'] = []
    let cmd = chartBlock.getInputTargetBlock('COMMANDS')
    while (cmd) {
      switch (cmd.type) {
        case BlockTypes.CAST_ON_START: {
          const count = asNumber(cmd.getFieldValue('COUNT'))
          commands.push({ op: 'cast_on_start', count } as const)
          break
        }
        case BlockTypes.CAST_ON_ADDITIONAL: {
          const count = asNumber(cmd.getFieldValue('COUNT'))
          if (count >= 1) {
            commands.push({ op: 'cast_on_additional', count } as const)
          } else {
            errors.push('Cast on additional requires count >= 1.')
          }
          break
        }
        case BlockTypes.ADD_ROW: {
          const pattern = String(cmd.getFieldValue('PATTERN') ?? '').trim()
          commands.push({ op: 'add_row', pattern } as const)
          break
        }
        case BlockTypes.REPEAT_ROWS: {
          const times = asNumber(cmd.getFieldValue('TIMES'))
          const patterns: string[] = []
          let p = cmd.getInputTargetBlock('PATTERNS')
          while (p) {
            if (p.type === BlockTypes.PATTERN_ROW || p.type === BlockTypes.ADD_ROW) {
              const pat = String(p.getFieldValue('PATTERN') ?? '').trim()
              if (pat) patterns.push(pat)
            } else {
              errors.push(`Unsupported pattern block inside repeat: ${p.type}`)
            }
            p = p.getNextBlock()
          }
          if (patterns.length === 0) {
            errors.push('Repeat Rows requires at least one pattern block.')
          }
          commands.push({ op: 'repeat_rows', times, patterns } as const)
          break
        }
        case BlockTypes.ADD_ROUND: {
          const pattern = String(cmd.getFieldValue('PATTERN') ?? '').trim()
          commands.push({ op: 'add_round', pattern } as const)
          break
        }
        case BlockTypes.REPEAT_ROUNDS: {
          const times = asNumber(cmd.getFieldValue('TIMES'))
          const patterns: string[] = []
          let p = cmd.getInputTargetBlock('PATTERNS')
          while (p) {
            if (p.type === BlockTypes.PATTERN_ROW || p.type === BlockTypes.ADD_ROW) {
              const pat = String(p.getFieldValue('PATTERN') ?? '').trim()
              if (pat) patterns.push(pat)
            } else {
              errors.push(`Unsupported pattern block inside repeat: ${p.type}`)
            }
            p = p.getNextBlock()
          }
          if (patterns.length === 0) {
            errors.push('Repeat Rounds requires at least one pattern block.')
          }
          commands.push({ op: 'repeat_rounds', times, patterns } as const)
          break
        }
        case BlockTypes.PLACE_MARKER: {
          const side = (cmd.getFieldValue('SIDE') ?? 'RS') as StartSide
          const position = asNumber(cmd.getFieldValue('POSITION'))
          commands.push({ op: 'place_marker', side, position } as const)
          break
        }
        case BlockTypes.PLACE_ON_HOLD: {
          const name = String(cmd.getFieldValue('NAME') ?? 'last').trim() || 'last'
          commands.push({ op: 'place_on_hold', name } as const)
          break
        }
        case BlockTypes.PLACE_ON_NEEDLE: {
          const join_side = (cmd.getFieldValue('JOIN_SIDE') ?? 'RS') as StartSide
          const from_hold = String(cmd.getFieldValue('FROM_HOLD') ?? 'last').trim() || 'last'
          commands.push({ op: 'place_on_needle', join_side, from_hold, source: from_hold } as const)
          break
        }
        case BlockTypes.JOIN_CHARTS: {
          const right_chart_name = String(cmd.getFieldValue('CHART_NAME') ?? '').trim()
          const firstPatternFrom = (inputName: string) => {
            const p = cmd.getInputTargetBlock(inputName)
            if (p && (p.type === BlockTypes.PATTERN_ROW || p.type === BlockTypes.ADD_ROW)) {
              return String(p.getFieldValue('PATTERN') ?? '').trim() || 'repeat(k1)'
            }
            return 'repeat(k1)'
          }
          const pattern1 = firstPatternFrom('PATTERN1')
          const pattern2 = firstPatternFrom('PATTERN2')
          if (!right_chart_name) {
            errors.push('Join & knit requires a chart name to join.')
          } else {
            commands.push({ op: 'join_and_knit', right_chart_name, pattern1, pattern2 } as const)
          }
          break
        }
        default:
          errors.push(`Unsupported command block: ${cmd.type}`)
      }
      cmd = cmd.getNextBlock()
    }

    return { name, start_side, sts, rows, commands }
  })

  return {
    ir: {
      version: IR_VERSION,
      charts,
    },
    errors,
  }
}

