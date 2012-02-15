'''
Created on Jan 25, 2012

@author: caioviel
'''

import sys

NUMBER = 0
STRING = 1
EQUAL = 2
ABRE_PARENT = 3
FECHA_PAREN = 4
VIRGULA = 5
PONTO_E_VIRGULA = 6
NAMESPACE = 7
ENUM = 8
END_OF_FILE = 9

class LexialAnalyzer:
    def __init__(self, input_str):
        self.str = input_str
        self.pos = 0
        
    def get_token(self):     
        char = ''   
        while self.pos < len(self.str):
            char = self.str[self.pos];
            if char == ' ' or char == '\n' or char == '\t':
                self.pos = self.pos+1
            else:
                break
            
        if self.pos == len(self.str):
            return END_OF_FILE, ''
        if char == '{':
            self.pos = self.pos+1
            return ABRE_PARENT, ''
        elif char == '}':
            self.pos = self.pos+1
            return FECHA_PAREN, ''
        elif char == ',':
            self.pos = self.pos+1
            return VIRGULA, ''
        elif char == ';':
            self.pos = self.pos+1
            return PONTO_E_VIRGULA, ''
        elif char == '=':
            self.pos = self.pos+1
            return EQUAL, ''
        elif char.isalpha() or char == '_':
            aux = self.__get_string__()
            if aux == 'namespace':
                return NAMESPACE, ''
            elif aux == 'enum':
                return ENUM, ''
            else:
                return STRING, aux
        elif char.isdigit():
            return self.__get_number__()
        else:
            raise Exception('Invalid character found: '  + char + ' .')
            
    def __get_string__(self):
        begin_pos = self.pos
        end_pos = self.pos +1
        self.pos = self.pos +1
        while self.pos < len(self.str):
            char = self.str[self.pos];
            if char.isdigit() or char.isalpha() or char == '_':
                end_pos = end_pos+1
                self.pos = self.pos +1
            else:
                break
        return self.str[begin_pos:end_pos]
    
    def __get_number__(self):
        begin_pos = self.pos
        end_pos = begin_pos +1
        self.pos = self.pos +1
        while self.pos < len(self.str):
            char = self.str[self.pos];
            if char.isdigit():
                end_pos = end_pos+1
                self.pos = self.pos +1
            else:
                break
        return NUMBER, int(self.str[begin_pos:end_pos])
        
class SyntheticAnalyzer:
    def __init__(self, input_str):
        self.lex = LexialAnalyzer(input_str)
        self.namespace_list = [] 
        self.enum_name = ''
        self.enum_itens = []
        
    def do_parse(self):
        lex = self.lex
        token, _ = lex.get_token()
        if token == ENUM:
            self.__parse_enum__()
        elif token == NAMESPACE:
            self.__parse_namespace__()
        else:
            raise Exception('Invalid token found in do_parse: expected ENUM or NAMESPACE.')
        
    def __parse_enum__(self):
        lex = self.lex
        token, value = lex.get_token()
        if token != STRING:
            raise Exception('Invalid token found in __parse_enum__: expected STRING.')
        
        self.enum_name = value;
        
        token, value = lex.get_token()
        if token != ABRE_PARENT:
            raise Exception('Invalid token found in __parse_enum__: expected ABRE_PARENT.')
        
        self.__parse_item_list__()
        
        token, value = lex.get_token()
        if token != PONTO_E_VIRGULA:
            raise Exception('Invalid token found in __parse_enum__: expected PONTO_E_VIRGULA.')
        
    def __parse_item_list__(self):
        lex = self.lex
        token, item = lex.get_token()
        if token != STRING:
            raise Exception('Invalid token found in __parse_item_list__: expected STRING.')
        
        while token == STRING:
            token, _ = lex.get_token()
            if token == VIRGULA:
                self.enum_itens.append((item, False, 0))
                token, item = lex.get_token()
            elif token == EQUAL:
                token, value = lex.get_token()
                if token == NUMBER:
                    self.enum_itens.append((item, True, value))
                token, item = lex.get_token()
                
                if token == VIRGULA:
                    token, item = lex.get_token()
                elif token == FECHA_PAREN:
                    return
                else:
                    raise Exception('Invalid token <' + str(token) + '> found in __parse_item_list__: expected FECHA_PAREN or VIRGULA.')
                
            elif token == FECHA_PAREN:
                self.enum_itens.append((item, False, 0))
                return
            else:
                raise Exception('Invalid token found in __parse_item_list__: expected VIRGULA or NUMBER.')
            
        if token != FECHA_PAREN:
            raise Exception('Invalid token <' + str(token) + '> found in __parse_item_list__: expected FECHA_PAREN.')
        
    def __parse_namespace__(self):
        lex = self.lex
        token, value = lex.get_token()
        if token != STRING:
            raise Exception('Invalid token found in __parse_namespace__: expected STRING.')
        
        self.namespace_list.append(value)
        
        token, value = lex.get_token()
        if token != ABRE_PARENT:
            raise Exception('Invalid token found in __parse_namespace__: expected ABRE_PARENT.')
        
        token, value = lex.get_token()
        if token == ENUM:
            self.__parse_enum__()
        elif token == NAMESPACE:
            self.__parse_namespace__()
        else:
            raise Exception('Invalid token found in __parse_namespace__: expected ENUM or NAMESPACE.')
        
        token, value = lex.get_token()
        if token != FECHA_PAREN:
            raise Exception('Invalid token found in __parse_namespace__: expected FECHA_PAREN.')
        

