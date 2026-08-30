def add(a, b): return a + b
def subtract(a, b): return a - b
def multiply(a, b): return a * b
def divide(a, b): return a / b if b != 0 else "Error: Division by Zero"

def run_calculator():
    print("--- Simple Python Calculator ---")
    while True:
        try:
            op = input("Operation (+,-,*,/) or 'q' to quit: ")
            if op.lower() == 'q': break
            
            n1 = float(input("Enter first number: "))
            n2 = float(input("Enter second number: "))
            
            if op == '+': print("Result:", add(n1, n2))
            elif op == '-': print("Result:", subtract(n1, n2))
            elif op == '*': print("Result:", multiply(n1, n2))
            elif op == '/': print("Result:", divide(n1, n2))
            else: print("Invalid operator.")
        except ValueError:
            print("Invalid number input.")

if __name__ == "__main__": run_calculator()
-------------------------------------------------------------------------------
this is for testing purpose 
i am updating this because Vicky got HIV positive so he is very very very happy for posiive is is very positive persion 
