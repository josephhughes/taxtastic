import collections
import logging
from itertools import combinations

log = logging.getLogger(__name__)

def union(it):
    "Take the union of an iterable of sets."

    ret = set()
    for x in it:
        ret.update(x)
    return ret

def intersection(it):
    "Take the intersection of an iterable of sets."

    ret = None
    for x in it:
        if ret is None:
            ret = set(x)
        else:
            ret.intersection_update(x)
    return ret or set()

CladeMetadata = collections.namedtuple(
    'CladeMetadata', 'parents colors cut_colors')

def color_clades(tree, colors):
    "Given a biopython tree and colors of its leaves, color its edges."

    parents = {tree.root: None}
    cut_colors = collections.defaultdict(set)
    stack = [('down', tree.root, None)]
    while stack:
        phase, cur, color = stack.pop()
        if phase == 'down':
            if not cur.clades:
                if cur not in colors:
                    continue
                stack.append(('up', cur, colors[cur]))
            else:
                for child in cur.clades:
                    parents[child] = cur
                    stack.append(('down', child, None))
        elif phase == 'up':
            if cur is None or color in cut_colors[cur]:
                continue
            cut_colors[cur].add(color)
            stack.append(('up', parents[cur], color))

    stack = [(tree.root, set())]
    while stack:
        node, okayed = stack.pop()
        if not node.clades:
            continue
        okayed = union(cut_colors[a] & cut_colors[b]
            for a, b in combinations(node.clades, 2)) | okayed
        for e in node.clades:
            e_ = cut_colors[e] & okayed
            if e_ != cut_colors[e]:
                stack.append((e, okayed))
                cut_colors[e] = e_

    return CladeMetadata(parents, colors, cut_colors)

def walk(cur, metadata):
    "Walk a biopython clade, determining the optimal convex subcoloring."

    parents, colors, cut_colors = metadata

    # The root node is reported to cut every color that crosses the root, but
    # we want to treat the root node as if it doesn't cut any color because we
    # only want the best set of nodes from the root.
    if parents[cur] is None:
        K = set()
    else:
        K = cut_colors[cur]

    ret = collections.defaultdict(dict)

    if not cur.clades:
        if K:
            color = colors[cur]
            assert len(K) == 1 and color in K
            ret[color][frozenset([color])] = {cur}
            ret[None][frozenset([color])] = {cur}
        else:
            ret[None][frozenset()] = {cur}
        return ret

    phi = [walk(x, metadata) for x in cur.clades]
    B = union(cut_colors[a] & cut_colors[b]
        for a, b in combinations(cur.clades, 2))

    for c in K | {None}:
        ret_c = collections.defaultdict(list)
        for b in B | {c}:
            def aux(phis, used_colors, accum):
                # Base case; we've reached the end of the list.
                if not phis:
                    ret_c[frozenset(used_colors)].append(accum)
                    return

                phi_i, phi_rest = phis[0], phis[1:]
                X_is = phi_i[b]

                # One possible solution is to ignore this `phi` completely.
                aux(phi_rest, used_colors, accum)

                if not X_is:
                    X_is = phi_i[None]

                for X_i in X_is:
                    if (X_i & used_colors) - {b}:
                        continue
                    if b != c and c in X_i:
                        continue
                    aux(phi_rest, used_colors | X_i, accum | X_is[X_i])

            aux(phi, set(), set())

        # For each `X_i`, the optimal `T_i` is the one with the most nodes in
        # it.
        ret[c] = {X_i: max(T_is, key=len) for X_i, T_is in ret_c.iteritems()}

    # If there were no cut colors, the only relevant data is the biggest set of
    # nodes, so prune everything else out.
    if not K:
        total = max(ret[None].itervalues(), key=len)
        ret.clear()
        ret[None][frozenset()] = total

    # If this is the parent node, return just the biggest set of nodes.
    if parents[cur] is None:
        return ret[None][frozenset()]

    return ret

Ranking = collections.namedtuple('Ranking', 'rank node')

def reroot_from_rp(root, rp, stop_at_first_root=True):
    name_map = dict(rp.db.cursor().execute("""
        SELECT seqname, tax_id
        FROM   sequences
    """))
    rank_map = dict(rp.db.cursor().execute("""
        SELECT tax_id, rank_order
        FROM   taxa
               JOIN ranks USING (rank)
    """))
    def subrk_min(terminals):
        mrca = rp.most_recent_common_ancestor(
            *{name_map[n.name] for n in terminals})
        return rank_map[mrca]

    return reroot(root, subrk_min, stop_at_first_root)

def all_parents(tree):
    parents = {}
    for clade in tree.find_clades():
        for child in clade:
            parents[child] = clade
    return parents

def reroot(cur, subrk_min, stop_at_first_root=True):
    parents = all_parents(cur)
    all_terminals = set(cur.get_terminals())
    prev = None

    log.debug('root: %r', cur)

    def all_clades(node):
        clades = list(node.clades)
        if node in parents:
            clades.append(parents[node])
        return clades

    def find_root(node):
        if not node.clades:
            return None
        ranks = [Ranking(subrk_min(n.get_terminals()), n) for n in node.clades]
        if node in parents:
            terminals = set(node.get_terminals())
            ranks.append(
                Ranking(subrk_min(all_terminals - terminals), parents[node]))
        ranks.sort()
        log.debug("rankings: %r", ranks)
        if ranks[0].rank == ranks[1].rank:
            return None
        return ranks[0].node

    while True:
        next = find_root(cur)
        if next is None:
            root = cur
            break
        elif next == prev:
            # If we're backtracking, there will only be two roots; we won't
            # need to traverse the tree for more roots.
            return cur, {prev}
        cur, prev = next, cur

    log.debug('found first root: %r', root)

    def is_root(node):
        if not node.clades:
            return False
        return find_root(node) is None

    other_roots = {n for n in all_clades(root) if is_root(n)}
    if stop_at_first_root:
        return root, other_roots

    seen = other_roots | {cur}
    stack = list(other_roots)
    while stack:
        log.debug('stack (%d): %r', len(stack), stack)
        cur = stack.pop()
        seen.add(cur)
        if find_root(cur) is None and cur.clades:
            other_roots.add(cur)
            stack.extend(n for n in all_clades(cur) if n not in seen)

    return root, other_roots
