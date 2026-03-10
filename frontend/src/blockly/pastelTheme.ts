import * as Blockly from 'blockly/core'

/**
 * Pastel dashboard theme for Blockly – matches the app's soft pastel palette.
 * Extends Classic and overrides workspace, toolbox, flyout, and block colours.
 */
export const pastelTheme = Blockly.Theme.defineTheme('pastel', {
  name: 'pastel',
  base: Blockly.Themes.Classic,
  componentStyles: {
    workspaceBackgroundColour: '#e9f5ff',
    toolboxBackgroundColour: '#f6f4ff',
    toolboxForegroundColour: '#111827',
    flyoutBackgroundColour: '#ffffff',
    flyoutForegroundColour: '#111827',
    flyoutOpacity: 1,
    scrollbarColour: '#b8c4d4',
    scrollbarOpacity: 0.7,
    insertionMarkerColour: '#7c6cf6',
    insertionMarkerOpacity: 0.4,
    cursorColour: '#7c6cf6',
    markerColour: '#5fb7ff',
  },
  blockStyles: {
    /* Charts – soft blue */
    '210': {
      colourPrimary: '#7eb8f0',
      colourSecondary: '#a8d4f8',
      colourTertiary: '#5a9ad4',
    },
    /* Commands (cast on, add row, repeat, etc.) – soft green */
    '120': {
      colourPrimary: '#70d090',
      colourSecondary: '#a8e6b8',
      colourTertiary: '#4aab6a',
    },
    /* Pattern row – soft purple */
    '65': {
      colourPrimary: '#b8a8e8',
      colourSecondary: '#d4c8f0',
      colourTertiary: '#8a7ac8',
    },
    /* Place marker, hold, join – soft purple */
    '40': {
      colourPrimary: '#a890e0',
      colourSecondary: '#c8b8f0',
      colourTertiary: '#7a6ab8',
    },
  },
  categoryStyles: {
    '210': { colour: '#7eb8f0' },
    '120': { colour: '#70d090' },
    '65': { colour: '#b8a8e8' },
    '40': { colour: '#a890e0' },
  },
})
