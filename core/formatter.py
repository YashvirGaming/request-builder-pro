import autopep8

def format_code(code):

    try:
        return autopep8.fix_code(code)
    except:
        return code