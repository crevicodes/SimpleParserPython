'''
@authors: Angelo, Raaed, Ezekiel, Rhea
Simple Parser Project for Dr. Michel Pasquier
filename: 'ACabarloc-RMunshi-EMorata-RSrivastava.rar'
------------------
implement both syntax analyzer and lexical analyzer
tested by an unknown number of text files
output which syntax error was found in which file and line, else say if it's correct
automatically read all test files in the same folder
save the output to a single output file
------------------
<assignment-statement> -> <identifier> = (<identifier> | <numerical-literal>) {<operator> (<identifier> | <numerical-literal>)}
<identifier> -> <letter> {<letter> | <digit>}
<numerical-literal> -> [+|-] <digit> {<digit>} [. <digit> {<digit>}]
<digit> -> 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
<letter> -> a | b | c | . . . | z | A | B | . . .| Z
<operator> -> + | - | * | / | %
'''

#class to classify the token types, not digit and alphabet characters since we already have string functions in python for that
class TokenType:
    NUM = '<NUMERIC-LITERAL>'
    ID = '<IDENTIFIER>'
    OP = '<OPERATOR>'
    ASSIGN = '<ASSIGNMENT-OPERATOR>'
    EOL = '<END-OF-LINE>' #when the given string/text/line has reached the end, this is the returned token type
    UNKNOWN = '<UNKNOWN>'

#token class to identify the tokens with their types and values   
class Token:
    def __init__(self, tokType, value):
        self.type = tokType
        self.value = value

#the lexical analyser which uses the Token and TokenType classes        
class LexicalAnalyzer:
    def __init__(self, string, lineCount, errorList): 
        self.string = string
        self.position = 0
        self.lineCount = lineCount #lineCount to keep track of the line within the file
        self.errorList = errorList #errorList to keep record of the errors
        
    def skipSpace(self): #ignoring spaces but still accounting for the position
        while self.position < len(self.string) and self.string[self.position].isspace():
            self.position += 1
    
    def nextChar(self, offset = 0): #return the next character, allow for offset to skip characters
        if (self.position + offset) < len(self.string):
            return self.string[self.position + offset]
        else:
            return None #easy to spot missing terms/operands or unknown characters in the parse tree
        
    def nextToken(self):
        self.skipSpace()
        
        if self.position >= len(self.string):
            self.position += 1 #for error printing if there is a missing term or operand at the end
            return Token(TokenType.EOL, '')
        
        if self.nextChar().isalpha(): #identifier token
            identifier = ''
            while self.nextChar() and self.nextChar().isalnum():
                identifier += self.nextChar()
                self.position += 1
            return Token(TokenType.ID, identifier)
        
        #numeric_literal token
        elif self.nextChar().isdigit() or ((self.nextChar() == '-' or self.nextChar() == '+') and self.nextChar(offset = 1).isdigit()): #to differentiate between an operator and the number sign
            numericliteral = ''
            if self.nextChar() == '-' or self.nextChar() == '+':
                numericliteral += self.nextChar()
                self.position += 1
            while self.nextChar() and self.nextChar().isdigit(): #keep going as long as the next character is a digit
                numericliteral += self.nextChar()
                self.position += 1
            if self.nextChar() == '.': #decimal point for float is optional
                numericliteral += self.nextChar()
                self.position += 1
                while self.nextChar() and self.nextChar().isdigit(): #rhs of decimal point
                    numericliteral += self.nextChar()
                    self.position += 1
            return Token(TokenType.NUM, float(numericliteral))
        
        elif self.nextChar() in ('+', '-', '*', '/', '%'): #operators
            operator = self.nextChar()
            self.position += 1
            return Token(TokenType.OP, operator)
        
        elif self.nextChar() == '=': #assignment operator, not explicitly mentioned by is syntactically required, similar to the decimal point
            assignment = self.nextChar()
            self.position += 1
            return Token(TokenType.ASSIGN, assignment)
        
        else: #for an invalid entry such as a special character that was not given in the specifications... ex: $ _ @ # ! ; ...etc.
            unknown = self.nextChar()
            self.position += 1
            self.errorList.append(f'Line {self.lineCount} Error : Unrecognized character {unknown} at position {self.position}')
            return Token(TokenType.UNKNOWN, None)
                       
