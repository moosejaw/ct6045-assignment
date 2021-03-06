def getTopValues(d, size):
    '''
    Returns the largest key-value pairs in a given dict. Output is specified
    by the size arg.
    '''
    top = {}
    for key in d.keys():
        if not top or len(top.keys()) < size:
            top[key] = d[key]
        else:
            larger = False
            for k in top.keys():
                if d[key] > top[k]:
                    larger = True
            if larger:
                top[key] = d[key]
                del top[min(top, key=lambda x: top[x])]
                larger = False
    return top

def processColumnName(column):
    """
    Processes a column name from the .csv file, removing leading
    whitespace, removing capitalisation and replacing whitespace with
    an underscore.

    Inputs:
        - column: string containing the column name
    Outputs:
        string containing the processed column name
    """
    column = column.lower()
    column = column.strip()
    column = column.replace(' ', '_')
    return column
