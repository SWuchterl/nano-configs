# write a python script that opens the root tree and checks which branches take what size to store
import ROOT
import sys
import os


# convert the size to human readable format
def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Y', suffix)

def analyze_tree(filename):
    f = ROOT.TFile.Open(filename)
    # print compression algorithm and level
    print("Compression algorithm:", f.GetCompressionAlgorithm())
    print("Compression level:", f.GetCompressionLevel())
    # print number of entries
    print("Number of entries:", f.Get("Events").GetEntries())

    tree = f.Get("Events")
    tree.GetEntry(0)  # Load the first entry to initialize branches

    branch_sizes = {}
    branch_sizes_human = {}
    for branch in tree.GetListOfBranches():
        branch_name = branch.GetName()
        # branch_size = branch.GetTotalSize()  # Total size in bytes
        branch_size = branch.GetZipBytes()  # Total size in bytes
        # get size on disk
        # branch_size_on_disk = branch.GetZipBytes()  # Compressed size on disk

        branch_size_human = sizeof_fmt(branch_size)
        # print(f"Branch: {branch_name}, Size: {branch_size_human} ({branch_size} bytes)")
        branch_sizes[branch_name] = branch_size
        branch_sizes_human[branch_name] = branch_size_human

    return branch_sizes, branch_sizes_human, f.Get("Events").GetEntries()




if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python analizeSize.py <root_file> <output_folder>")
        sys.exit(1)

    filename = sys.argv[1]
    output_folder = sys.argv[2]
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    sizes, sizes_human, nEntries = analyze_tree(filename)
    # make a pie chart by groups with same beginning of the branch name split by "_"
    grouped_sizes = {}
    for branch, size in sizes.items():
        group = branch.split("_")[0]
        grouped_sizes[group] = grouped_sizes.get(group, 0) + size
    sizes = grouped_sizes

    # now convert the grouped sizes to a human readable format
    grouped_sizes_human = {}
    for group, size in sizes.items():
        grouped_sizes_human[group] = sizeof_fmt(size)
    sizes_human = grouped_sizes_human

    import matplotlib.pyplot as plt

    labels = sizes.keys()
    sizes_values = sizes.values()

    plt.figure(figsize=(10, 10))
    plt.pie(sizes_values, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title(f"Branch sizes in file: {filename.split('/')[-1]}")
    # plt.show()
    plt.savefig(f"{output_folder}/branch_sizes_pie_chart_{filename.split('/')[-1].replace('.root', '')}.png")

    # sort sizes by size d escending
    sizes = dict(sorted(sizes.items(), key=lambda item: item[1], reverse=True))
    sizes_human = dict(sorted(sizes_human.items(), key=lambda item: sizes[item[0]], reverse=True))

    # write this into a log file
    with open(f"{output_folder}/branch_sizes_{filename.split('/')[-1].replace('.root', '')}.log", "w") as f:
        f.write(f"Branch sizes in file: {filename}\n")
        for branch, size in sizes_human.items():
            f.write(f"{branch}: {size} total\n")
        total_size = sum(sizes.values())
        f.write(f"\nTotal size of all branches: {sizeof_fmt(total_size)}\n")
        f.write(f"Total size per entry: {sizeof_fmt(total_size/nEntries)} per entry\n")

    print("Branch sizes in file:", filename)
    for branch, size in sizes_human.items():
        # print(f"{branch}: {size/nEntries} per entry - ({size} total)")
        print(f"{branch}: {size} total")
    # print total size per entry
    total_size = sum(sizes.values())
    print ("\nTotal size of all branches:")
    print (sizeof_fmt(total_size))
    print(f"Total size per entry: {sizeof_fmt(total_size/nEntries)} per entry")