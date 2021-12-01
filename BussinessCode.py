######################################## IMPORTS #######################################

from lexer import *
from parser import *
from parser import Parser
from intermediate import *

import os
import sys

######################################## FUNCTION BUILT-IN #######################################

class BuiltInFunction(BaseFunction):
  def __init__(self, name):
    super().__init__(name)

  def execute(self, args):
    res = RunTimeResult()
    exec_ctx = self.generate_new_context()

    method_name = f'execute_{self.name}'
    method = getattr(self, method_name, self.no_visit_method)

    res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
    if res.should_return(): return res

    return_value = res.register(method(exec_ctx))
    if res.should_return(): return res
    return res.success(return_value)
  
  def no_visit_method(self, node, context):
    raise Exception(f'No execute_{self.name} method defined')

  def copy(self):
    copy = BuiltInFunction(self.name)
    copy.set_context(self.context)
    copy.set_pos(self.pos_start, self.pos_end)
    return copy

  def __repr__(self):
    return f"<built-in function {self.name}>"

  def execute_print(self, exec_ctx):
    print(str(exec_ctx.symbol_table.get('value')))
    return RunTimeResult().success(Number.null)
  execute_print.arg_names = ['value']
  
  def execute_print_ret(self, exec_ctx):
    return RunTimeResult().success(String(str(exec_ctx.symbol_table.get('value'))))
  execute_print_ret.arg_names = ['value']
  
  def execute_input(self, exec_ctx):
    text = input()
    return RunTimeResult().success(String(text))
  execute_input.arg_names = []

  def execute_input_int(self, exec_ctx):
    while True:
      text = input()
      try:
        number = int(text)
        break
      except ValueError:
        print(f"'{text}' must be an integer. Try again!")
    return RunTimeResult().success(Number(number))
  execute_input_int.arg_names = []

  def execute_clear(self, exec_ctx):
    os.system('cls' if os.name == 'nt' else 'cls')
    os.system('clear')
    return RunTimeResult().success(Number.null)
  execute_clear.arg_names = []

