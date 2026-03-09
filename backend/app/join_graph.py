from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

from backend.app.ir_models import ChartProgram, JoinCharts


def build_join_graph(programs_by_name: Dict[str, ChartProgram]) -> Dict[str, Set[str]]:
    """
    Build a directed graph of chart join dependencies.

    Edge: left_chart_name -> right_chart_name for each JoinCharts command.
    """
    graph: Dict[str, Set[str]] = {name: set() for name in programs_by_name.keys()}

    for program in programs_by_name.values():
        for cmd in program.commands:
            if isinstance(cmd, JoinCharts):
                # left_chart_name joins right_chart_name
                graph.setdefault(cmd.left_chart_name, set()).add(cmd.right_chart_name)
                # Ensure right chart appears in graph even if it has no outgoing joins
                graph.setdefault(cmd.right_chart_name, set())

    return graph


def validate_join_graph(
    programs_by_name: Dict[str, ChartProgram],
) -> Tuple[Optional[List[str]], Optional[List[str]]]:
    """
    Validate the join dependency graph.

    Returns:
        (order, None) if the graph is acyclic, where order is a topological
        ordering of chart names.
        (None, cycle) if a cycle is detected, where cycle is a list of chart
        names forming the cycle (e.g. ['back', 'sleeve', 'back']).
    """
    graph = build_join_graph(programs_by_name)

    # If there are no joins at all, treat the original IR order as the order.
    if all(not targets for targets in graph.values()):
        return list(programs_by_name.keys()), None

    order: List[str] = []
    visiting: Set[str] = set()
    visited: Set[str] = set()
    cycle: List[str] = []

    def dfs(node: str, stack: List[str]) -> bool:
        """
        Depth-first search.

        Returns True if a cycle is found (and fills 'cycle'), False otherwise.
        """
        if node in visited:
            return False
        if node in visiting:
            # Found a cycle; extract the cycle path from the stack.
            if node in stack:
                idx = stack.index(node)
                cycle.extend(stack[idx:] + [node])
            else:
                cycle.extend(stack + [node])
            return True

        visiting.add(node)
        stack.append(node)

        for neighbor in graph.get(node, ()):
            if dfs(neighbor, stack):
                return True

        stack.pop()
        visiting.remove(node)
        visited.add(node)
        order.append(node)
        return False

    for name in graph.keys():
        if name not in visited:
            if dfs(name, []):
                return None, cycle

    # Post-order DFS yields dependencies-first: charts with no outgoing edges
    # (leaf nodes) are added first, so when we iterate this order, any chart
    # referenced in a join is built before the chart that joins it.
    return order, None

