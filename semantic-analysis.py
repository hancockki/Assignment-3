import sys


tokens = []
lexemes = []
token_pointer = 0

symbol_table = {}
expression_list = []

"""
Read in the file of tokens and lexemes.
Each line of the file contains a token followed
by a tab, followed by a lexeme.
This file is read in line by line, and the token 
is added to our globally defined list, tokens.

@params:
    input --> file name given on command line
"""


def get_input(input):
    with open(input, 'r') as tokens_stream:
        for line in tokens_stream:
            next_line = line.split()
            next_token = next_line[0]
            next_lexeme = next_line[1]
            tokens.append(next_token)
            lexemes.append(next_lexeme)


"""
Main method, driver for our recursion.
We start by getting the stream of user tokens
and then call our start symbol.
From Program(), all of the subsequent NT methods 
are called until all tokens are processed or an error
is raised.

@params:
    input --> file name given on command line
"""


def main(input):
    get_input(input)
    print("Tokens:\n", tokens, "\nLexemes:\n ", lexemes)
    Program()  # start symbol
    if token_pointer < len(tokens):  # could not consume the whole input
        print("Incomplete expression. Error at index " +
              str(token_pointer) + " " + str(tokens[token_pointer]))
    else:  # consumed all tokens with no errors
        print("Success")
"""
Start symbol.
Since the first 5 tokens are the same for any program, we manually check these.
Then, after the opening bracket for the main method,
we call Declarations and Statements, the two NT symbols on the RHS of Program

When we reach the end of this method we are done parsing and return to main(),
where we check if the parsing was valid.
"""
def Program():
    global token_pointer
    if token_pointer < len(tokens) and tokens[token_pointer] == "type":
        token_pointer += 1
    else:
        return
    if token_pointer < len(tokens) and tokens[token_pointer] == "main":
        token_pointer+= 1
    else:
        return
    if token_pointer < len(tokens) and tokens[token_pointer] == "(":
        token_pointer+=1
    else:
        return
    if token_pointer < len(tokens) and tokens[token_pointer] == ")":
        token_pointer+=1
    else:
        return
    if token_pointer < len(tokens) and tokens[token_pointer] == "{":
        token_pointer += 1
        #call NT symbols on RHS of Program grammar production rule
        Declarations()
        Statements()
    else:
        return
    if token_pointer < len(tokens) and tokens[token_pointer] == "}":
        token_pointer += 1

"""
Grammar rule is that Declarations maps to
one or more iterations of Declaration. 
We use a while loop to capture this.
"""
def Declarations():
    while token_pointer < len(tokens) and tokens[token_pointer] == "type":
        Declaration()

"""
Grammar rule for declaration is type followed
by id, followed by 0 or more iterations of ,id.
"""

def Declaration():
    global token_pointer
    var_type = Type() #type must come first
    if token_pointer < len(tokens) and tokens[token_pointer] == "id":
        #add new variable to symbol table
        symbol_table[lexemes[token_pointer]] = [var_type, None]
        token_pointer += 1
    # we could have id followed by any number of ,id (comma separated values)
    while token_pointer < len(tokens) and tokens[token_pointer] == ",":
        token_pointer += 1
        if token_pointer < len(tokens) and tokens[token_pointer] == "id":
            symbol_table[lexemes[token_pointer]] = [var_type, None]
            token_pointer += 1
    #declaration must end with a semicolon
    if token_pointer < len(tokens) and tokens[token_pointer] == ";":
        token_pointer += 1

"""
Simply check if the token is type.
"""
def Type():
    global token_pointer
    if token_pointer < len(tokens) and tokens[token_pointer] == "type":
        var_type = lexemes[token_pointer]
        token_pointer += 1
    return var_type

"""
Statements is defined as 0 or more iterations
of Statement. Keep running Statement until it returns
false.
"""
def Statements():
    #not sure if this is correct!!!
    while Statement(True):
        Statement(True)

""" 
The grammar rule for Statement is either
Assignment OR PrintStmt OR IfStatement OR WhileStatement
OR ReturnStatement. We try each of these until the 
syntax for one matches. If this is the case, we return True.
Otherwise, we return False.

We use elif here, meaning we try each one until it works.

@params:
    evaluate --> true if we want to change the symbol after evaluation,
                false if not. This is determined by the truth value of the 
                Expresssion() in an if statement / while loop
"""
def Statement(evaluate):
    if token_pointer < len(tokens) and tokens[token_pointer] == "id":
        print("calling assignment with value: ", evaluate)
        Assignment(evaluate)
        return True
    elif token_pointer < len(tokens) and tokens[token_pointer] == "print":
        PrintStmt()
        return True
    elif token_pointer < len(tokens) and tokens[token_pointer] == "if":
        IfStatement()
        return True
    elif token_pointer < len(tokens) and tokens[token_pointer] == "while":
        WhileStatement()
        return True
    elif token_pointer < len(tokens) and tokens[token_pointer] == "return":
        ReturnStatement()
        return True
    else:
        return False
        error("incorrect syntax for statement")

