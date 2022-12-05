import re
import operator
import inspect
from collections import namedtuple
from string import ascii_lowercase, ascii_uppercase
import itertools
import random

# Regular expression matching optional whitespace followed by a token
# (if group 1 matches) or an error (if group 2 matches)
TOKEN_RE = re.compile(r'\s*(?:([A-Za-z01()~∧∨→↔])|(\S))')

# Token indicating the end of the input string.
TOKEN_END = '\n'

# Tokens representing Boolean constants (0=False, 1=True).
CONSTANTS = '01'

# Tokens representing variables.
VARIABLES = set(ascii_lowercase) | set(ascii_uppercase)

# Map from unary operator name to function.
UNARY_OPERATORS = {
    '~': operator.not_,
}

# Map from binary operator name to function.
BINARY_OPERATORS = {
    '∧': operator.and_,
    '∨': operator.or_,
    '→': lambda a, b: not a or b,
    '↔': operator.eq,

}

Constant = namedtuple('Constant', 'value')
Variable = namedtuple('Variable', 'name')
UnaryOp = namedtuple('UnaryOp', 'op operand')
BinaryOp = namedtuple('BinaryOp', 'left op right')

#########################################################################
#                            Functions                                  #
#########################################################################
def checkAmbiguity(s):
    ambiguityCount = 0
    startCheck = True
    for match in TOKEN_RE.finditer(s):
        token, error = match.groups()
        if token:
            if token == '(':
                ambiguityCount = 0
            elif token == ')':
                ambiguityCount = 0
            else:
                ambiguityCount = ambiguityCount + 1
        else:
            raise SyntaxError("Unexpected character {!r}".format(error))
        if ambiguityCount > 3:
            return True
    return False

def tokenize(s):
    """Generate tokens from the string s, followed by Token_END."""
    for match in TOKEN_RE.finditer(s):
        token, error = match.groups()
        if token:
            yield token
        else:
            raise SyntaxError("Unexpected character {!r}".format(error))
    yield TOKEN_END

def parse(s):
    """Parse s as a Boolean expression and return the parse tree."""
    tokens = tokenize(s)        # Stream of tokens.
    token = next(tokens)        # The current token.

    def error(expected):
        # Current token failed to match, so raise syntax error.
        raise SyntaxError("Expected {} but found {!r}"
                          .format(expected, token))

    def match(valid_tokens):
        # If the current token is found in valid_tokens, consume it
        # and return True. Otherwise, return False.
        nonlocal token
        if token in valid_tokens:
            token = next(tokens)
            return True
        else:
            return False

    def term():
        # Parse a <Term> starting at the current token.
        t = token
        if match(VARIABLES):
            return Variable(name=t)
        elif match(CONSTANTS):
            return Constant(value=(t == '1'))
        elif match('('):
            tree = disjunction()
            if match(')'):
                return tree
            else:
                error("')'")
        else:
            error("term")

    def unary_expr():
        # Parse a <UnaryExpr> starting at the current token.
        t = token
        if match('~'):
            operand = unary_expr()
            return UnaryOp(op=UNARY_OPERATORS[t], operand=operand)
        else:
            return term()

    def binary_expr(parse_left, valid_operators, parse_right):
        # Parse a binary expression starting at the current token.
        # Call parse_left to parse the left operand; the operator must
        # be found in valid_operators; call parse_right to parse the
        # right operand.
        left = parse_left()
        t = token
        if match(valid_operators):
            right = parse_right()
            return BinaryOp(left=left, op=BINARY_OPERATORS[t], right=right)
        else:
            return left

    def implication():
        # Parse an <Implication> starting at the current token.
        return binary_expr(unary_expr, '→↔', implication)

    def conjunction():
        # Parse a <Conjunction> starting at the current token.
        return binary_expr(implication, '∧', conjunction)

    def disjunction():
        # Parse a <Disjunction> starting at the current token.
        return binary_expr(conjunction, '∨', disjunction)

    tree = disjunction()
    if token != TOKEN_END:
        error("end of input")
    return tree

# Create traverse function, will take a tree and a configuration of truth and compute result
def traverse_verify(tree, variables):
    # Check if current traversal is a variable
    if type(tree).__name__ == "Variable":
        # Call into the truth in the variables dictionary and return the True/False
        return variables[str(tree.name)]
    # Determine if value is a Binary Operation
    elif type(tree).__name__ == "BinaryOp":
        # Find the True/False value of the left side of binary op
        left = traverse_verify(tree.left, variables)
        # Find the True/False value of the right side of the binary op
        right = traverse_verify(tree.right, variables)
        # Call the binary op function on both True/False values and return
        return tree.op(left, right)
    # Determine if current op is a ~
    elif type(tree).__name__ == "UnaryOp":
        # Negate the recursive call's True/False value
        return not traverse_verify(tree.operand, variables)

# Create traverse_pathing: Creates a tree-like list struture with unique operand ids
def traverse_pathing(tree):
    # Check if current elem is a varaible
    if type(tree).__name__ == "Variable":
        # Save the variable's name and unique id
        return [(str(tree.name), str(random.randint(0, 10**10)))]
    # Check if elem is a binary op
    elif type(tree).__name__ == "BinaryOp":
        # Find the pathing of the left of the tree
        left = traverse_pathing(tree.left)
        # Find the pathing list structure of the right children
        right = traverse_pathing(tree.right)
        # Perform a reverse lookup to extract the operator string value
        func = [k for k in BINARY_OPERATORS if BINARY_OPERATORS[k] == tree.op][0]
        # Return the unique id for function string, and children
        return [(func, str(random.randint(0, 10**10))), left, right]
    # Check if function is invert
    elif type(tree).__name__ == "UnaryOp":
        # Return unique id for ~ and internal operand
        return [('~', str(random.randint(0, 10**10))), traverse_pathing(tree.operand)]


