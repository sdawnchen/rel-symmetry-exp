import random
import numpy as np
import time
import cPickle


# ==========
# Parameters
# ==========

# Number of general relational types
num_types = 10
# The CD pairs for these subtypes should be reversed to best align with other subtypes of the same relation
rev_subtypes = ['2e', '9i', '10c']

# File containing the relational subtype names
paradigmsFileName = 'SemEval-2012-Complete-Data-Package/subcategories-paradigms.txt'

# Name prefixes of the files containing prototypicality ratings
ratingsFilePrefix = 'SemEval-2012-Gold-Ratings/GoldRatings-'

# Number of each kind of comparison desired
num_wi_subtype_wanted = 220
num_bt_subtype_wanted = 220
num_bt_type_wanted = 60

# Number of random subsets of stimuli
num_subsets = 20

# Name of output file
out_filename = 'static/js/SemEval-stimuli.js'


# ============================================================
# Create index pairs for all possible comparisons of each kind
# ============================================================

print 'Creating indices for all comparisons...'

# Get names of relational subtypes

subtypes = [[] for i in xrange(num_types)]

with open(paradigmsFileName, 'r') as paradigmsFile:
    for line in paradigmsFile:
        line = line.strip()
        parts = line.split(', ')
        reltype = int(parts[0]) - 1
        # The short name for the relation (e.g., "1a")
        relname = parts[0] + parts[1]
        subtypes[reltype].append(relname)


# Put all CD pairs into a nested list indexed first by the relational type, then by the subtype

all_CD_pairs = [[[] for subtype in xrange(len(subtypes[reltype]))] for reltype in xrange(num_types)]

for reltype in xrange(num_types):
    for subtype, relname in enumerate(subtypes[reltype]):
        ratingsFileName = ratingsFilePrefix + relname + '.txt'

        with open(ratingsFileName, 'r') as ratingsFile:
            subtype_pairs = all_CD_pairs[reltype][subtype]
            for line in ratingsFile:
                if line[0] != '#':   # skip over info at the top of the file
                    parts = line.split('"')
                    rating = float(parts[0].strip())
                    
                    if rating >= 0:
                        CDpair = parts[1].split(':')
                        
                        if relname in rev_subtypes:
                            rev_pair = CDpair
                            CDpair = [CDpair[1], CDpair[0]]
                        else:
                            rev_pair = [CDpair[1], CDpair[0]]
                            
                        # Don't add the CD pair if its reverse was previously added (i.e., has a
                        # higher prototypicality score)
                        if rev_pair not in subtype_pairs:
                            subtype_pairs.append(CDpair)
                    
                    # Skip to the next subtype if the prototypicality ratings are now negative
                    else:
                        break

# Get indices for within-subtype comparisons
wi_subtype_inds = []
for reltype in xrange(num_types):
    for subtype in xrange(len(subtypes[reltype])):
        num_pairs = len(all_CD_pairs[reltype][subtype])
        for i in xrange(num_pairs - 1):
            for j in xrange(i + 1, num_pairs):
                wi_subtype_inds.append(((reltype, subtype, i), (reltype, subtype, j)))

print len(wi_subtype_inds), ' total within-subtype comparisons'

# Get indices for between-subtype comparisons
bt_subtype_inds = []
for reltype in xrange(num_types):
    num_subtypes = len(subtypes[reltype])

    for subtype1 in xrange(num_subtypes - 1):
        num_pairs1 = len(all_CD_pairs[reltype][subtype1])

        for subtype2 in xrange(subtype1 + 1, num_subtypes):
            num_pairs2 = len(all_CD_pairs[reltype][subtype2])

            for i in xrange(num_pairs1):
                for j in xrange(num_pairs2):
                    bt_subtype_inds.append(((reltype, subtype1, i), (reltype, subtype2, j)))

print len(bt_subtype_inds), ' total between-subtype comparisons'

# Get indices for between-type comparisons
bt_type_inds = []
for reltype1 in xrange(num_types - 1):
    num_subtypes1 = len(subtypes[reltype1])

    for reltype2 in xrange(reltype1 + 1, num_types):
        num_subtypes2 = len(subtypes[reltype2])

        for subtype1 in xrange(num_subtypes1):
            num_pairs1 = len(all_CD_pairs[reltype1][subtype1])

            for subtype2 in xrange(num_subtypes2):
                num_pairs2 = len(all_CD_pairs[reltype2][subtype2])

                for i in xrange(num_pairs1):
                    for j in xrange(num_pairs2):
                        bt_type_inds.append(((reltype1, subtype1, i), (reltype2, subtype2, j)))

print len(bt_type_inds), ' total between-type comparisons'

wi_subtype_inds = np.array(wi_subtype_inds)
bt_subtype_inds = np.array(bt_subtype_inds)
bt_type_inds = np.array(bt_type_inds)


# ======================================
# Choose random comparisons of each kind
# ======================================

# Flag indicating whether the chosen stimuli are valid
invalid_stim = True


