"""
A demo to capture the TDCALL event using eBPF.
"""
from __future__ import print_function
from bcc import BPF

# load BPF program
b = BPF(text="""
#define EXIT_REASON_TDCALL 77
BPF_HASH(start, u8, u8);

TRACEPOINT_PROBE(kvm, kvm_exit) {
    u8 e = EXIT_REASON_TDCALL;
    u8 one = 1;
    if (args->exit_reason == EXIT_REASON_TDCALL) {
        bpf_trace_printk("KVM_EXIT for TDCALL : %d\\n", args->exit_reason);
        start.update(&e, &one);
    }
    return 0;
}

TRACEPOINT_PROBE(kvm, kvm_entry) {
    u8 e = EXIT_REASON_TDCALL;
    u8 zero = 0;
    u8 *s = start.lookup(&e);
    if (s != NULL && *s == 1) {
        bpf_trace_printk("KVM_ENTRY for TDCALL vcpu_id : %u\\n", args->vcpu_id);
        start.update(&e, &zero);
    }
    return 0;
}

""")

# header
print("%-18s %-16s %-6s %s", "TIME(s)", "COMM", "PID", "EVENT")

# format output
while 1:
    try:
        (task, pid, cpu, flags, ts, msg) = b.trace_fields()
    except ValueError:
        continue

    print("%-18.9f %-16s %-6d %s", ts, task, pid, msg)
