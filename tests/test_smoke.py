# import fitz
# print(fitz.__doc__)
# print(dir(fitz)[:10])

import logging

root = logging.getLogger()
print(root.handlers)  # This will show a list of handlers. If not empty, logging is set up.
