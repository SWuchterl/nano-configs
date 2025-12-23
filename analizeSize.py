# write a python script that opens the root tree and checks which branches take what size to store
import ROOT
import sys
def analyze_file(filename):
    f = ROOT.TFile.Open(filename)
    tree = f.Get("Events")
    tree.GetEntry(0)  # Load the first entry to initialize branches

    branch_sizes = {}
    for branch in tree.GetListOfBranches():
        branch_name = branch.GetName()
        branch_size = branch.GetTotalSize()  # Total size in bytes
        branch_sizes[branch_name] = branch_size

    return branch_sizes
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analizeSize.py <root_file>")
        sys.exit(1)

    filename = sys.argv[1]
    sizes = analyze_file(filename)
    # make a pie chart by groups with same beginning of the branch name split by "_"
    grouped_sizes = {}
    for branch, size in sizes.items():
        group = branch.split("_")[0]
        grouped_sizes[group] = grouped_sizes.get(group, 0) + size
    sizes = grouped_sizes
    import matplotlib.pyplot as plt

    labels = sizes.keys()
    sizes_values = sizes.values()

    plt.figure(figsize=(10, 10))
    plt.pie(sizes_values, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title(f"Branch sizes in file: {filename}")
    plt.show()
    plt.savefig("branch_sizes_pie_chart.png")

    print("Branch sizes in file:", filename)
    for branch, size in sizes.items():
        print(f"{branch}: {size} bytes")