from abnf import Node, NodeVisitor

import http_headers.visitors.rfc9110.challenge as challenge


class WWWAuthenticateVisitor(NodeVisitor):
    visit_challenge = challenge.ChallengeVisitor()

    def visit_www_authenticate(
        self, node: Node
    ) -> list[challenge.TokenChallenge | challenge.AuthParamChallenge]:
        return list(filter(None, map(self.visit, node.children)))
