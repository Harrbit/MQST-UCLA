import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Define the sequence steps
steps = [
    "Init", "Rx(π/2)", "Shuttle", "Exchange t/2", "Return",
    "Rx(π)", "Shuttle", "Exchange t/2", "Return", "Rx(π/2)", "Readout"
]
times = list(range(len(steps)))

# Define qubit operations
q2_ops = [
    "Init", "Rx(π/2)", "Shuttle", "Idle", "Return",
    "Rx(π)", "Shuttle", "Idle", "Return", "Rx(π/2)", "Measure"
]
q5_ops = [
    "Init", "", "Shuttle", "Idle", "Return",
    "Rx(π)", "Shuttle", "Idle", "Return", "", "Measure"
]

fig, ax = plt.subplots(figsize=(10, 3))
ax.set_xlim(-0.5, len(steps)-0.5)
ax.set_ylim(0, 2)
ax.set_yticks([0.5, 1.5])
ax.set_yticklabels(["Q5", "Q2"])

# Draw operations as boxes
for i, (op_q2, op_q5) in enumerate(zip(q2_ops, q5_ops)):
    if op_q2:
        ax.add_patch(patches.Rectangle((i - 0.4, 1.2), 0.8, 0.6, edgecolor='black', facecolor='lightblue'))
        ax.text(i, 1.5, op_q2, ha='center', va='center', fontsize=9)
    if op_q5:
        ax.add_patch(patches.Rectangle((i - 0.4, 0.2), 0.8, 0.6, edgecolor='black', facecolor='lightgreen'))
        ax.text(i, 0.5, op_q5, ha='center', va='center', fontsize=9)

# Draw lines for the timeline
ax.hlines([0.5, 1.5], -0.5, len(steps)-0.5, colors='gray', linestyles='dotted')

ax.set_xticks(times)
ax.set_xticklabels(steps, rotation=45, ha='right')
ax.set_title("DCPhase Sequence for Q2 and Q5")
ax.axis('off')

plt.tight_layout()
plt.show()
