import time


class Benchmark(object):
    def __init__(self, iterations=20):
        self.iterations = iterations

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

            print '%2.3f seconds' % mean_time
        return wrapped