############ I Believe It Could Be Deleted ####################
  def execute_is_number(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
    return RunTimeResult().success(Number.true if is_number else Number.false)
  execute_is_number.arg_names = ["value"]

  def execute_is_string(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), String)
    return RunTimeResult().success(Number.true if is_number else Number.false)
  execute_is_string.arg_names = ["value"]

  def execute_is_list(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), List)
    return RunTimeResult().success(Number.true if is_number else Number.false)
  execute_is_list.arg_names = ["value"]

  def execute_is_function(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
    return RunTimeResult().success(Number.true if is_number else Number.false)
  execute_is_function.arg_names = ["value"]
###################### END ####################################

##################### Business Functions ############################
#Probability and Statistics
  def execute_mean(self, exec_ctx):
    list_ = exec_ctx.symbol_table.get("list")
    n = len(list_.elements)

    elementSum = float(0.0)
    for element in list_.elements:
      elementSum += float(str(element))
    mean = elementSum/n

    return RunTimeResult().success(Number(mean))
  execute_mean.arg_names = ["list"]

  def execute_variance(self, exec_ctx):
    list_ = exec_ctx.symbol_table.get("list")
    n = len(list_.elements)
    
    elementSum = float(0.0)
    for element in list_.elements:
      elementSum += float(str(element))
    mean = elementSum/n

    deviations = []
    for element in list_.elements:
      deviations.append(((float(str(element)))-mean)**2)

    variance = (sum(deviations))/(n-1)
    return RunTimeResult().success(Number(variance))
  execute_variance.arg_names = ["list"]

  def execute_standard_deviation(self, exec_ctx):
    list_ = exec_ctx.symbol_table.get("list")
    n = len(list_.elements)
    
    elementSum = float(0.0)
    for element in list_.elements:
      elementSum += float(str(element))
    mean = elementSum/n

    deviations = []
    for element in list_.elements:
      deviations.append(((float(str(element)))-mean)**2)

    variance = (sum(deviations))/(n-1)
    standard_deviation = math.sqrt(variance)

    return RunTimeResult().success(Number(standard_deviation))
  execute_standard_deviation.arg_names = ["list"]

  #Economical Analysis
  def execute_present_value(self, exec_ctx):
    future_value = float(str(exec_ctx.symbol_table.get("value1")))
    interest_rate = float(str(exec_ctx.symbol_table.get("value2")))
    period = float(str(exec_ctx.symbol_table.get("value3")))
  
    present_value = future_value/(1+interest_rate)**period
    return RunTimeResult().success(Number(present_value))
  execute_present_value.arg_names = ["value1","value2","value3"]
  
  def execute_simple_interest(self, exec_ctx):
    principal = float(str(exec_ctx.symbol_table.get("value1")))
    time = float(str(exec_ctx.symbol_table.get("value2")))
    rate= float(str(exec_ctx.symbol_table.get("value3")))

    simpleInterest = principal*time*rate/100
    
    return RunTimeResult().success(Number(simpleInterest))
  execute_simple_interest.arg_names = ["value1","value2","value3"]

  ###################### End ##################################
  def execute_append(self, exec_ctx):
    list_ = exec_ctx.symbol_table.get("list")
    value = exec_ctx.symbol_table.get("value")

    if not isinstance(list_, List):
      return RunTimeResult().failure(RunTimeError(
        self.pos_start, self.pos_end,
        "First argument must be list",
        exec_ctx
      ))

    list_.elements.append(value)
    return RunTimeResult().success(Number.null)
  execute_append.arg_names = ["list", "value"]

  def execute_pop(self, exec_ctx):
    list_ = exec_ctx.symbol_table.get("list")
    index = exec_ctx.symbol_table.get("index")

    if not isinstance(list_, List):
      return RunTimeResult().failure(RunTimeError(
        self.pos_start, self.pos_end,
        "First argument must be list",
        exec_ctx
      ))

    if not isinstance(index, Number):
      return RunTimeResult().failure(RunTimeError(
        self.pos_start, self.pos_end,
        "Second argument must be number",
        exec_ctx
      ))

    try:
      element = list_.elements.pop(index.value)
    except:
      return RunTimeResult().failure(RunTimeError(
        self.pos_start, self.pos_end,
        'Element at this index could not be removed from list because index is out of bounds',
        exec_ctx
      ))
    return RunTimeResult().success(element)
  execute_pop.arg_names = ["list", "index"]

  def execute_extend(self, exec_ctx):
    listA = exec_ctx.symbol_table.get("listA")
    listB = exec_ctx.symbol_table.get("listB")

    if not isinstance(listA, List):
      return RunTimeResult().failure(RunTimeError(
        self.pos_start, self.pos_end,
        "First argument must be list",
        exec_ctx
      ))

    if not isinstance(listB, List):
      return RunTimeResult().failure(RunTimeError(
        self.pos_start, self.pos_end,
        "Second argument must be list",
        exec_ctx
      ))

    listA.elements.extend(listB.elements)
    return RunTimeResult().success(Number.null)
  execute_extend.arg_names = ["listA", "listB"]

  def execute_len(self, exec_ctx):
    list_ = exec_ctx.symbol_table.get("list")

    if not isinstance(list_, List):
      return RunTimeResult().failure(RunTimeError(
        self.pos_start, self.pos_end,
        "Argument must be list",
        exec_ctx
      ))

    return RunTimeResult().success(Number(len(list_.elements)))
  execute_len.arg_names = ["list"]

  def execute_run(self, exec_ctx):
    fn = exec_ctx.symbol_table.get("fn")

    if not isinstance(fn, String):
      return RunTimeResult().failure(RunTimeError(
        self.pos_start, self.pos_end,
        "Second argument must be string",
        exec_ctx
      ))

    fn = fn.value

    try:
      with open(fn, "r") as f:
        script = f.read()
    except Exception as e:
      return RunTimeResult().failure(RunTimeError(
        self.pos_start, self.pos_end,
        f"Failed to load script \"{fn}\"\n" + str(e),
        exec_ctx
      ))

    _, error = run(fn, script)
    
    if error:
      return RunTimeResult().failure(RunTimeError(
        self.pos_start, self.pos_end,
        f"Failed to finish executing script \"{fn}\"\n" +
        error.as_string(),
        exec_ctx
      ))

    return RunTimeResult().success(Number.null)
  execute_run.arg_names = ["fn"]

  def execute_exit(self, exec_ctxs):
      sys.exit()
  execute_exit.arg_names = []

BuiltInFunction.print       = BuiltInFunction("print")
BuiltInFunction.print_ret   = BuiltInFunction("print_ret")
BuiltInFunction.input       = BuiltInFunction("input")
BuiltInFunction.input_int   = BuiltInFunction("input_int")
BuiltInFunction.clear       = BuiltInFunction("clear")

####################### Business Functions  ###################
#Probability and Statistics
BuiltInFunction.mean                = BuiltInFunction("mean")
BuiltInFunction.variance            = BuiltInFunction("variance")
BuiltInFunction.standard_deviation  = BuiltInFunction("standard_deviation")

#Economical Analysis
BuiltInFunction.present_value       = BuiltInFunction("present_value")
BuiltInFunction.simple_interest     = BuiltInFunction("simple_interest")

########################## End #################################


############ I Believe It Could Be Deleted ####################
BuiltInFunction.is_number   = BuiltInFunction("is_number")
BuiltInFunction.is_string   = BuiltInFunction("is_string")
BuiltInFunction.is_list     = BuiltInFunction("is_list")
BuiltInFunction.is_function = BuiltInFunction("is_function")
###################### END ####################################

BuiltInFunction.append      = BuiltInFunction("append")
BuiltInFunction.pop         = BuiltInFunction("pop")
BuiltInFunction.extend      = BuiltInFunction("extend")
BuiltInFunction.len			    = BuiltInFunction("len")
BuiltInFunction.run			    = BuiltInFunction("run")
BuiltInFunction.exit		    = BuiltInFunction("exit")

######################################## RUN #######################################

global_symbol_table = SymbolTable()
global_symbol_table.set("NULL", Number.null)
global_symbol_table.set("FALSE", Number.false)
global_symbol_table.set("TRUE", Number.true)
global_symbol_table.set("MATH_PI", Number.math_PI)
global_symbol_table.set("PRINT", BuiltInFunction.print)
global_symbol_table.set("PRINT_RET", BuiltInFunction.print_ret)
global_symbol_table.set("INPUT", BuiltInFunction.input)
global_symbol_table.set("INPUT_INT", BuiltInFunction.input_int)
global_symbol_table.set("CLEAR", BuiltInFunction.clear)
global_symbol_table.set("CLS", BuiltInFunction.clear)

####################### Business Functions #############################
#Probability and Statistics
global_symbol_table.set("MEAN", BuiltInFunction.mean)
global_symbol_table.set("VARIANCE", BuiltInFunction.variance)
global_symbol_table.set("STANDARD_DEVIATION", BuiltInFunction.standard_deviation)

#Economical Analysis
global_symbol_table.set("PRESENT_VALUE", BuiltInFunction.present_value)
global_symbol_table.set("SIMPLE_INTEREST", BuiltInFunction.simple_interest)

########################## End ##################################

############ I Believe It Could Be Deleted ####################
global_symbol_table.set("IS_NUM", BuiltInFunction.is_number)
global_symbol_table.set("IS_STR", BuiltInFunction.is_string)
global_symbol_table.set("IS_LIST", BuiltInFunction.is_list)
global_symbol_table.set("IS_FUN", BuiltInFunction.is_function)
###################### END ####################################

global_symbol_table.set("APPEND", BuiltInFunction.append)
global_symbol_table.set("POP", BuiltInFunction.pop)
global_symbol_table.set("EXTEND", BuiltInFunction.extend)
global_symbol_table.set("LEN", BuiltInFunction.len)
global_symbol_table.set("RUN", BuiltInFunction.run)
global_symbol_table.set("EXIT", BuiltInFunction.exit)

def run(fn, text):
  # Generate Tokens
  lexer = Lexer(fn, text)
  tokens, error = lexer.make_tokens()
  if error: return None, error
  
  # Generate Abstract Syntax Tree
  parser = Parser(tokens)
  ast = parser.parse()
  if ast.error: return None, ast.error

  # Run Program
  interpreter = Interpreter()
  context = Context('<program>')
  context.symbol_table = global_symbol_table
  result = interpreter.visit(ast.node, context)

  return result.value, result.error