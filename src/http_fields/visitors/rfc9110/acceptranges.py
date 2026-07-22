from abnf import Node, NodeVisitor

import http_fields.visitors.rfc9110.rangeunit as rangeunit


class AcceptRangesVisitor(NodeVisitor):
    visit_range_unit = rangeunit.RangeUnitVisitor()

    def visit_acceptable_ranges(self, node: Node) -> list[rangeunit.RangeUnit]:
        return list(filter(None, map(self.visit, node.children)))

    def visit_accept_ranges(self, node: Node) -> list[rangeunit.RangeUnit]:
        return next(filter(None, map(self.visit, node.children)))
