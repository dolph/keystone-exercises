import time


def benchmark(method):
    def benchmarked(*args, **kw):
        print 'Benchmarking', method.__name__, '...',
        times = []
        for _ in range(BENCHMARK_ITERATIONS):
            start = time.time()
            result = method(*args, **kw)
            end = time.time()
            times.append(end - start)
        mean_time = sum(times) / BENCHMARK_ITERATIONS
        print '%2.3f seconds' % mean_time
        return result
    return benchmarked


BENCHMARK_ITERATIONS = 100
