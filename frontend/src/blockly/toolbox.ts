import type * as Blockly from 'blockly/core'
import { BlockTypes } from './registerBlocks'

export const toolbox: Blockly.utils.toolbox.ToolboxDefinition = {
  kind: 'categoryToolbox',
  contents: [
    {
      kind: 'category',
      name: 'Charts',
      categorystyle: '210',
      contents: [
        {
          kind: 'block',
          type: BlockTypes.CHART,
        },
      ],
    },
    {
      kind: 'category',
      name: 'Commands',
      categorystyle: '120',
      contents: [
        {
          kind: 'block',
          type: BlockTypes.CAST_ON_START,
        },
        {
          kind: 'block',
          type: BlockTypes.CAST_ON_ADDITIONAL,
        },
        {
          kind: 'block',
          type: BlockTypes.ADD_ROW,
        },
        {
          kind: 'block',
          type: BlockTypes.ADD_ROUND,
        },
        {
          kind: 'block',
          type: BlockTypes.REPEAT_ROWS,
        },
        {
          kind: 'block',
          type: BlockTypes.REPEAT_ROUNDS,
        },
        {
          kind: 'block',
          type: BlockTypes.PLACE_MARKER,
        },
        {
          kind: 'block',
          type: BlockTypes.PLACE_ON_HOLD,
        },
        {
          kind: 'block',
          type: BlockTypes.PLACE_ON_NEEDLE,
        },
        {
          kind: 'block',
          type: BlockTypes.JOIN_CHARTS,
        },
      ],
    },
    {
      kind: 'category',
      name: 'Patterns',
      categorystyle: '65',
      contents: [
        {
          kind: 'block',
          type: BlockTypes.PATTERN_ROW,
        },
      ],
    },
  ],
}