#the syntax analyser or 'parser' where you pass the lexical analyzer or 'lexer'      
class SyntaxAnalyzer:
    
    def __init__(self, lexer):
        self.lexer = lexer
        self.currentToken = self.lexer.nextToken()
        self.lineCount = self.lexer.lineCount #inherit the lineCount and errorList from the passed lexer
        self.errorList = self.lexer.errorList
        
    def consume(self, tokType): #processing the tokens one by one based on the passed token type which would be according to the syntax
        if self.currentToken.type == tokType: 
            self.currentToken = self.lexer.nextToken() #if it's syntactically correct, go to the next token
        else:
            self.errorList.append(f'Line {self.lineCount} Error : Expected token type {tokType} at position {self.lexer.position}, got {self.currentToken.type}')
            self.currentToken = self.lexer.nextToken() #proceed anyway to spot any other errors in the same line
     
    def term(self): #defined as an identifier or a numeric literal
        token = self.currentToken #store current token since we consume then return the value for the creation of the syntax tree
        if token.type == TokenType.ID:
            self.consume(TokenType.ID)
            return token.value
        elif token.type == TokenType.NUM:
            self.consume(TokenType.NUM)
            return token.value
        elif (token.type == TokenType.OP):
            self.errorList.append(f'Line {self.lineCount} Error : Missing <IDENTIFIER> or <NUMERIC-LITERAL> at position {self.lexer.position}')
            self.consume(self.currentToken.type)
            self.term()
        else:
            self.errorList.append(f'Line {self.lineCount} Error : Expected token type <IDENTIFIER> or <NUMERIC-LITERAL> at position {self.lexer.position}, got {token.type}')
            self.consume(self.currentToken.type)
            
            
    def expr(self): #defined as a term followed by an operator and then another term
        left = self.term()
        while self.currentToken.type == TokenType.OP and self.currentToken.value in ('+', '-', '*', '/', '%'): #similar to recursion for nesting within the parse/syntax tree
            opToken = self.currentToken
            self.consume(TokenType.OP)
            right = self.term() 
            left = (opToken.value, left, right) #node for the syntax/parse tree
         
        #error for missing operator in the middle of an expression   
        if self.currentToken == TokenType.ID or self.currentToken == TokenType.NUM:
            self.errorList.append(f'Line {self.lineCount} Error : Missing <OPERATOR> at position {self.lexer.position}')
            self.consume(self.currentToken.type)
            self.expr()
        elif self.currentToken.type != TokenType.EOL and not (self.currentToken.type == TokenType.OP and self.currentToken.value in ('+', '-', '*', '/', '%')):
            self.errorList.append(f'Line {self.lineCount} Error : Expected token type <OPERATOR> at position {self.lexer.position}, got {self.currentToken.type}')
            self.consume(self.currentToken.type)
            
        
            
        return left
       
    def assignmentStatement(self): #the very top of the syntax tree, following the assignment statement rule given in the specifications
         identifierToken = self.currentToken
         self.consume(TokenType.ID)
         self.consume(TokenType.ASSIGN) #must be an identifier followed by an assignment operator
         
         parseRHS = self.expr() #the right side of the assignment operator must be an expression
         node = ('=', identifierToken.value, parseRHS) #nested to the right
         
         return node
            
    def parse(self):
        return self.assignmentStatement() #the only function we need to call in the main

#main program
def driver():
    
    #opening the output text file
    fileNotOpen = True #flag to  see if we created a new output file or if it already exists
    try:
        fout = open('parser_output.txt', 'x')
        fileNotOpen = False
    except FileExistsError:
        pass

    if(fileNotOpen): fout = open('parser_output.txt', 'w') #file exists so just write to it

    #opening the test files and writing the result to the output file
    fileCount = 1 #counter as advised in the specifications
    try:
        while True:
            fin = open(f'{fileCount}.txt','r')
            fout.write('---------------------------------------------------------------------------------------------------------\n')
            fout.write(f'Test Program "{fileCount}.txt":\n') #heading to identify which test file has the errors / is syntactically correct
            finString = fin.read()
            testLines = finString.split('\n')
            errorList = []
            lineCount = 1
            for line in testLines:
                lexer = LexicalAnalyzer(line, lineCount, errorList) #only creates an object with attributes
                parser = SyntaxAnalyzer(lexer) #eventually calls functions to start tokenizing and analyzing the syntax
                print(parser.parse()) #calling parse() triggers a sequence of function calls to parse based on the tokens
                #bonus feature: print the parse/syntax tree, does not account for errors :)
                errorList = parser.errorList #we have to reassign it since there is no classic pass-by-reference in python
                lineCount += 1 #next line
                
            #when the entire test file is correct, you gave us a choice on whether we do it for each sentence or each program, I opted for program
            if not errorList[1:]: #works without slicing but just in case I missed something when tokenizing, this is here as a precaution  
                fout.write('Successful test program! All statements are syntactically correct.\n') 
            else:
                for error in errorList:
                    fout.write(error)
                    fout.write('\n')
            
            fileCount += 1 #increment counter before the end of loop
            fin.close() #close every test file
            fout.write('---------------------------------------------------------------------------------------------------------\n')   
            
    except FileNotFoundError: #no more test files
        fout.close() 

driver() #execute the main program


   