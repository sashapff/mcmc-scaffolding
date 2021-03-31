import numpy as np

from tools.tools import get_distance


def get_ordering(ordering, pairs, contigs):
    """
    TODO
    """
    for pos in range(len(contigs)):
        for i in range(len(contigs)):
            if ordering[i] == pos and contigs[i] != ordering[i]:
                change_position(i, pos, pairs, contigs)


def change_position(number_changed_contig, position_changed_contig, pairs, contigs):
    """
    TODO
    """
    if position_changed_contig < contigs[number_changed_contig].pos:
        previous_pos = contigs[number_changed_contig].pos
        shift_length = 0
        for i in range(len(contigs)):
            if position_changed_contig <= contigs[i].pos < previous_pos:
                contigs[i].pos += 1

                ind = contigs[i].reads_ind
                a = (pairs[ind][:, 0] == i)
                indx_1 = np.where(a)[0]
                indx_2 = np.where(~a)[0]

                pairs[ind[indx_1], 6] -= contigs[number_changed_contig].length
                pairs[ind[indx_2], 6] += contigs[number_changed_contig].length
                shift_length += contigs[i].length

        ind = contigs[number_changed_contig].reads_ind
        a = (pairs[ind][:, 0] == number_changed_contig)
        indx_1 = np.where(a)[0]
        indx_2 = np.where(~a)[0]

        pairs[ind[indx_1], 6] += shift_length
        pairs[ind[indx_2], 6] -= shift_length

        for i in range(len(contigs)):
            if position_changed_contig < contigs[i].pos <= previous_pos and i != number_changed_contig:
                ind = contigs[i].reads_ind
                a = (pairs[ind][:, 0] == i)
                indx0 = np.where(a)[0]
                b = (pairs[ind[indx0]][:, 1] == number_changed_contig)
                indx = np.where(b)[0]

                pairs[ind[indx], 6] = -pairs[ind[indx], 6]

                pairs[ind[indx], 0], pairs[ind[indx], 2] = pairs[ind[indx], 2], pairs[ind[indx], 0]
                pairs[ind[indx], 1], pairs[ind[indx], 3] = pairs[ind[indx], 3], pairs[ind[indx], 1]
                pairs[ind[indx], 4], pairs[ind[indx], 5] = pairs[ind[indx], 5], pairs[ind[indx], 4]

        contigs[number_changed_contig].pos = position_changed_contig
    else:
        previous_pos = contigs[number_changed_contig].pos
        shift_length = 0
        for i in range(len(contigs)):
            if position_changed_contig >= contigs[i].pos > previous_pos:
                contigs[i].pos -= 1

                ind = contigs[i].reads_ind
                a = (pairs[ind][:, 0] == i)
                indx_1 = np.where(a)[0]
                indx_2 = np.where(~a)[0]

                pairs[ind[indx_1], 6] += contigs[number_changed_contig].length
                pairs[ind[indx_2], 6] -= contigs[number_changed_contig].length
                shift_length += contigs[i].length

        ind = contigs[number_changed_contig].reads_ind
        a = (pairs[ind][:, 0] == number_changed_contig)
        indx_1 = np.where(a)[0]
        indx_2 = np.where(~a)[0]

        pairs[ind[indx_1], 6] -= shift_length
        pairs[ind[indx_2], 6] += shift_length

        for i in range(len(contigs)):
            if position_changed_contig > contigs[i].pos >= previous_pos and i != number_changed_contig:
                ind = contigs[i].reads_ind
                a = (pairs[ind][:, 0] == i)
                indx0 = np.where(a)[0]
                b = (pairs[ind[indx0]][:, 1] == number_changed_contig)
                indx = np.where(b)[0]

                pairs[ind[indx], 6] = -pairs[ind[indx], 6]

                pairs[ind[indx], 0], pairs[ind[indx], 2] = pairs[ind[indx], 2], pairs[ind[indx], 0]
                pairs[ind[indx], 1], pairs[ind[indx], 3] = pairs[ind[indx], 3], pairs[ind[indx], 1]
                pairs[ind[indx], 4], pairs[ind[indx], 5] = pairs[ind[indx], 5], pairs[ind[indx], 4]

        contigs[number_changed_contig].pos = position_changed_contig


def change_position_log_likelihood(last_log_likelihood, number_changed_contig, position_changed_contig, pairs, contigs,
                                   P):
    """
    P(new_orientation) = P(old_orientation) + P(difference in orientation)
    """
    last_log_likelihood -= P(get_distance(pairs[contigs[number_changed_contig].reads_ind], contigs)).sum()
    change_position(number_changed_contig, position_changed_contig, pairs, contigs)
    new_lk = last_log_likelihood + P(get_distance(pairs[contigs[number_changed_contig].reads_ind], contigs)).sum()

    return new_lk