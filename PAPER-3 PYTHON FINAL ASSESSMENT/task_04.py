# Task 04 - Dependency Execution Planner

import heapq

def plan_execution(tasks, dependencies):

    task_list = list(tasks)
    if len(set(task_list)) != len(task_list):
        raise ValueError("Duplicate task names are not allowed")
    known = set(task_list)

    successors = {t: set() for t in known}
    indegree = {t: 0 for t in known}
    for pair in dependencies:
        if not isinstance(pair, (tuple, list)) or len(pair) != 2:
            raise ValueError(f"Invalid dependency (expected a pair): {pair!r}")
        before, after = pair
        for name in (before, after):
            if name not in known:
                raise ValueError(f"Unknown task in dependency: {name!r}")
        if after not in successors[before]:
            successors[before].add(after)
            indegree[after] += 1

    ready = [t for t, d in indegree.items() if d == 0]
    heapq.heapify(ready)
    order = []
    while ready:
        current = heapq.heappop(ready)
        order.append(current)
        for nxt in successors[current]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                heapq.heappush(ready, nxt)

    if len(order) != len(task_list):
        stuck = sorted(t for t, d in indegree.items() if d > 0)
        raise ValueError(f"Cycle detected involving tasks: {stuck}")
    return order


if __name__ == "__main__":
    print(plan_execution(["build", "test", "deploy"],
                         [("build", "test"), ("test", "deploy")]))
    print(plan_execution(["c", "a", "b"], []))
    try:
        plan_execution(["a", "b"], [("a", "b"), ("b", "a")])
    except ValueError as exc:
        print("Error:", exc)