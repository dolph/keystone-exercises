import os
import shelve
import tempfile
import time


class Benchmark(object):
    def __init__(self, iterations=20):
        self.iterations = iterations
        self.shelf = Shelf()

    def __call__(self, f):
        def wrapped(*args, **kw):
            print 'Benchmarking', f.__name__, '...',

            times = []
            for _ in range(self.iterations):
                start = time.time()
                f(*args, **kw)
                end = time.time()
                times.append(end - start)
            mean_time = sum(times) / self.iterations

            previous = self.shelf.get(f.__name__)
            self.shelf.set(f.__name__, mean_time)

            if previous is not None:
                percent_diff = 100.0 * (mean_time - previous) / previous
                print '%2.3f seconds (%+2.3f%%)' % (mean_time, percent_diff)
            else:
                print '%2.3f seconds' % mean_time
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
