# ResiliStream
Fault-tolerant data ingestion engine optimized for high-latency 4G networks (The Pallavaram Field Test).
ResiliStream: Network-Aware Ingestion Engine
The problem — the “Pallavaram Constraint”

Most data ingestion pipelines assume a stable, low-loss connection. In my development environment in Pallavaram, Chennai, I saw roughly 40% packet loss and frequent ISP timeouts over 4G. Common libraries repeatedly failed, producing corrupted files and interrupting training runs.

The solution

ResiliStream is a reliability-first Python engine built to tolerate real-world network instability. Instead of treating the network as reliable, it treats it as a variable and manages TCP stream state so transfers can continue or recover without data loss.

Key engineering features

Byte-level resumption: Uses HTTP/1.1 Range headers to request only the missing segments, avoiding redundant downloads.

Watchman telemetry: A separate monitoring thread pings an external DNS (8.8.8.8) to measure latency and signal health in real time.

Self-healing logic: Custom handlers for ConnectionReset and TimeoutError that pause and retry intelligently rather than terminating the process.

Proof of work — stress test

I tested the system by intentionally disconnecting the network multiple times during a 30 MB ingestion. Results:

Data integrity: 100% (verified with bit-offset checks).

Manual intervention: 0% (fully automated recovery).

Forensic evidence: See execution_audit.log for timestamps of each failure and the successful resumption.
