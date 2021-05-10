"""
Semantic analyzer for CLite program.
This script builds on assignment 2, our syntactic
analyzer. Here, we read in a file of tokens and lexemes,
and check that the program is both syntactically correct
and semantically correct. Since this lab focuses on semantic
analysis, we will briefly outline the rules of this. For rules
on syntactic analysis refer to assignment 2.
A program is semantically correct if:
    1) all variables are declared before assigned values
    2) no two variables have the same name
    3) a variable declared as one type cannot be reassigned another type
    3) The only narrowing conversion allowed is converting float to int
    4) truth value in all if statement / while loops / for loops
    is valid

The semantic analyzer will update the value of the statement inside
an if stmt / for loop / while loop if the truth value is True. Otherwise,
the lexemes/tokens are read in but the statement is not evaluated (ie we
do not update the symbol table)

Since we are just running this script with programs having a single main method,
we only have one scope for our symbol table (ie we have a single global symbol table).
The symbol table is updated when we call Statement and the truth value is True.

The semantic analyzer will ONLY output print statements defined in the string
of tokens and lexemes and any error messages that arise. Error messages include
semantic errors like type errors as well as syntactic errors like missing braces.
When an error is raised, the error message is printed and the program terminates.

Principles of Programming Languages
Bowdoin College
Kim Hancock and Jigyasa Subedi

"""


import sys

tokens = []
lexemes = []
token_pointer = 0

#key is var id; value is a 2-element list containing the type and value
symbol_table = {}

"""
Read in the file of tokens and lexemes.
Each line of the file contains a token followed
by a tab, followed by a lexeme.
This file is read in line by line. The token 
is added to our globally defined list, tokens.
The lexeme is added to our globally defined list,
lexemes.

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
are called until all tokens and lexemes are processed or
an error is raised (either syntactic or semantic).

@params:
    input --> file name given on command line
"""
def main(input):
    get_input(input)
    Program() # start symbol
    if token_pointer < len(tokens):  #could not consume the whole input
        print("Incomplete program. Error at index " +
              str(token_pointer) + " " + str(tokens[token_pointer]))

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
Add a new id to the symbol table as we declare variables.
"""

def Declaration():
    global token_pointer
    var_type = Type() #type must come first
    if token_pointer < len(tokens) and tokens[token_pointer] == "id":
        if token_pointer < len(tokens) and tokens[token_pointer] == "id":
            if lexemes[token_pointer] in symbol_table:
                print("Trying to declare the same variable twice. Error at index " + str(token_pointer))
                exit(0)
        #add new variable to symbol table
        symbol_table[lexemes[token_pointer]] = [var_type, None]
        token_pointer += 1
    else:
         error("Missing 'id'. Error at index " + str(token_pointer))
    # we could have id followed by any number of ,id (comma separated values)
    while token_pointer < len(tokens) and tokens[token_pointer] == ",":
        token_pointer += 1
        #add new var to symbol table
        if token_pointer < len(tokens) and tokens[token_pointer] == "id":
            print("current var:", lexemes[token_pointer])
            if lexemes[token_pointer] in symbol_table:
                print("Trying to declare the same variable twice. Error at index " + str(token_pointer))
                exit(0)
            symbol_table[lexemes[token_pointer]] = [var_type, None]
            token_pointer += 1
    #declaration must end with a semicolon
    if token_pointer < len(tokens) and tokens[token_pointer] == ";":
        token_pointer += 1
    else:
         error("Missing ';'. Error at index " + str(token_pointer))

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
                Expresssion() in an if statement / for loop / while loop
"""
def Statement(evaluate):
    if token_pointer < len(tokens) and tokens[token_pointer] == "id":
        Assignment(evaluate)
        return True
    elif token_pointer < len(tokens) and tokens[token_pointer] == "print":
        PrintStmt(evaluate)
        return True
    elif token_pointer < len(tokens) and tokens[token_pointer] == "if":
        IfStatement(evaluate)
        return True
    elif token_pointer < len(tokens) and tokens[token_pointer] == "while":
        WhileStatement()
        return True
    elif token_pointer < len(tokens) and tokens[token_pointer] == "return":
        ReturnStatement(evaluate)
        return True
    else:
        return False
        error("incorrect syntax for statement")

