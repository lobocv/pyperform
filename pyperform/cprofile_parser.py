import marshal
import os

from tools import convert_time_units


class cProfileFuncStat(object):
    """
    Class that represents a item in the pstats dictionary
    """
    stats = {}
    run_time_s = 0
    n_decimal_percentages = 2

    def __init__(self, filename, lineno, name, ncalls, ncall_nr, total_time, cum_time, subcall_stats=None):
        self.filename = filename
        self.line_number = lineno
        self.name = name
        self.ncalls = ncalls
        self.nonrecursive_calls = ncall_nr
        self.own_time_s = total_time
        self.cummulative_time_s = cum_time
        self.exclude = False
        self.parent = None

        if (filename, lineno, name) not in cProfileFuncStat.stats:
            cProfileFuncStat.stats[(filename, lineno, name)] = self
            cProfileFuncStat.run_time_s += self.own_time_s

        if subcall_stats:
            self.subcall = cProfileFuncStat.from_dict(subcall_stats)
            for s in self.subcall:
                s.parent = self
        else:
            self.subcall = subcall_stats

    @property
    def total_time(self):
        return convert_time_units(self.own_time_s)

    @property
    def cummulative_time(self):
        return convert_time_units(self.cummulative_time_s)

    @property
    def percentage_cummulative(self):
        return round(100 * self.cummulative_time_s / cProfileFuncStat.run_time_s, cProfileFuncStat.n_decimal_percentages)

    @property
    def percentage_own(self):
        return round(100 * self.own_time_s / cProfileFuncStat.run_time_s, cProfileFuncStat.n_decimal_percentages)

    @property
    def per_call_time(self):
        return self.own_time_s / self.ncalls

    @property
    def per_call_time_non_recursive(self):
        return self.own_time_s / self.nonrecursive_calls

    @classmethod
    def from_dict(cls, d):
        """Used to create an instance of this class from a pstats dict item"""
        stats = []
        for (filename, lineno, name), stat_values in d.iteritems():
            if len(stat_values) == 5:
                ncalls, ncall_nr, total_time, cum_time, subcall_stats = stat_values
            else:
                ncalls, ncall_nr, total_time, cum_time = stat_values
                subcall_stats = None
            stat = cProfileFuncStat(filename, lineno, name, ncalls, ncall_nr, total_time, cum_time, subcall_stats)
            stats.append(stat)

        return stats

    def to_dict(self):
        """Convert back to the pstats dictionary representation (used for saving back as pstats binary file)"""
        if self.subcall is not None:
            if isinstance(self.subcall, dict):
                subcalls = self.subcall
            else:
                subcalls = {}
                for s in self.subcall:
                    subcalls.update(s.to_dict())
            return {(self.filename, self.line_number, self.name): \
                        (self.ncalls, self.nonrecursive_calls, self.own_time_s, self.cummulative_time_s, subcalls)}
        else:
            return {(self.filename, self.line_number, self.name): \
                        (self.ncalls, self.nonrecursive_calls, self.own_time_s, self.cummulative_time_s)}

    def __repr__(self):
        return "{s.name}: total={s.total_time}, cum={s.cummulative_time}" \
               " N={s.ncalls}, N_nr={s.nonrecursive_calls}".format(s=self)


class cProfileParser(object):
    """
    A manager class that reads in a pstats file and allows futher decontruction of the statistics.
    """
    def __init__(self, pstats_file):
        self.path = pstats_file

        with open(stat_file, 'rb') as _f:
            self.raw_stats = _f.read()

        with open(stat_file, 'r') as _f:
            self.stats_dict = marshal.load(_f)

        self.stats = cProfileFuncStat.from_dict(self.stats_dict)

    def exclude_functions(self, *funcs):
        """
        Excludes the contributions from the following functions.
        """
        for f in funcs:
            f.exclude = True
        run_time_s = sum(0 if s.exclude else s.own_time_s for s in self.stats)
        cProfileFuncStat.run_time_s = run_time_s

    def get_top(self, stat, n):
        """Return the top n values when sorting by 'stat'"""
        return sorted(self.stats, key=lambda x: getattr(x, stat), reverse=True)[:n]

    def save_pstat(self, path):
        """
        Save the modified pstats file
        """
        stats = {}
        for s in self.stats:
            if not s.exclude:
                stats.update(s.to_dict())

        with open(path, 'wb') as f:
            marshal.dump(stats, f)


if __name__ == '__main__':

    stat_folder = "/home/local/SENSOFT/clobo/.PyCharm2016.1/system/snapshots"
    stat_file = os.path.join(stat_folder, 'lmx64.pstat')
    stat_file_out = os.path.join(stat_folder, 'lmx64-modified.pstat')

    parser = cProfileParser(stat_file)
    top_5 = parser.get_top('own_time_s', 5)
    parser.exclude_functions(*top_5)
    asd = parser.save_pstat(stat_file_out)
    dfg=3
