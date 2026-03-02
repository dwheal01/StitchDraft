import * as Blockly from 'blockly/core'

const CHART_BLOCK_TYPE = 'chart_create'
const CMD_CAST_ON_START_TYPE = 'cmd_cast_on_start'
const CMD_ADD_ROW_TYPE = 'cmd_add_row'

export const BlockTypes = {
  CHART: CHART_BLOCK_TYPE,
  CAST_ON_START: CMD_CAST_ON_START_TYPE,
  ADD_ROW: CMD_ADD_ROW_TYPE,
} as const

export function registerKnittingBlocks(): void {
  // Idempotent registration (React StrictMode mounts twice in dev).
  if (Blockly.Blocks[CHART_BLOCK_TYPE]) return

  Blockly.defineBlocksWithJsonArray([
    {
      type: CHART_BLOCK_TYPE,
      message0: 'Chart %1 start side %2 sts %3 rows %4 %5 commands %6',
      args0: [
        {
          type: 'field_input',
          name: 'NAME',
          text: 'chart',
        },
        {
          type: 'field_dropdown',
          name: 'START_SIDE',
          options: [
            ['RS', 'RS'],
            ['WS', 'WS'],
          ],
        },
        {
          type: 'field_number',
          name: 'STS',
          value: 22,
          min: 1,
          precision: 1,
        },
        {
          type: 'field_number',
          name: 'ROWS',
          value: 28,
          min: 1,
          precision: 1,
        },
        { type: 'input_dummy' },
        {
          type: 'input_statement',
          name: 'COMMANDS',
        },
      ],
      colour: 210,
      tooltip: 'Define a chart/piece, then attach commands.',
      helpUrl: '',
    },
    {
      type: CMD_CAST_ON_START_TYPE,
      message0: 'cast on start %1',
      args0: [
        {
          type: 'field_number',
          name: 'COUNT',
          value: 10,
          min: 0,
          precision: 1,
        },
      ],
      previousStatement: null,
      nextStatement: null,
      colour: 120,
      tooltip: 'Cast on the initial stitch count for the chart.',
      helpUrl: '',
    },
    {
      type: CMD_ADD_ROW_TYPE,
      message0: 'add row pattern %1',
      args0: [
        {
          type: 'field_input',
          name: 'PATTERN',
          text: 'repeat(k1)',
        },
      ],
      previousStatement: null,
      nextStatement: null,
      colour: 120,
      tooltip: 'Add a flat row using the engine pattern DSL.',
      helpUrl: '',
    },
  ])
}

