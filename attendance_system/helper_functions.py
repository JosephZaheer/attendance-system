import time
import sys

###############################################################################

animations = {
    "dots": ("...", 0.5),
    "bar":  ("============", 0.3),
    "fill": ("████████████", 0.3),
    "empty": ("       ", 0.2)
}

def load_animation(indicator="dots", newline=True):
    print()
    s, time_per_char = animations[indicator]

    for char in s:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(time_per_char)
    print(end="\n" if newline else "")

################################################################################