def traverse(tree,printQueue):
    #print (printQueue)
    if type(tree).__name__ == "Variable":
        #print(tree.name)
        #print("1")
        #print(printQueue)
        return(str(tree.name))
    elif type(tree).__name__ == "builtin_function_or_method":
        #print(str(tree).split('<built-in function ')[1].split('_>')[0])
        #print("2")
        #print(printQueue)
        return(str(tree).split('<built-in function ')[1].split('_>')[0])
    elif type(tree).__name__ == "BinaryOp":
        #print("3")
        #print(printQueue)
        printQueue.append(traverse(tree.left,printQueue))
        printQueue.append(traverse(tree.op,printQueue))
        printQueue.append(traverse(tree.right,printQueue))
    elif type(tree).__name__ == "UnaryOp":
        #print('~')
        #print("4")
        #print(printQueue)
        printQueue.append(" ")
        printQueue.append("not")
        printQueue.append(traverse(tree.operand,printQueue))
    return printQueue;

#########################################################################
#                            Results                                    #
#########################################################################


def displayResult(statement, print_info=False):
    printQueue = []
    traverseThis = statement

    #print(parse(traverseThis))
    if checkAmbiguity(traverseThis) == True:
        raise SyntaxError("Ambiguity Error")
    parsedExpr = parse(traverseThis)
    pq = traverse(parsedExpr,[])

    #print(pq)
    for item in pq:
        if str(type(item)) == "<class 'list'>":
            continue
        else:
            printQueue.append(item)
    if(print_info):
        print (printQueue)
        depthCounter = 0
        while len(printQueue) > 0:
           for i in range(0,depthCounter*3):
               print(" ", end=" ")
           if len(printQueue) == 1:
               print("level: " + str(depthCounter) + " right operator/var: " + str(printQueue.pop(0)))
           else:
               print("level: " + str(depthCounter) + " right operator/var: " + str(printQueue.pop(1)))
               depthCounter = depthCounter + 1
               for i in range(0,depthCounter*3):
                   print(" ", end=" ")
               print("level: " + str(depthCounter) + " left operator/var: " + str(printQueue.pop(0)), end="      ")

# Extract the varaibles from a given expression
def get_variables(statement):
    # Create an empty set to store varaibles
    variables = set()
    # Create the REGEX to only find valid variables
    regex = re.compile(r'\s*(?:([A-Za-z01])|(\S))')
    # Iterate through each of the capture groups
    for match in regex.finditer(statement):
        # Iterate through each token
        token, error = match.groups()
        # If the token exists, add it to our variables
        if(token):
            # Add our tokens to the variables
            variables.add(token)
    # Return a sorted list of variables that were found
    return sorted(list(variables))

# Extracts information relevant for forming a truth table of a particular expression
def get_truth_table(statement):
    # Extracts the variable name set from the expression
    variables = get_variables(statement)
    # Creates the possible states for each of the variables (True/False)
    base_truths = [[True, False] for i in variables]
    # Performs a set-cartesian product on each of the permutation elements
    table = itertools.product(*base_truths)
    # Parses the expression
    parsedExpr = parse(statement)
    # Creates an empty list which will hold the truth table
    tableBuild = []
    # Iterate through each of the permutations from the product
    for perm in table:
        # Create a dict which links the varaibles to a particular True/False set
        var_dict = {variables[i]:perm[i] for i in range(len(variables))}
        # Append to the True/False permutation the result of the expression
        tableBuild.append(list(perm) + [traverse_verify(parsedExpr, var_dict)])
    # Return a list of variables (including the expression), and their respective truth table
    return { 'variables': variables + [statement], 'truth_table': tableBuild }

# A wrapper function to parse and call traverse_pathing
def get_tree(statement):
    # Call traverse_pathing on the parsed statement
    return traverse_pathing(parse(statement))

#########################################################################
#                            Testing                                  #
#########################################################################

# print(traverse_pathing(parse('~(A → B)')))
# print(get_truth_table('~(A ∨ B) ↔ (~A ∧ ~B)'))
#print(parse('A ∨ B ∧ C ∧ B ∨ C'))

#test1 = 'A ∨ B ∧ C ∧ B ∨ C'
#print(test1 + " is ambiguous?: " + str(checkAmbiguity(test1)))
#test2 = 'A ∨ B'
#print(test2 + " is ambiguous?: " + str(checkAmbiguity(test2)))
#test3 = '(A ∨ B) ∧ (C ∧ B) ∨ C'
#print(test3 + " is ambiguous?: " + str(checkAmbiguity(test3)))
# test4 = 'A ∨ '
# try:
#     parse(test4)
#     print(test4 + " is ambiguous?: " + str(checkAmbiguity(test4)))
# except SyntaxError:
#     print(SyntaxError)
#test5 = '~A'
#print(test5 + " is ambiguous?: " + str(checkAmbiguity(test5)))
#test6 = 'A'
#print(test6 + " is ambiguous?: " + str(checkAmbiguity(test6)))
#test7 = '~A ∨ B'
#print(test7 + " is ambiguous?: " + str(checkAmbiguity(test7)))#
#test8 = '~(A ∨ B)'
#print(test8 + " is ambiguous?: " + str(checkAmbiguity(test8)))
#test9 = '~(A ∨ B) ∧ (C ∧ B) ∨ C'
#print(test9 + " is ambiguous?: " + str(checkAmbiguity(test9)))
