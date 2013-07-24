import shelve
import sys
import threading
import time


class Benchmark(object):
    def __init__(self, concurrency=10, iterations=10):
        self.concurrency = concurrency
        self.iterations = iterations
        self.shelf = Shelf()

    def __call__(self, f):
        def wrapped(*args, **kwargs):
            print 'Benchmarking %s...' % f.__name__,
            sys.stdout.flush()

            # build threads
            threads = [threading.Thread(target=f, args=args, kwargs=kwargs)
                       for _ in range(self.concurrency)]

            start = time.time()
            for thread in threads:
                thread.start()
            while any(thread.is_alive() for thread in threads):
                pass
            end = time.time()
            total_time = end - start
            mean_time = total_time / (self.concurrency * self.iterations)
            task_per_sec = (self.concurrency * self.iterations) / total_time

            previous = self.shelf.get(f.__name__)
            self.shelf.set(f.__name__, total_time)

            if previous is not None:
                percent_diff = 100.0 * (total_time - previous) / previous
                print ('%2.3f seconds total (%+2.3f%%), %2.3f seconds per task, %2.3f tasks per second'
                       % (total_time, percent_diff, mean_time, task_per_sec))
            else:
                print ('%2.3f seconds total, %2.3f seconds per task, %2.3f tasks per second'
                       % (total_time, mean_time, task_per_sec))
        return wrapped


class Shelf(object):
    def __init__(self):
        self.filename = '.keystoneworkout-benchmark-shelf'

    def get(self, key):
        shelf = shelve.open(self.filename)
        try:
            return shelf.get(key)
        finally:
            shelf.close()

    def set(self, key, value):
        shelf = shelve.open(self.filename)
        try:
            shelf[key] = value
        finally:
            shelf.close()

    def delete(self, key):
        shelf = shelve.open(self.filename)
        try:
            del shelf[key]
        finally:
            shelf.close()
