import * as Blockly from 'blockly/core'

const CHART_BLOCK_TYPE = 'chart_create'
const CMD_CAST_ON_START_TYPE = 'cmd_cast_on_start'
const CMD_CAST_ON_ADDITIONAL_TYPE = 'cmd_cast_on_additional'
const CMD_ADD_ROW_TYPE = 'cmd_add_row'
const CMD_REPEAT_ROWS_TYPE = 'cmd_repeat_rows'
const CMD_ADD_ROUND_TYPE = 'cmd_add_round'
const CMD_REPEAT_ROUNDS_TYPE = 'cmd_repeat_rounds'
const CMD_PLACE_MARKER_TYPE = 'cmd_place_marker'
const CMD_PLACE_ON_HOLD_TYPE = 'cmd_place_on_hold'
const CMD_PLACE_ON_NEEDLE_TYPE = 'cmd_place_on_needle'
const CMD_JOIN_CHARTS_TYPE = 'cmd_join_charts'
const PATTERN_ROW_TYPE = 'pattern_row'

export const BlockTypes = {
  CHART: CHART_BLOCK_TYPE,
  CAST_ON_START: CMD_CAST_ON_START_TYPE,
  CAST_ON_ADDITIONAL: CMD_CAST_ON_ADDITIONAL_TYPE,
  ADD_ROW: CMD_ADD_ROW_TYPE,
  REPEAT_ROWS: CMD_REPEAT_ROWS_TYPE,
  ADD_ROUND: CMD_ADD_ROUND_TYPE,
  REPEAT_ROUNDS: CMD_REPEAT_ROUNDS_TYPE,
  PLACE_MARKER: CMD_PLACE_MARKER_TYPE,
  PLACE_ON_HOLD: CMD_PLACE_ON_HOLD_TYPE,
  PLACE_ON_NEEDLE: CMD_PLACE_ON_NEEDLE_TYPE,
  JOIN_CHARTS: CMD_JOIN_CHARTS_TYPE,
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
      type: CMD_CAST_ON_ADDITIONAL_TYPE,
      message0: 'cast on additional %1',
      args0: [
        {
          type: 'field_number',
          name: 'COUNT',
          value: 1,
          min: 1,
          precision: 1,
        },
      ],
      previousStatement: 'COMMAND',
      nextStatement: 'COMMAND',
      colour: 120,
      tooltip: 'Cast on more stitches after the first row/round (e.g. after add round).',
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
    {
      type: CMD_ADD_ROUND_TYPE,
      message0: 'add round pattern %1',
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
      tooltip: 'Add a round using the engine pattern DSL.',
      helpUrl: '',
    },
    {
      type: CMD_REPEAT_ROUNDS_TYPE,
      message0: 'repeat rounds %1 times %2 patterns %3',
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
      tooltip: 'Repeat a sequence of round patterns.',
      helpUrl: '',
    },
    {
      type: CMD_PLACE_MARKER_TYPE,
      message0: 'place marker side %1 position %2',
      args0: [
        {
          type: 'field_dropdown',
          name: 'SIDE',
          options: [
            ['RS', 'RS'],
            ['WS', 'WS'],
          ],
        },
        {
          type: 'field_number',
          name: 'POSITION',
          value: 0,
          min: 0,
          precision: 1,
        },
      ],
      previousStatement: 'COMMAND',
      nextStatement: 'COMMAND',
      colour: 40,
      tooltip: 'Place a marker at the given position on RS/WS.',
      helpUrl: '',
    },
    {
      type: CMD_PLACE_ON_HOLD_TYPE,
      message0: 'place on hold name %1',
      args0: [
        {
          type: 'field_input',
          name: 'NAME',
          text: 'last',
        },
      ],
      previousStatement: 'COMMAND',
      nextStatement: 'COMMAND',
      colour: 40,
      tooltip: 'Place unconsumed stitches on hold. Name the slot (e.g. left, right) to use with place on needle.',
      helpUrl: '',
    },
    {
      type: CMD_PLACE_ON_NEEDLE_TYPE,
      message0: 'place on needle from hold %1 join side %2 cast on between %3',
      args0: [
        {
          type: 'field_input',
          name: 'FROM_HOLD',
          text: 'last',
        },
        {
          type: 'field_dropdown',
          name: 'JOIN_SIDE',
          options: [
            ['RS', 'RS'],
            ['WS', 'WS'],
          ],
        },
        {
          type: 'field_number',
          name: 'CAST_ON_BETWEEN',
          value: 0,
          min: 0,
          max: 1000,
        },
      ],
      previousStatement: 'COMMAND',
      nextStatement: 'COMMAND',
      colour: 40,
      tooltip: 'Place stitches from the named hold back on the needle. Optionally cast on N stitches between (e.g. 4 to rejoin with a gap).',
      helpUrl: '',
    },
    {
      type: CMD_JOIN_CHARTS_TYPE,
      message0: 'join chart %1 work right with %2',
      args0: [
        {
          type: 'field_input',
          name: 'CHART_NAME',
          text: 'chart1',
        },
        {
          type: 'input_statement',
          name: 'PATTERN',
          check: 'PATTERN',
        },
      ],
      previousStatement: 'COMMAND',
      nextStatement: 'COMMAND',
      colour: 40,
      tooltip: 'Join the named chart to the right of this chart. The pattern states how to work the new (right) chart\'s stitches (e.g. repeat(k1) or k2, inc, repeat(k1)).',
      helpUrl: '',
    },
  ])
}

