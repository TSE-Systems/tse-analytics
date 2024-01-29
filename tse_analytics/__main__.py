from multiprocessing import Process, freeze_support

from tse_analytics.app import main

if __name__ == "__main__":
    # See https://docs.python.org/3/library/multiprocessing.html#multiprocessing.freeze_support
    freeze_support()
    Process(target=main).start()
