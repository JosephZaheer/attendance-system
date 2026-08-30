def box_print(lines, title="", strip=True):
    import math
    
    lines = list(lines)
    longest = 0
    
    for line in lines:
        if strip:
            line = line.strip()
            
        if len(line) > longest:
            longest = len(line)
            
    if len(title) >= longest:
        width = len(title)
        
    else:
        width = longest
            
    bars = width + 8
    
    print("|", "—"*bars, "|", sep="")
    
    if title != "":
        
        if strip:
            title = title.strip()
            
        x = (width - len(title))/2
        lspace = math.ceil(x)
        rspace = math.floor(x)
        
        print("|    ", end="")
        print(" "*lspace + title + " "*rspace, sep="", end="")
        print("    |")
        print("|", "—"*bars, "|", sep="")
        
    for line in lines:
        
        if strip:
            line = line.strip()
            
        xl = (width - longest)/2
        lspace = math.ceil(xl)
        
        xr = width - len(line) - xl
        rspace = math.floor(xr)
        
        print("|    ", end="")
        print(" "*lspace + line + " "*rspace, sep="", end="")
        print("    |")
        
    print("|", "—"*bars, "|", sep="")

def box_print2D(lines, title="", s=4, strip=True):
    import math
    import numpy as np

    lines = np.array(lines)
    longest = [0]*lines.shape[1]
    
    for i in range(lines.shape[1]):
        for j in range(lines.shape[0]):
            line = lines[j, i]
            
            if strip:
                line = line.strip()
                
            if len(line) > longest[i]:
                longest[i] = len(line)
                
    width = longest
    bars = sum(width) + lines.shape[1]*2*s + lines.shape[1] - 1

    padding = lpad = rpad = 0
    title_longer = len(title) > bars

    if title_longer:
        padding = (len(title) - bars)/2
        lpad = math.ceil(padding)
        rpad = math.floor(padding)

        bars = len(title)

    s = " "*s
    
    if title != "":
        print("|", "—"*bars, "|", sep="")
        
        if strip:
            title = title.strip()

        x = (sum(width) + lines.shape[1] - 1 - len(title) + len(s)*2*lines.shape[1])/2

        if title_longer:
            x = 0

        lspace = math.ceil(x)
        rspace = math.floor(x)
        
        print("|", " "*lspace + title + " "*rspace, "|", sep="")

    print("|", "—"*bars, "|", sep="")
    
    for i in range(lines.shape[0]):
        for j in range(lines.shape[1]):
            line = lines[i, j]
            
            if strip:
                line = line.strip()
            
            xl = (width[j] - longest[j])/2
            lspace = math.ceil(xl)
        
            xr = width[j] - len(line) - xl
            rspace = math.floor(xr)
            
            print("|", s, sep="", end="")

            if title_longer and j == 1:
                print(" "*lpad, end="")

            print(" "*lspace + line + " "*rspace, sep="", end="")

            if title_longer and j == 1:
                print(" "*rpad, end="")
            
            print(s, end="")
            if j + 1 == lines.shape[1]:
                print("|")
                
        for idx, k in enumerate(width):
            
            if 0 < idx < len(width):
                if i + 1 != lines.shape[0]:
                    print("+", end="")
                    
                else:
                    print("—", end="")
                
            else:
                print("|", end="")
                
            if idx == 1:
                print("—"*(k + 2*len(s) + lpad + rpad), sep="", end="")

            else:
                print("—"*(k + 2*len(s)), sep="", end="")

        print("|")