"""
PrintStmt grammar production rule is defined as print followed
by expression followed by semicolon. 
If we want to evaluate the statement, we print the value of the Stmt.
We always want to print if the print statement is not in a loop/if statement.
If it is in a loop/if statement and evaluate is true, then we print it.

@params:
    evaluate --> true if we want to print, false if not
"""
def PrintStmt(evaluate):
    global token_pointer
    if token_pointer < len(tokens) and tokens[token_pointer] == "print":
        token_pointer += 1
    else:
        error("Missing print. Error at index " + str(token_pointer))
    result = Expression()
    if not result:
        print("Variable not declared. Error at index " + str(token_pointer))
        exit(0)
    if token_pointer < len(tokens) and tokens[token_pointer] == ";":
        token_pointer += 1
    else:
        error("Missing semicolon. Error at index " + str(token_pointer))
    if evaluate:
        print(result)

"""
Grammar production rule for IfStatement is if followed by (Expression) 
followed by Statement, followed by 0 or 1 iterations of else Statement.
Checks if the truth statement in the Expression of the if statement
is true, and if so, we evaluate the body of the if statement.

@params: 
    evaluate --> used for if statements nested in while. If false,
    then we do not want to evaluate the if statement even if it is true
"""
def IfStatement(evaluate):
    global token_pointer
    evaluate_if = evaluate #initialize to the value passed in
    while tokens[token_pointer] == "if" and token_pointer < len(tokens):
        token_pointer += 1
        if tokens[token_pointer] == '(' and token_pointer < len(tokens):
            token_pointer += 1
            if evaluate_if: #if the while loop was true, see if we want to execute if
                evaluate_if = Expression() #get truth value for if statement
            else:
                Expression()
        else:
            error("Missing '('. Error at index " + str(token_pointer))
        if tokens[token_pointer] == ')' and token_pointer < len(tokens):
            token_pointer += 1
        else:
            error("Missing ')'. Error at index " + str(token_pointer))
    Statement(evaluate_if)
    #check if we have an else block, not required
    if token_pointer < len(tokens) and tokens[token_pointer] == "else":
        token_pointer += 1
        if evaluate: #if evaluate was false, we do not want to execute the else block
            Statement(not evaluate_if) #this is the case that evaluate_if is false, so instead we evaluate the else
        else: #we do not want to evaluate if OR else
            Statement(False)

"""
WhileStatement grammar production rule is defined as while followed by
(Expression) followed by Statement.
Continuously execute the Statement in the body of the while loop until
the truth value of the while loop is false. While it is true, update
the symbol table based on the body of the while loop. If it is false,
break from the loop.
"""
def WhileStatement():
    global token_pointer
    if tokens[token_pointer] == "while" and token_pointer < len(tokens):
        token_pointer += 1
    else:
        error("Missing 'while'. Error at index " + str(token_pointer))
    if tokens[token_pointer] == "(" and token_pointer < len(tokens):
        token_pointer += 1
        #keep track of where the expression starts for iterating
        track_token_pointer = token_pointer
        while True:
            evaluate = Expression()
            #print("Iteration of while: ", evaluate)
            if tokens[token_pointer] == ")" and token_pointer < len(tokens):
                token_pointer += 1
            else:
                error("Missing ')'. Error at index " + str(token_pointer))
            if evaluate:
                Statement(evaluate)
                token_pointer = track_token_pointer #decrement token pointer to beginning of while loop
            else:
                Statement(evaluate) #pass in evaluate as false to read in the tokens
                break
    else:
        error("Missing '('. Error at index " + str(token_pointer))

"""
ReturnStatement grammar production rule is defined as return followed by
Expression followed by semicolon. 
If we want to evaluate the return statement, exit the program.
"""
def ReturnStatement(evaluate):
    global token_pointer
    if tokens[token_pointer] == "return" and token_pointer < len(tokens):
        token_pointer += 1
    else:
         error("Missing 'return'. Error at index " + str(token_pointer))
    Expression()
    if tokens[token_pointer] == ";" and token_pointer < len(tokens):
        token_pointer += 1
    else:
         error("Missing ';'. Error at index " + str(token_pointer))
    if evaluate: #exit program if we want to execute this return statement
        exit(0)

