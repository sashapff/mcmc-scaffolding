from tools.load import get_contigs_and_pairs
from orientation.model import MCMC
from orientation.orientation_tools import get_orientation
from tools.prob import density, toy_density
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    print("Start!")

    correct_total = 0
    contigs_total = 0
    chromosomes = ['1', '2', '3', '4', '5', '6', '7', '8', '10', '11', '12', '13',
                   '14', '15', '16', '17', '18', '19', '20', '21', '22']

    # chromosomes = ['2', '3']

    pairs_arr, contigs_arr, id_contig_arr, longest_contig_arr, longest_contig_name_arr, correct_contigs_arr = [], [], [], [], [], []

    min_contig_length = 100_000
    min_contig_length_name = '100k'

    for chr_ind in chromosomes:
        print(f'Chromosome {chr_ind}')

        path_layout = "/GWSPH/groups/cbi/Users/pavdeyev/HiCProject/layouts/chr" + chr_ind + ".layout.txt"

        # if chr_ind == '9':
        # path_layout = "/GWSPH/groups/cbi/Users/pavdeyev/HiCProject/layouts/chr9.partial_layout.txt"

        path_lens = "/lustre/groups/cbi/Users/aeliseev/aivanova/data/contig_length/contig.length." + chr_ind + ".txt"
        path_pairs = "/lustre/groups/cbi/Users/aeliseev/aivanova/data/pairs/chr_pairs" + chr_ind + ".txt"

        # longest_contig
        pairs, contigs, id_contig, longest_contig, longest_contig_name = get_contigs_and_pairs(path_layout, path_lens,
                                                                                               path_pairs,
                                                                                               long_contig=True,
                                                                                               min_len=min_contig_length)

        # # path_layout = "/Users/alexandra/bioinf/mcmc/data/chr1.layout.txt"
        # path_layout = "/Users/alexandra/bioinf/mcmc/data/simulation.layout.txt"
        #
        # # path_lens = "/Users/alexandra/bioinf/mcmc/data/comp18_lens.tsv"
        # path_lens = "/Users/alexandra/bioinf/mcmc/data/simulation.lens.tsv"
        #
        # # path_pairs = "/Users/alexandra/bioinf/mcmc/data/pairs18.txt"
        # path_pairs = "/Users/alexandra/bioinf/mcmc/data/simulation.pairs.txt"
        #
        # # longest_contig
        # # pairs, contigs, id_contig, longest_contig, longest_contig_name = get_contigs_and_pairs(path_layout, path_lens, path_pairs,
        #                                                                   long_contig=True)
        # pairs, contigs, id_contig, longest_contig, longest_contig_name, in_contigs = get_contigs_and_pairs(path_layout, path_lens, path_pairs,
        #                                                                               long_contig=True,
        #                                                                               all_contigs=True,
        #                                                                               min_len=0)

        correct_contigs = [contig.o for contig in contigs]

        pairs_arr.append(pairs)
        contigs_arr.append(contigs)
        id_contig_arr.append(id_contig)
        longest_contig_arr.append(longest_contig)
        longest_contig_name_arr.append(longest_contig_name)
        correct_contigs_arr.append(correct_contigs)

    print("Estimation of density...")

    j = 0
    longest_contig_length = 0
    for i in range(len(longest_contig_name_arr)):
        if longest_contig_name_arr[i].length > longest_contig_length:
            longest_contig_length = longest_contig_name_arr[i].length
            j = i
    longest_contig = longest_contig_name_arr[j].name

    longest_pairs_numpy = longest_contig_arr[j]

    P, f = density(longest_pairs_numpy)
    # P, f = toy_density(longest_pairs_numpy)
    print("Estimation of density is done")

    for (j, chr_ind) in enumerate(chromosomes):
        pairs, contigs, id_contig, correct_contigs \
            = pairs_arr[j], contigs_arr[j], id_contig_arr[j], correct_contigs_arr[j]

        print("MCMC is running...")
        get_orientation([0 for i in range(len(contigs))], pairs, contigs)
        accuracy_arr = MCMC(pairs, contigs, P, number_it=200, n_chains=1, id_contig=id_contig,
                            correct_contigs=correct_contigs)
        print("Have found follow orientation:", [contigs[i].o for i in range(len(contigs))])

        with open("/lustre/groups/cbi/Users/aeliseev/aivanova/data/final" + chr_ind + ".layout.txt", "w") as file:
            sign = lambda x: "+" if x == 1 else "-"
            file.write(",".join([contig.name + sign(contig.o) for contig in contigs]))
        print("Result has been saved")

        print("Count correctness...")
        correct_number = np.array([contig.o == correct_contigs[id_contig[contig.name]] for contig in contigs]).sum()
        print(
            f"{correct_number}/{len(contigs)} contigs were oriented correctly ({correct_number / len(contigs) * 100}%)")

        with open(f"/lustre/groups/cbi/Users/aeliseev/aivanova/data/stat_{min_contig_length_name}.txt", "a") as file:
            file.write(f"CHROMOSOME {chr_ind}\n")
            file.write(
                f"{correct_number}/{len(contigs)} contigs were oriented correctly ({correct_number / len(contigs) * 100}%)\n")

        correct_total += correct_number
        contigs_total += len(contigs)

        print(accuracy_arr)
        plt.clf()
        plt.plot(accuracy_arr)
        plt.savefig(f'/lustre/groups/cbi/Users/aeliseev/aivanova/data/plots/accuracy_chr{chr_ind}_{min_contig_length_name}.png')

    with open(f"/lustre/groups/cbi/Users/aeliseev/aivanova/data/stat_{min_contig_length_name}.txt", "a") as file:
        file.write(f"TOTAL ACCURACY\n")
        file.write(
            f"{correct_total}/{contigs_total} contigs were oriented correctly ({correct_total / contigs_total * 100}%)\n")
