# Wall-Clock Decomposition: Distinguishing Compute vs Wait Time

When a process is suspected of being "stuck" or "slower than expected", use wall-clock decomposition to determine whether the bottleneck is compute, I/O, lock contention, or IPC overhead.

## Theory

A process showing 0% parent CPU with children at 100% is NOT necessarily stuck — it's the parent waiting for children. The key metric is `utime` (user CPU time) vs wall-clock time for each child process.

```python
# Per-worker formula
cpu_utilization = (utime + stime) / wall_clock_time

# utime/stime from /proc/<pid>/stat (jiffies)
# wall_clock_time from ps -o etime (seconds)
# CLK_TCK = 100 on most Linux systems
```

## Quick Check

```bash
# 1. Check process tree structure
pstree -p <parent_pid> | head -5
# ✅ parent sleeping + children R (running) at 100% CPU = working
# ❌ parent sleeping + children S (sleeping) at 0% CPU = stuck

# 2. Decompose one worker
pid=$(ps --ppid <parent_pid> -o pid --no-headers | head -1)
cat /proc/$pid/stat | awk '{print "utime=" $14 " stime=" $15}'
ps -p $pid -o etime --no-headers
# utime jiffies / CLK_TCK = CPU seconds
# wall time from etime
# If CPU seconds ≈ wall seconds → it's 100% compute (not stuck)
# If CPU seconds << wall seconds → it's waiting on something

# 3. Check which syscall the process is spending time in
cat /proc/$pid/wchan 2>/dev/null    # kernel function blocked on
cat /proc/$pid/stack 2>/dev/null    # kernel stack trace
```

## Instrumented Decomposition (Recommended)

For reliable measurements, add `time.perf_counter` instrumentation around the hot path:

```python
import time

def run_pipeline():
    totals = {}
    
    t0 = time.perf_counter()
    result = compute_heavy_function()
    totals['compute'] = time.perf_counter() - t0
    
    t0 = time.perf_counter()
    write_to_sqlite(result)
    totals['db_write'] = time.perf_counter() - t0
    
    t0 = time.perf_counter()
    serialize_result(result)
    totals['serialize'] = time.perf_counter() - t0
    
    total = sum(totals.values())
    for k, v in totals.items():
        print(f"  {k}: {v:.1f}s ({v/total*100:.1f}%)")
    print(f"  total: {total:.1f}s")
```

## Common Pitfalls

- **Reading parent PID CPU instead of child PID CPU**: The parent/scheduler process may show 0% CPU even when children are at 100%. Always check children when using multiprocessing/ProcessPoolExecutor.
- **PYTHONUNBUFFERED not set**: When output is piped (`| tee log`), Python defaults to block buffering. Set `PYTHONUNBUFFERED=1` before the command to get real-time progress.
- **cProfile overhead**: Running cProfile adds significant overhead (can slow execution 5-20x). Use wall-clock decomposition for realistic timing; use cProfile only for breakdown within the hot path.
