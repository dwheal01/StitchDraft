import * as Blockly from 'blockly/core'

const CHART_BLOCK_TYPE = 'chart_create'
const CMD_CAST_ON_START_TYPE = 'cmd_cast_on_start'
const CMD_ADD_ROW_TYPE = 'cmd_add_row'
const CMD_REPEAT_ROWS_TYPE = 'cmd_repeat_rows'
const PATTERN_ROW_TYPE = 'pattern_row'

export const BlockTypes = {
  CHART: CHART_BLOCK_TYPE,
  CAST_ON_START: CMD_CAST_ON_START_TYPE,
  ADD_ROW: CMD_ADD_ROW_TYPE,
  REPEAT_ROWS: CMD_REPEAT_ROWS_TYPE,
  PATTERN_ROW: PATTERN_ROW_TYPE,
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
          check: 'COMMAND',
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
      previousStatement: 'COMMAND',
      nextStatement: 'COMMAND',
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
      previousStatement: 'COMMAND',
      nextStatement: 'COMMAND',
      colour: 120,
      tooltip: 'Add a flat row using the engine pattern DSL.',
      helpUrl: '',
    },
    {
      type: PATTERN_ROW_TYPE,
      message0: 'pattern %1',
      args0: [
        {
          type: 'field_input',
          name: 'PATTERN',
          text: 'repeat(k1)',
        },
      ],
      previousStatement: 'PATTERN',
      nextStatement: 'PATTERN',
      colour: 65,
      tooltip: 'A row pattern (used inside repeat blocks).',
      helpUrl: '',
    },
    {
      type: CMD_REPEAT_ROWS_TYPE,
      message0: 'repeat rows %1 times %2 patterns %3',
      args0: [
        {
          type: 'field_number',
          name: 'TIMES',
          value: 2,
          min: 0,
          precision: 1,
        },
        { type: 'input_dummy' },
        {
          type: 'input_statement',
          name: 'PATTERNS',
          check: 'PATTERN',
        },
      ],
      previousStatement: 'COMMAND',
      nextStatement: 'COMMAND',
      colour: 120,
      tooltip: 'Repeat a sequence of row patterns.',
      helpUrl: '',
    },
  ])
}

