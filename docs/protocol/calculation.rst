Design calculations
===================

.. jupyter-execute::
    :hide-code:

    %config InlineBackend.figure_format = 'svg'
    import numpy as np
    from matplotlib import pyplot
    from IPython.display import Latex
    from prettytable import PrettyTable



Page write performance
----------------------

Below is the calculation of the write duration given applications of certain size and set baudrates
at which the target communicates.

With these numbers the targets for this type of flashing are max. 64kB applications at 19200
baudrate as these would finish in the one minute range.

The interbyte space, page write duration and request timings start to become the bottleneck at the
large application sizes, this can be seen in the fact that doubling the baudrate from 57600 at 128kB
size only has a 10% reduction in total time.

.. jupyter-execute::
    :hide-code:

    sizes = [8 * 1024, 16 * 1024, 32 * 1024, 64 * 1024, 128 * 1024, 256 * 1024]
    speeds = [9600, 19200, 57600, 115200]

    interbyte_space = 0.0005 # 500 usec
    pagewrite_time = 0.010   # 10ms
    poststatus_time = 0.010  # 10ms

    table = PrettyTable()
    table.field_names = ["Baudrate/Size"] + [f'{x/1024} kB' for x in sizes]
    for speed in speeds:
        page_time = (5 + 4 + 128) * 10 / speed + (5 + 4 + 128) * interbyte_space + pagewrite_time + \
                    (6 * 10) / speed + 6 * interbyte_space + poststatus_time
        
        flashing_times = []
        for size in sizes:
            flash_time = size / 128 * page_time
            flashing_times.append(flash_time)
        table.add_row([f"{speed} bps"] + [f'{x:.03f} s' for x in flashing_times])

    print(table)

Overhead calculation
--------------------

The total protocol overhead given the above settings is expressed as the time spent
transferring useful data subtracted from the total time needed with checksums, spaces, etc.

.. jupyter-execute::
    :hide-code:

    baudrate = 19200
    page_time = (5 + 4 + 128) * 10 / 19200 + (5 + 4 + 128) * interbyte_space + pagewrite_time + \
                (6 * 10) / 19200 + 6 * interbyte_space + poststatus_time
    useful_time = 128 * 8 / 19200

    print(f"Overhead: {100 - (useful_time / page_time) * 100:.03f} %")