class CodeGenerator:
    def __init__(self, namespaces, class_name, enum_itens):
        self.namespaces = namespaces
        self.class_name = class_name
        self.enum_itens = enum_itens
        
        self.complete_name = ''
        for namespace in self.namespaces:
            self.complete_name += namespace + '::'
            
        self.complete_name += class_name
        
    def generate_header_str(self):
        c_name = self.class_name
        code = ''
        code += '#ifndef ' + c_name + '_H_\n'
        code += '#define ' + c_name + '_H_\n\n'
        
        code += '#include <string>\n'
        code += '#include <iostream>\n\n'
        
        for namespace in self.namespaces:
            code += 'namespace ' + namespace + ' {\n'

        code += '\nclass ' + c_name + '{\n'
        code += 'public:\n'
        code += '\tenum Type {\n'
        for item, has_value, value in self.enum_itens:
            code += '\t\t' + item
            if has_value:
                code += '=' + str(value)
            code += ',\n'
        code += '\t};\n\n'
        
        code += 'public:\n'
        code += '\t//Default constructor will use the first element of the enumeration for initializations\n'
        code += '\t' + c_name + '();\n'
        code += '\t' + c_name + '(' + c_name + '::Type type);\n'
        code += '\t' + c_name + '(const ' + c_name + '& obj);\n'
        code += '\t' + c_name + '(const std::string& str);\n\n'
        
        code += '\t' + c_name + '& operator=(const ' + c_name + '& obj);\n'
        code += '\t' + c_name + '& operator=('+ c_name + '::Type type);\n\n'
        
        code += '\tbool operator==(const ' + c_name + '& obj) const;\n'
        code += '\tbool operator==('+ c_name + '::Type type) const;\n\n'
        
        code += '\tbool operator!=(const ' + c_name + '& obj) const;\n'
        code += '\tbool operator!=('+ c_name + '::Type type) const;\n\n'
        
        code += '\tfriend std::ostream& operator<<(std::ostream &out,\n'
        code += '\t\t\tconst ' + c_name + '& obj);\n\n'
        
        code += '\tstd::string toString() const;\n'
        code += '\t' + c_name + '::Type getType() const;\n\n'
        
        code += 'private:\n'
        code += '\t' + c_name + '::Type type;\n'
        code += '\tchar* str;\n\n'
        
        code += '\tstatic char** initializeStrTypes();\n'
        code += '\tstatic char** strTypes;\n'
        
        code += '\tstatic '+ c_name + '::Type* initializeTypes();\n'
        code += '\tstatic ' + c_name + '::Type* types;\n\n'
        
        code += '\tstatic char* typeToString(' + c_name + '::Type);\n'
        code += '\tstatic ' + c_name + '::Type stringToType(const std::string& str);\n\n'
        
        code += '};\n\n'
            
        for namespace in self.namespaces:
            code += '} /* namespace ' + namespace + ' */\n' 
        
        
        code += '\n#endif /* ' + c_name + '_H_ */'
        return code
        
    def generate_source_str(self, include_file):
        c_name = self.class_name
        code = ''
        code += '#include "' + include_file + '"\n'
        code += '#include <libcpputil/SimpleException.h>\n'
        code += '#include <libcpputil/Functions.h>\n\n'
        
        for namespace in self.namespaces:
            code += 'namespace ' + namespace + ' {\n'
            
        code += self.__generate_constructors__()
        
        code += self.__generate_attribuicao__()
        
        code += self.__generate_boolean__()
        
        code += self.__generate_converters__()
        
        code += self.__generate_initializers__()
            
        for namespace in self.namespaces:
            code += '} /* namespace ' + namespace + ' */\n' 
            
        return code
    
    def __generate_initializers__(self):
        c_name = self.class_name
        code = '\n'
        
        code += 'char** ' + c_name + '::initializeStrTypes() {\n'
        code += '\tchar** aux = new char*[' + str(len(self.enum_itens)) + '];\n'
        count = 0
        for item, _, _ in self.enum_itens:
            code += '\taux[' + str(count) + '] = (char*) "' + item.upper() + '";\n'
            count += 1
        code += '\treturn aux;\n'
        code += '}\n\n'
        code += 'char** ' + c_name + '::strTypes = ' + c_name + '::initializeStrTypes();\n\n'
        
        
        code += c_name + '::Type* ' + c_name + '::initializeTypes() {\n'
        code += '\t' + c_name + '::Type* aux = new ' + c_name + '::Type[' + str(len(self.enum_itens)) + '];\n'
        count = 0
        for item, _, _ in self.enum_itens:
            code += '\taux[' + str(count) + '] = ' + item + ';\n'
            count += 1
        code += '\treturn aux;\n'
        code += '}\n\n'
        code += c_name + '::Type* ' + c_name + '::types = ' + c_name + '::initializeTypes();\n\n'
        
        return code
        
    
    def __generate_converters__(self):
        c_name = self.class_name
        code = '\n'
        
        code += 'char* ' + c_name + '::typeToString(' + c_name + '::Type type) {\n'
        code += '\tfor (int i = 0; i < ' + str(len(self.enum_itens)) + '; i++) {\n'
        code += '\t\tif (type == types[i]) {\n'
        code += '\t\t\treturn strTypes[i];\n'
        code += '\t\t}\n'
        code += '\t}\n'
        code += '\tthrow cpputil::SimpleException(\n'
        code += '\t\t\t"Trying to convert a invalid ' + c_name + '::Type",\n'
        code += '\t\t\t"' + self.complete_name + '",\n'
        code += '\t\t\t"typeToString(' + c_name + '::Type)");\n'
        code += '}\n\n' 
        
        
        code += c_name + '::Type ' + c_name + '::stringToType(const std::string& str) {\n'
        code += '\tstd::string aux = cpputil::Functions::toUpperCase(str);\n'
        code += '\tfor (int i = 0; i < ' + str(len(self.enum_itens)) + '; i++) {\n'
        code += '\t\tif (aux == strTypes[i]) {\n'
        code += '\t\t\treturn types[i];\n'
        code += '\t\t}\n'
        code += '\t}\n'
        code += '\tthrow cpputil::SimpleException(\n'
        code += '\t\t\t"Trying to convert a invalid string: " + str,\n'
        code += '\t\t\t"' + self.complete_name + '",\n'
        code += '\t\t\t"stringToType(const string&)");\n'
        code += '}\n' 
        
        return code
        
    
    def __generate_boolean__(self):
        c_name = self.class_name
        code = '\n'
        
        code += 'bool ' + c_name + '::operator==(const ' + c_name + '& obj) const {\n'
        code += '\treturn (this->type == obj.type);\n'
        code += '}\n\n'
        
        code += 'bool ' + c_name + '::operator==(' + c_name + '::Type type) const {\n'
        code += '\treturn (this->type == type);\n'
        code += '}\n\n'
        
        code += 'bool ' + c_name + '::operator!=(const ' + c_name + '& obj) const {\n'
        code += '\treturn (this->type != obj.type);\n'
        code += '}\n\n'
        
        code += 'bool ' + c_name + '::operator!=(' + c_name + '::Type type) const {\n'
        code += '\treturn (this->type != type);\n'
        code += '}\n\n'
        
        code += 'std::string ' + c_name + '::toString() const {\n'
        code += '\treturn str;\n'
        code += '}\n\n'
        
        code += c_name + '::Type ' + c_name + '::getType() const {\n'
        code += '\treturn type;\n'
        code += '}\n'
        
        return code
    
    def __generate_attribuicao__(self):
        c_name = self.class_name
        code = '\n'
        
        code += c_name + '& ' + c_name + '::operator=(const ' + c_name + '& obj) {\n'
        code += '\tif (this->type != obj.type) {\n'
        code += '\t\tthis->type = obj.type;\n'
        code += '\t\tthis->str = obj.str;\n'
        code += '\t}\n'
        code += '\treturn *this;\n'
        code += '}\n\n'     
        
        code += c_name + '& ' + c_name + '::operator=(' + c_name + '::Type type) {\n'
        code += '\tif (this->type != type) {\n'
        code += '\t\tthis->type = type;\n'
        code += '\t\tthis->str = typeToString(type);\n'
        code += '\t}\n'
        code += '\treturn *this;\n'
        code += '}\n\n'
        
        code += 'std::ostream& operator<<(std::ostream& out, const ' + c_name + '& obj) {'
        code += '\tout << obj.toString();\n'
        code += '\treturn out;\n'
        code += '}\n'   
        
        return code
        
    
    def __generate_constructors__(self):
        c_name = self.class_name
        code = '\n'
        
        code += c_name + '::' + c_name + '() {\n'
        code += '\tthis->type = types[0];\n'
        code += '\tthis->str = strTypes[0];\n'
        code += '}\n\n'
        
        code += c_name + '::' + c_name + '(' + c_name + '::Type type) {\n'
        code += '\tthis->type = type;\n'
        code += '\tthis->str = typeToString(type);\n';
        code += '}\n\n'
        
        code += c_name + '::' + c_name + '(const ' + c_name + '& obj) {\n'
        code += '\tthis->type = obj.type;\n'
        code += '\tthis->str = obj.str;\n';
        code += '}\n\n'
        
        code += c_name + '::' + c_name + '(const std::string& str) {\n'
        code += '\tfor (int i = 0; i <' + str(len(self.enum_itens)) + '; i++) {\n'
        code += '\t\tif (str == strTypes[i]) {\n'
        code += '\t\t\tthis->type = types[i];\n'
        code += '\t\t\tthis->str = strTypes[i];\n'
        code += '\t\t\treturn;\n'
        code += '\t\t}\n'
        code += '\t}\n'
        code += '\tthrow cpputil::SimpleException(\n'
        code += '\t\t\t"Trying to convert a invalid string: " + str,\n'
        code += '\t\t\t"' + self.complete_name + '",\n'
        code += '\t\t\t"' + c_name + '(const string&)");\n'
        code += '}\n'
        return code
    