"""
PrintStmt grammar production rule is defined as print followed
by expression followed by semicolon. 
"""
def PrintStmt():
    global token_pointer
    if token_pointer < len(tokens) and tokens[token_pointer] == "print":
        token_pointer += 1
    else:
        error("Missing print. Error at index " + str(token_pointer))
    result = Expression()
    print(result)
    if token_pointer < len(tokens) and tokens[token_pointer] == ";":
        token_pointer += 1
    else:
        error("Missing semicolon. Error at index " + str(token_pointer))

"""
Grammar production rule for IfStatement is if followed by (Expression) 
followed by Statement, followed by 0 or 1 iterations of else Statement
"""
def IfStatement():
    global token_pointer
    if tokens[token_pointer] == "if" and token_pointer < len(tokens):
        token_pointer += 1
    if tokens[token_pointer] == "(" and token_pointer < len(tokens):
        token_pointer += 1
        evaluate = Expression()
    if tokens[token_pointer] == ")" and token_pointer < len(tokens):
        token_pointer += 1
    Statement(evaluate)
    #check if we have an else block, not required
    if token_pointer < len(tokens) and tokens[token_pointer] == "else":
        token_pointer += 1
        Statement(not evaluate) #we do want to evaluate if evaluate == true

"""
WhileStatement grammar production rule is defined as while followed by
(Expression) followed by Statement.
"""
def WhileStatement():
    global token_pointer
    if tokens[token_pointer] == "while" and token_pointer < len(tokens):
        token_pointer += 1
    else:
        error("Missing 'while'. Error at index " + str(token_pointer))
    if tokens[token_pointer] == "(" and token_pointer < len(tokens):
        token_pointer += 1
        Expression()
    else:
        error("Missing ( after 'while'. Error at index " + str(token_pointer))
    if tokens[token_pointer] == ")" and token_pointer < len(tokens):
        token_pointer += 1
    else:
        error("Missing ) after 'while'. Error at index " + str(token_pointer))
    Statement()

"""
ReturnStatement grammar production rule is defined as return followed by
Expression followed by semicolon. 
"""
def ReturnStatement():
    global token_pointer
    if tokens[token_pointer] == "return" and token_pointer < len(tokens):
        token_pointer += 1
    Expression()
    if tokens[token_pointer] == ";" and token_pointer < len(tokens):
        token_pointer += 1
    else:
        error("Missing ; in return. Error at index " + str(token_pointer))

"""
Grammar production rule for assignment is defined as 
if followed by assignOp followed by Expression followed
by semicolon.
"""
def Assignment(evaluate):
    global token_pointer
    if token_pointer < len(tokens) and tokens[token_pointer] == "id":
        var_id = lexemes[token_pointer]
        token_pointer += 1
    if token_pointer < len(tokens) and tokens[token_pointer] == "assignOp":
        token_pointer += 1
    result = Expression()
    #if evaluate is True, update symbol Table
    if evaluate:
        print(var_id, symbol_table[var_id][0], result)
        if symbol_table[var_id][0] == "int" and type(result) != int:
            print("Widening scope, tried to convert int to float. Type error at index ", token_pointer)
            exit(0)
        symbol_table[var_id][1] = result
    print("Current val of id: ", var_id, symbol_table[var_id])
    if token_pointer < len(tokens) and tokens[token_pointer] == ";":
        token_pointer += 1
    

"""
Grammar production rule for Expression() is Conjunction followed by
zero or more iterations of || Conjunction
"""
def Expression():
    global token_pointer
    global expression_list
    result = Conjunction()
    while token_pointer < len(tokens) and tokens[token_pointer] == "||":
        token_pointer += 1
        result = result or Conjunction()
    print("Expression is:", result)
    return result

"""
Grammar production rule for Conjunction is Equality followed
by zero or more iterations of && Equality
"""
def Conjunction():
    global token_pointer
    global expression_list
    result = Equality()
    while token_pointer < len(tokens) and tokens[token_pointer] == "&&":
        token_pointer += 1
        #continue computing logical AND until the token pointer doesnt match &&
        result = result and Equality()
    return result