while invalid_stim:

    print 'Choosing stimuli for the experiment...'

    # Choose random within-subtype comparisons
    num_wi_subtype_comps = len(wi_subtype_inds)
    rand_wi_subtype_inds = random.sample(range(num_wi_subtype_comps), num_wi_subtype_wanted)
    chosen_wi_subtype_inds = wi_subtype_inds[rand_wi_subtype_inds]

    wi_subtype_comps = []
    for comp_inds in chosen_wi_subtype_inds:
        pair1_inds, pair2_inds = comp_inds
        reltype1, subtype1, i = pair1_inds
        reltype2, subtype2, j = pair2_inds
        pair1 = all_CD_pairs[reltype1][subtype1][i]
        pair2 = all_CD_pairs[reltype2][subtype2][j]
        comp = ((pair1[0], pair1[1]), (pair2[0], pair2[1]))
        wi_subtype_comps.append(comp)

    # Choose random between-subtype comparisons
    num_bt_subtype_comps = len(bt_subtype_inds)
    rand_bt_subtype_inds = random.sample(range(num_bt_subtype_comps), num_bt_subtype_wanted)
    chosen_bt_subtype_inds = bt_subtype_inds[rand_bt_subtype_inds]

    bt_subtype_comps = []
    for comp_inds in chosen_bt_subtype_inds:
        pair1_inds, pair2_inds = comp_inds
        reltype1, subtype1, i = pair1_inds
        reltype2, subtype2, j = pair2_inds
        pair1 = all_CD_pairs[reltype1][subtype1][i]
        pair2 = all_CD_pairs[reltype2][subtype2][j]
        relname1 = subtypes[reltype1][subtype1]
        relname2 = subtypes[reltype2][subtype2]
        comp = ((pair1[0], pair1[1]), (pair2[0], pair2[1]))
        bt_subtype_comps.append(comp)

    # Choose random between-type comparisons
    num_bt_type_comps = len(bt_type_inds)
    rand_bt_type_inds = random.sample(range(num_bt_type_comps), num_bt_type_wanted)
    chosen_bt_type_inds = bt_type_inds[rand_bt_type_inds]

    bt_type_comps = []
    for comp_inds in chosen_bt_type_inds:
        pair1_inds, pair2_inds = comp_inds
        reltype1, subtype1, i = pair1_inds
        reltype2, subtype2, j = pair2_inds
        pair1 = all_CD_pairs[reltype1][subtype1][i]
        pair2 = all_CD_pairs[reltype2][subtype2][j]
        relname1 = subtypes[reltype1][subtype1]
        relname2 = subtypes[reltype2][subtype2]
        comp = ((pair1[0], pair1[1]), (pair2[0], pair2[1]))
        bt_type_comps.append(comp)

    invalid_stim = True

    # Check whether the stimuli set is valid
    all_comps = set()
    for comp in wi_subtype_comps:
        pair1 = comp[0]
        pair2 = comp[1]
        if comp in all_comps:
            print 'Duplicate comparison, starting over...'
            invalid_stim = True
            break
        elif pair1 == pair2:
            print 'Comparison of identical pairs, starting over...'
            invalid_stim = True
            break
        elif pair1[0] == pair2[1] and pair1[1] == pair2[0]:
            print 'Comparison of reversed pairs, starting over...'
            invalid_stim = True
            break
        else:
            all_comps.add(comp)

    for comp in bt_subtype_comps:
        pair1 = comp[0]
        pair2 = comp[1]
        if comp in all_comps:
            print 'Duplicate comparison, starting over...'
            invalid_stim = True
            break
        elif pair1 == pair2:
            print 'Comparison of identical pairs, starting over...'
            invalid_stim = True
            break
        elif pair1[0] == pair2[1] and pair1[1] == pair2[0]:
            print 'Comparison of reversed pairs, starting over...'
            invalid_stim = True
            break
        else:
            all_comps.add(comp)
            
    for comp in bt_type_comps:
        pair1 = comp[0]
        pair2 = comp[1]
        if comp in all_comps:
            print 'Duplicate comparison, starting over...'
            invalid_stim = True
            break
        elif pair1 == pair2:
            print 'Comparison of identical pairs, starting over...'
            invalid_stim = True
            break
        elif pair1[0] == pair2[1] and pair1[1] == pair2[0]:
            print 'Comparison of reversed pairs, starting over...'
            invalid_stim = True
            break
        else:
            all_comps.add(comp)


# =======================================================
# Divide the comparisons chosen above into random subsets
# =======================================================