def func_help():
    print 'Usage: enumgen.py (-f <FILE> | -e <ENUM>) [-h <HEADER> -s <SOURCE>]'
    print'\t--file, -f <FILE>\t\tSet the file with the enum code'
    print'\t--enum, -e <N>\t\tAn inline C++ enum that will be converted'
    print '\t--source, -s <SOURCE>\t\tSet the name of c++ header file to be generated'
    print '\t--header, -h <HEADER>\t\tet the name of c++ source file to be generated.'

if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print 'Error: You must inform the file to be parsed or the enum source code at least.'
        print '\tTry: enumgen.py -h for help'
        sys.exit()
    
    header_file_name = ''
    source_file_name = ''
    input_file_name = ''
    input_str = ''
    option, value = sys.argv[1], sys.argv[2]
    next_option = 3
    use_file = False;
    
    if option == '--file' or option == '-f':
        use_file = True
        input_file_name = value
    elif option == '--enum' or option == '-e':
        use_file = False
        input_str = value
    else:
        print 'Error: You must inform the file to be parsed or the enum source code at least.'
        print '\tTry: enumgen.py -h for help'
        sys.exit()
        
    while next_option+1 <= len(sys.argv):
        option, value = sys.argv[next_option], sys.argv[next_option+1]
        next_option += 2
        if option == '-s' or option == '--source':
            source_file_name = value
        elif option == '-h' or option == '--header':
            header_file_name = value
        else:
            print 'Error: Invalid option: ', option 
            print '\tTry: enumgen.py -h for help'
            sys.exit()
        
    
    if use_file:
        input_file = open(input_file_name, 'r')
        input_str = input_file.read()
    
    parser = SyntheticAnalyzer(input_str)
    parser.do_parse()
    
    code_generator = CodeGenerator(parser.namespace_list, parser.enum_name, parser.enum_itens)
    
    header_str = code_generator.generate_header_str()
    if header_file_name == '':
        header_file_name = parser.enum_name + '.h'
    
    header_file = open(header_file_name, 'w')
    header_file.write(header_str)
    header_file.close()
    print 'Header file generated: ', header_file_name
    
    source_str = code_generator.generate_source_str(header_file_name)
    if source_file_name == '':
        source_file_name = parser.enum_name + '.cpp'
    
    source_file = open(source_file_name, 'w')
    source_file.write(source_str)
    source_file.close()
    print 'Source File generated: ', source_file_name
    
    print '\n'
    