"""
Grammar production rule for Equality is Relation followed by
zero or 1 occurences of equOp Relation 
"""
def Equality():
    global token_pointer
    global expression_list
    result_LHS = Relation()
    if token_pointer < len(tokens) and tokens[token_pointer] == "equOp":
        expression_list.append(lexemes[token_pointer])
        token_pointer+=1
        result_RHS = Relation()
        if lexemes[token_pointer] == "==":
            return result_LHS == result_RHS
        else:
            return result_LHS != result_RHS
    else:
        return result_LHS

"""
Grammar Production rule for Relation is Addition followed by
zero or 1 occurence of relOp Addition
"""
def Relation():
    global token_pointer
    global expression_list
    result_LHS = Addition()
    if token_pointer < len(tokens) and tokens[token_pointer] == "relOp":
        print("got a relop:", lexemes[token_pointer])
        relOp_token_pointer = token_pointer
        token_pointer += 1
        result_RHS = Addition()
        print("Token pointer is at: ", token_pointer)
        if lexemes[relOp_token_pointer] == "<":
            print(result_LHS, "<", result_RHS)
            return result_LHS < result_RHS
        elif lexemes[relOp_token_pointer] == "<=":
            return result_LHS <= result_RHS
        elif lexemes[relOp_token_pointer] == ">":
            return result_LHS > result_RHS
        elif lexemes[relOp_token_pointer] == ">=":
            return result_LHS >= result_RHS
    else:
        return result_LHS

"""
Grammar Production rule for Addition is Term followed by zero or 
more iterations of addOp Term
"""
def Addition():
    global token_pointer
    global expression_list
    result = Term()
    while token_pointer < len(tokens) and tokens[token_pointer] == "addOp":
        sign = 1 if lexemes[token_pointer] == '+' else -1
        token_pointer+=1
        result2 = Term()
        valid = checkTypes(result, result2)
        if not valid:
            print("Types do not match in addOp operation. Error at token pointer ", token_pointer)
            exit(0)
        result += sign * result2
        print("Computed addition. Result is:", result)
    return result

"""
Check for widening scope
"""
def checkTypes(param1, param2):
    print("value: ", param1, " type: ", type(param1), " value: ", param2, " type: ", type(param2))
    if type(param1) != type(param2):
        if type(param1) == float or type(param2) == float:
            return True
        else:
            return False
    else:
        return True

"""
Grammar Production rule for Term is Factor followed by zero or more
iterations of multOp Factor 
"""
def Term():
    global token_pointer
    global expression_list
    result = Factor()
    print("LHS of multOp:", result)
    while token_pointer < len(tokens) and tokens[token_pointer] == "multOp":
        exponent = 1 if lexemes[token_pointer] == "*" else -1
        token_pointer += 1
        result2 = Factor()
        print("RHS of multOp:", result2)
        valid = checkTypes(result, result2)
        if not valid:
            print("Types mismatched. Error at token pointer ", token_pointer)
            exit(0)
        result *= result2 ** exponent
        print("Computed multOp. Result is: ", result)
    return result

""" 
Grammar Production rule for Factor is id OR intLiteral OR boolLiteral OR
floatLiteral OR (Expression)
"""
def Factor():
    global token_pointer
    if token_pointer < len(tokens):
        if  tokens[token_pointer] == "id":
            token_pointer += 1
            #grab value from symbol table
            return symbol_table[lexemes[token_pointer-1]][1]
        elif tokens[token_pointer] == "intLiteral":
            token_pointer += 1
            try:
                value = int(lexemes[token_pointer-1])
                print("int is: ", value)
                return value
            except:
                print("Type error, not an int. Eror at token pointer: ", token_pointer-1)
                exit(0)
        elif tokens[token_pointer] == "boolLiteral":
            token_pointer += 1
            if lexemes[token_pointer-1] == "true":
                return True
            elif lexemes[token_pointer-1] == "false":
                return False
            else:
                print("Type error, not a bool.Eror at token pointer: ", token_pointer-1)
                exit(0)
        elif tokens[token_pointer] == "floatLiteral":
            token_pointer += 1
            try:
                value = float(lexemes[token_pointer-1])
                return value
            except:
                print("Type error, not a float. Eror at token pointer: ", token_pointer-1)
                exit(0)
        #check if we have opening parenthenses for (Expression)
        elif token_pointer < len(tokens) and tokens[token_pointer] == "(":
            print("Found openeing parenthenses!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            token_pointer += 1
            result = Expression()
            token_pointer += 1 #for closing parenthenses!!
            return result
    else:
        print("error")
        exit(0)
        

"Print error message and exit program"
def error(msg):
    print("Syntax error.\n" + msg)
    exit()

if __name__ == "__main__":
    main(sys.argv[1])
