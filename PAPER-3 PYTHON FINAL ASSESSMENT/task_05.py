# Task 05 - Expression Validator and Evaluator

BINARY_PREC = {"+": 1, "-": 1, "*": 2, "/": 2}


def tokenize(expression):
    if not isinstance(expression, str):
        raise TypeError("Expression must be a string")
    tokens, i = [], 0
    while i < len(expression):
        ch = expression[i]
        if ch.isspace():
            i += 1
        elif ch.isdigit():
            j = i
            while j < len(expression) and expression[j].isdigit():
                j += 1
            tokens.append(int(expression[i:j]))
            i = j
        elif ch in "+-*/()":
            tokens.append(ch)
            i += 1
        else:
            raise ValueError(f"Invalid character {ch!r} at position {i}")
    return tokens


def to_rpn(tokens):
    if not tokens:
        raise ValueError("Empty expression")
    output, ops = [], []
    expect_operand = True
    for tok in tokens:
        if isinstance(tok, int):
            if not expect_operand:
                raise ValueError("Missing operator before number")
            output.append(tok)
            expect_operand = False
        elif tok == "(":
            if not expect_operand:
                raise ValueError("Missing operator before '('")
            ops.append(tok)
        elif tok == ")":
            if expect_operand:
                raise ValueError("Unexpected ')' or empty parentheses")
            while ops and ops[-1] != "(":
                output.append(ops.pop())
            if not ops:
                raise ValueError("Mismatched parentheses")
            ops.pop()
        elif expect_operand:
            if tok not in "+-":
                raise ValueError(f"Unexpected operator {tok!r}")
            ops.append("neg" if tok == "-" else "pos")
        else:
            while (ops and ops[-1] != "("
                   and (ops[-1] in ("neg", "pos") or BINARY_PREC[ops[-1]] >= BINARY_PREC[tok])):
                output.append(ops.pop())
            ops.append(tok)
            expect_operand = True
    if expect_operand:
        raise ValueError("Expression ends with an operator")
    while ops:
        if ops[-1] == "(":
            raise ValueError("Mismatched parentheses")
        output.append(ops.pop())
    return output


def evaluate(expression):
    """Evaluate an integer expression; returns a float."""
    stack = []
    for tok in to_rpn(tokenize(expression)):
        if isinstance(tok, int):
            stack.append(float(tok))
        elif tok == "neg":
            stack.append(-stack.pop())
        elif tok == "pos":
            pass
        else:
            right, left = stack.pop(), stack.pop()
            if tok == "+":
                stack.append(left + right)
            elif tok == "-":
                stack.append(left - right)
            elif tok == "*":
                stack.append(left * right)
            else:
                if right == 0:
                    raise ZeroDivisionError("Division by zero")
                stack.append(left / right)
    return stack[0]


if __name__ == "__main__":
    print(evaluate("-(3 + 2) * 4 + 18 / 3"))
    print(evaluate("2 + 3 * 4"), evaluate("--5"), evaluate("2*-3"))
    for bad in ["", "2 +", "(1 + 2", "1 + 2)", "4 / 0", "2 $ 3", "3 4", "()"]:
        try:
            evaluate(bad)
        except (ValueError, ZeroDivisionError) as exc:
            print(f"{bad!r}: {type(exc).__name__}: {exc}")