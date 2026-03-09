export const IR_VERSION = '0.1' as const

export type StartSide = 'RS' | 'WS'

export type CommandOp =
  | 'cast_on_start'
  | 'cast_on_additional'
  | 'add_row'
  | 'add_round'
  | 'repeat_rows'
  | 'repeat_rounds'
  | 'place_marker'
  | 'place_on_hold'
  | 'place_on_needle'
  | 'join'
  | 'join_and_knit'

export type KnittingCommand =
  | { op: 'cast_on_start'; count: number }
  | { op: 'cast_on_additional'; count: number }
  | { op: 'add_row'; pattern: string }
  | { op: 'add_round'; pattern: string }
  | { op: 'repeat_rows'; times: number; patterns: string[] }
  | { op: 'repeat_rounds'; times: number; patterns: string[] }
  | { op: 'place_marker'; side: StartSide; position: number }
  | { op: 'place_on_hold'; name?: string }
  | { op: 'place_on_needle'; join_side: StartSide; from_hold?: string; source?: string; cast_on_between?: number }
  | { op: 'join'; left_chart_name: string; right_chart_name: string; right_pattern?: string }
  | { op: 'join_and_knit'; right_chart_name: string; pattern1: string; pattern2: string }

export type ChartProgram = {
  name: string
  start_side: StartSide
  sts: number
  rows: number
  commands: KnittingCommand[]
}

export type KnittingIR = {
  version: typeof IR_VERSION
  charts: ChartProgram[]
}