def get_subset_inds(num_items, num_subsets):
    """
    Get random indices for each subset. Constraints: (1) Half of each subset/group's comparisons
    are forward and half are backward. (2) No participant ever sees a comparison in both the
    forward and backward directions. (3) Each forward/backward comparison appears exactly once.
    """
    subset_size = num_items / num_subsets
    
    # Randomly shuffle the order of items
    rand_order = np.arange(num_items)
    np.random.shuffle(rand_order)
    
    # The first half of comparisons will be forward and the second half will be backward
    # (for the first half of subsets)
    half_items = num_items / 2
    forward1 = rand_order[:half_items]
    backward1 = rand_order[half_items:]
    
    # The forward comparisons from the first half of subsets will be backward in the second
    # half of subsets and in a different random order. Similarly for the backward comparisons
    # from the first half of subsets.
    forward2 = np.random.permutation(backward1)
    backward2 = np.random.permutation(forward1)
    
    # Partition each group of comparisons into subsets
    half_num_subsets = num_subsets / 2
    forward1 = forward1.reshape(half_num_subsets, subset_size)
    backward1 = backward1.reshape(half_num_subsets, subset_size)
    forward2 = forward2.reshape(half_num_subsets, subset_size)
    backward2 = backward2.reshape(half_num_subsets, subset_size)
    
    # Put all the parts together
    subsets1 = np.concatenate((forward1, backward1), axis = 1)
    subsets2 = np.concatenate((forward2, backward2), axis = 1)
    subsets = np.concatenate((subsets1, subsets2), axis = 0)
    
    return subsets
     
def get_subset_comp_inds(all_comp_inds, subsets):
    """
    Given subset indices created by get_subset_inds (i.e., first half of each subset is forward
    and second half of each subset is backward), get the comparison indices for each subset
    (i.e., each comparison is represented by a pair of [type index, subtype index, pair index]
    arrays).
    """
    num_subsets, subset_size = subsets.shape
    half = subset_size / 2
    subset_comp_inds = np.empty((num_subsets, subset_size, 2, 3), dtype = np.int)

    for subset in xrange(num_subsets):
        subset_inds = subsets[subset]
        forward_inds = subset_inds[:half]
        backward_inds = subset_inds[half:]
        forward_comp_inds = all_comp_inds[forward_inds]
        backward_comp_inds = all_comp_inds[backward_inds]
        backward_comp_inds = np.stack((backward_comp_inds[:, 1], backward_comp_inds[:, 0]), axis = 1)
        comp_inds = np.concatenate((forward_comp_inds, backward_comp_inds))
        subset_comp_inds[subset] = comp_inds
    
    return subset_comp_inds

def get_subset_comps(subset_comp_inds, all_CD_pairs, type_str):
    """
    Given subsets of comparison indices, get the actual comparisons.
    """
    num_subsets = subset_comp_inds.shape[0]
    subset_size = subset_comp_inds.shape[1]
    subset_comps = [[None for i in xrange(subset_size)] for s in xrange(num_subsets)]
    
    for subset in xrange(num_subsets):
        for item, comp_inds in enumerate(subset_comp_inds[subset]):
            pair1_inds, pair2_inds = comp_inds
            reltype1, subtype1, i = pair1_inds
            reltype2, subtype2, j = pair2_inds
            pair1 = all_CD_pairs[reltype1][subtype1][i]
            pair2 = all_CD_pairs[reltype2][subtype2][j]
            relname1 = subtypes[reltype1][subtype1]
            relname2 = subtypes[reltype2][subtype2]
            comp = [type_str, relname1, relname2, [pair1[0], pair1[1]], [pair2[0], pair2[1]]]
            subset_comps[subset][item] = comp
            
    return subset_comps


# Choose random subsets of each kind of comparison
wi_subtype_subsets = get_subset_inds(num_wi_subtype_wanted, num_subsets)
wi_subtype_subset_comp_inds = get_subset_comp_inds(chosen_wi_subtype_inds, wi_subtype_subsets)
wi_subtype_subset_comps = get_subset_comps(wi_subtype_subset_comp_inds, all_CD_pairs, 'within-subtype')

bt_subtype_subsets = get_subset_inds(num_bt_subtype_wanted, num_subsets)
bt_subtype_subset_comp_inds = get_subset_comp_inds(chosen_bt_subtype_inds, bt_subtype_subsets)
bt_subtype_subset_comps = get_subset_comps(bt_subtype_subset_comp_inds, all_CD_pairs, 'between-subtype')
    
bt_type_subsets = get_subset_inds(num_bt_type_wanted, num_subsets)
bt_type_subset_comp_inds = get_subset_comp_inds(chosen_bt_type_inds, bt_type_subsets)
bt_type_subset_comps = get_subset_comps(bt_type_subset_comp_inds, all_CD_pairs, 'between-type')

# Put the different kinds of comparisons together
all_subset_comps = [[] for s in xrange(num_subsets)]
for subset in xrange(num_subsets):
    comps = all_subset_comps[subset]
    comps.extend(wi_subtype_subset_comps[subset])
    comps.extend(bt_subtype_subset_comps[subset])
    comps.extend(bt_type_subset_comps[subset])

# Write the stimuli subsets to a file
with open(out_filename 'w') as out_file:
    out_file.write('var allComps = [\n')
    for subset in xrange(num_subsets):
        out_file.write('\t[\n')
        comps = all_subset_comps[subset]
        for comp in comps:
            out_file.write('\t\t' + str(comp) + ',\n')
        out_file.write('\t],\n')
    out_file.write('];\n')