"""
Grammar production rule for assignment is defined as 
if followed by assignOp followed by Expression followed
by semicolon.
Update symbol table if we are executing this line of code.
Otherwise just read in the tokens/lexemes.

@params:
    evaluate --> update symbol table if true
"""
def Assignment(evaluate):
    global token_pointer
    if token_pointer < len(tokens) and tokens[token_pointer] == "id":
        var_id = lexemes[token_pointer]
        if var_id not in symbol_table.keys():
            print("Variable not declared before Assignment. Error at token pointer", token_pointer)
            exit(0)
        token_pointer += 1
    else:
        error("Missing 'id'. Error at index " + str(token_pointer))
    if token_pointer < len(tokens) and tokens[token_pointer] == "assignOp":
        token_pointer += 1
    else:
        error("Missing 'assignOp'. Error at index " + str(token_pointer))
    result = Expression() #compute the new value of the variable
    #print("result is: ", result, " evaluate: ", evaluate)
    #if evaluate is True, update symbol Table to store result
    if evaluate:
        if symbol_table[var_id][0] != (type(result).__name__):
            #widening an int (RHS) to a float (LHS)
            if symbol_table[var_id][0] == "float" and (type(result).__name__) == "int":
                pass
            else:
                print("Widening scope, tried to convert", symbol_table[var_id][0], "to type", \
                    type(result).__name__, "\nType error at index", token_pointer)
                exit(0)
        symbol_table[var_id][1] = result
    if token_pointer < len(tokens) and tokens[token_pointer] == ";":
        token_pointer += 1
    else:
        error("Missing ';'. Error at index " + str(token_pointer))

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
        #continue computing logical OR until the token pointer doesnt match ||
        result2 = Conjunction()
        result = result or result2
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
        result2 = Equality()
        result = result and result2
    return result

"""
Grammar production rule for Equality is Relation followed by
zero or 1 occurences of equOp Relation 
"""
def Equality():
    global token_pointer
    result_LHS = Relation()
    if token_pointer < len(tokens) and tokens[token_pointer] == "equOp":
        equOp_token = tokens[token_pointer]
        token_pointer+=1
        result_RHS = Relation()
        if lexemes[equOp_token] == "==":
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
        relOp_token_pointer = token_pointer
        token_pointer += 1
        result_RHS = Addition()
        #compute the correct logical operator
        if lexemes[relOp_token_pointer] == "<":
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
more iterations of addOp Term. Compute addition/subtraction
"""
def Addition():
    global token_pointer
    result = Term()
    while token_pointer < len(tokens) and tokens[token_pointer] == "addOp":
        sign = 1 if lexemes[token_pointer] == '+' else -1
        token_pointer+=1
        result2 = Term()
        #verify the types match
        valid = checkTypes(result, result2)
        if not valid:
            print("Types do not match in addOp operation. Error at token pointer ", token_pointer)
            exit(0)
        result += sign * result2 #sign determines whether it is addition or subtraction
    return result

"""
Check for widening scope for binary operations.

@params:
    param1 --> value of LHS of binary operation
    param2 --> value of RHS of binary operation
"""
def checkTypes(param1, param2):
    if type(param1) != type(param2):
        #if one param is a float and the other is an int
        if (type(param1) == float or type(param2) == float) and (type(param1) == int or type(param2) == int):
            return True
        else:
            return False
    else:
        return True

"""
Grammar Production rule for Term is Factor followed by zero or more
iterations of multOp Factor. compute mult/division
"""
def Term():
    global token_pointer
    result = Factor()
    while token_pointer < len(tokens) and tokens[token_pointer] == "multOp":
        #set exponent to -1 if we want to do division
        exponent = 1 if lexemes[token_pointer] == "*" else -1
        token_pointer += 1
        result2 = Factor()
        valid = checkTypes(result, result2)
        if not valid:
            print("Types mismatched. Error at token pointer ", token_pointer)
            exit(0)
        result *= result2 ** exponent
    return result

""" 
Grammar Production rule for Factor is id OR intLiteral OR boolLiteral OR
floatLiteral OR (Expression).
Try to convert the lexeme to the type defined by the token, raising
type errors if they do not match.
Return the factor and then return from the above recursive calls to compute
the operations on this factor as determined by the expression.
"""
def Factor():
    global token_pointer
    if token_pointer < len(tokens):
        if  tokens[token_pointer] == "id":
            token_pointer += 1
            #grab value from symbol table
            if lexemes[token_pointer-1] not in symbol_table:
                return False
            return symbol_table[lexemes[token_pointer-1]][1]
        elif tokens[token_pointer] == "intLiteral":
            token_pointer += 1
            try:
                value = int(lexemes[token_pointer-1])
                return value
            except:
                print("Type error, not an int. Eror at token pointer: ", token_pointer-1)
                exit(0)
        elif tokens[token_pointer] == "boolLiteral":
            #can 0 be false in CLite or can anything not 0 be true?
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
            token_pointer += 1
            result = Expression()
            token_pointer += 1 #for closing parenthenses!!
            return result
    else:
        error("Nonterminal symbol not detected. Error at index " + str(token_pointer))
        

"Print error message and exit program"
def error(msg):
    print("Syntax error.\n" + msg)
    exit(0)

if __name__ == "__main__":
    main(sys.argv[1])
