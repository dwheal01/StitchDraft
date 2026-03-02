import type * as Blockly from 'blockly/core'
import { BlockTypes } from './registerBlocks'

export const toolbox: Blockly.utils.toolbox.ToolboxDefinition = {
  kind: 'categoryToolbox',
  contents: [
    {
      kind: 'category',
      name: 'Charts',
      colour: '210',
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
      colour: '120',
      contents: [
        {
          kind: 'block',
          type: BlockTypes.CAST_ON_START,
        },
        {
          kind: 'block',
          type: BlockTypes.ADD_ROW,
        },
      ],
    },
  ],
}

