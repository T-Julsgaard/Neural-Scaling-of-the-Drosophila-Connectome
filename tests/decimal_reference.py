"""Separate scalar, 50-digit equation oracle. Does not import production rules.

Keeps the author's separate M+/M- products before DAN rectification, in
contrast to the vectorized production value difference. This is an equation
adaptation, not execution of MATLAB or an independent human review.
"""
from decimal import Decimal, localcontext


def reference_trace(fixture):
    with localcontext() as ctx:
        ctx.prec = 50
        d = lambda x: Decimal(str(x))
        plus = list(map(d, fixture["initial_plus"]))
        minus = list(map(d, fixture["initial_minus"]))
        activities = [list(map(d, s)) for s in fixture["activities"]]
        gamma, rate, zero = d(fixture["gamma"]), d(fixture["eta"]), d(0)
        trace = []
        for choice, rewards in zip(fixture["choices"], fixture["rewards"]):
            maps = [sum(w * x for w, x in zip(plus, s)) for s in activities]
            mavs = [sum(w * x for w, x in zip(minus, s)) for s in activities]
            s = activities[choice]
            reward = d(rewards[choice])
            dap = max(zero, sum(gamma * x for x in s) - maps[choice] + mavs[choice] + reward)
            dav = max(zero, sum(gamma * x for x in s) - mavs[choice] + maps[choice] - reward)
            next_plus = [max(zero, w + rate * x * (dap - dav)) for w, x in zip(plus, s)]
            next_minus = [max(zero, w + rate * x * (dav - dap)) for w, x in zip(minus, s)]
            trace.append({"values": [float(a-b) for a, b in zip(maps, mavs)],
                          "d_plus": float(dap), "d_minus": float(dav),
                          "plus": list(map(float, next_plus)), "minus": list(map(float, next_minus))})
            plus, minus = next_plus, next_minus
        return trace
