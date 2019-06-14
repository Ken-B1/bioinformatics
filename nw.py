import sys
from Bio import SeqIO
from config import Config
from score import Score


class NW:
    def __init__(self, sequences, config=Config()):
        """
        Initialize a Needleman-Wunch instance to solve alignment
        :param sequences: A list of sequences which have to be aligned
        :param config: A config file which contains the scoring
        """
        self.sequences = sequences
        self.config = config
        self.matrix = self.initializeMatrix(sequences)
        self.enterelement([0]*len(self.sequences), Score([0]*len(self.sequences), 0))   # Set the origin of the matrix to 0
        self.counter = [1] + ([0] * (len(sequences)-1))                                 # Creates a counter which is used to transverse a matrix of arbitrary size

    def increase(self):
        """
            Increase the counter according to the matrix
            (0,0,0) -> (1,0,0)
            (4,0,0) if len(seq1) = 5 -> (0,1,0)
        """
        self.counter[0] += 1

        for x in range(len(self.sequences) -1):
            if self.counter[x] == len(self.sequences[x]) + 1:
                self.counter[x] = 0
                self.counter[x+1] += 1

    def generatebasepairs(self, x):
        """
        Method which takes coordinates and extracts the nucleotides from the sequences corresponding to the positions indicated in the coordinates
        for sequences "ABC" and "DEF" and x (1,2) this method returns "AE"
        For coordinates 0, the method will return a "_"
        :param x: Coordinates indicating the current position in the matrix
        :return: A string representing the bases corresponding to the coordinates
        """
        currentbases = ""
        for u, v in zip(x, range(len(x))):
            if u == 0:
                currentbases += '_'
            else:
                currentbases += self.sequences[v][u-1]

        return currentbases

    def generatemoves(self, x):
        """
            Generates all possible combinations of entering gaps for nucleotides x
            abc -> [abc, _bc, a_c, ab_, __c, _b_, a__]
            each combination is connected to a move in the matrix
            :param x: The current combination of bases to be considered
            :return: A list of possible moves generated by adding gaps in x
        """
        returnvalue = [x[0], "_"] if x[0] != '_' else [x[0]]

        for u in range(1, len(x)):
            if x[u] == '_':
                returnvalue = [y + "_" for y in returnvalue]
            else:
                returnvalue = [y + x[u] for y in returnvalue] + [y + "_" for y in returnvalue]

        returnvalue.remove(("_" * len(x)))
        return returnvalue

    def generatecoordinates(self, x, y):
        """
            For a given move x eg. "A_C" and the current coordinate y this method calculates the origin coordinate
            from which the current coordinate with the currrent move can be reached.
            a_c & (1,1,1) -> (1,0,1)
            :param x: a move x
            :param y: a coordinate y
            :return: a coordinate
        """
        entry = []
        for u, v in zip(x, y):
            if u == "_":
                entry.append(v)
            else:
                entry.append(v-1)

        return entry

    def getallpairs(self, x):
        """
            For a move with gaps generate all possible pairs
            a_c -> [a_, ac, _c]
            :param x: A move
        """
        result = []
        for u in range(len(x) - 1):
            result.extend([x[u] + a for a in x[u+1:]])

        return result

    def scorePair(self, x):
        """
            Generates a score for a pair x
            aa = config.match
            a_ = config.gap
            ab = config.mismatch
            __ = config.twogaps
            :param x: A pair
        """
        if x[0] == x[1] == '_':
            return self.config.twogaps
        elif x[0] == '_' or x[1] == '_':
            return self.config.gap
        elif x[0] == x[1]:
            return self.config.match
        else: return self.config.mismatch

    def retrievematrixelement(self, coord):
        """
            returns the element at coordinates coord, variable to the matrix size
            :param x: A coordinate
        """
        currentelement = self.matrix
        for u in coord:
            currentelement = currentelement[u]

        return currentelement

    def solve(self):
        """
            Function which solves the matrix according to the Needleman-Wunsch algorithm
        """
        while self.counter[-1] != len(self.sequences[-1]) + 1:
            basepair = self.generatebasepairs(self.counter)             # Get the combination for the current coordination
            moves = self.generatemoves(basepair)                        # Get all possible ways to get to this current coordination

            maxscore = -100000000                                       # set the maxscore to a value which is always lower than possible scores
            bestmove = None

            # FOr each move calculate score
            for move in moves:
                coordinates = self.generatecoordinates(move, self.counter) # generate the origin coordinate for the current move
                score = self.retrievematrixelement(coordinates).score      # Get the score at the origin coordinate
                pairs = self.getallpairs(move)                             # Get all pairs possible for the current move
                scores = [self.scorePair(u) for u in pairs]                # Generate scores for all pairs
                newscore = score + sum(scores)                          # Add generated scores to origin score
                if newscore > maxscore:
                    maxscore = newscore
                    bestmove = coordinates

            self.enterelement(self.counter, Score(bestmove, maxscore))
            self.increase()

    def enterelement(self, coordinate, value):
        """
            Enters value in the matrix at location coordinate
            :param coordinate: Coordinate where the value has to be entered
            :param value: The value to add to the matrix
        """
        currentlist = self.matrix
        for u in coordinate[:-1]:
            currentlist = currentlist[u]

        currentlist[coordinate[-1]] = value


    def initializeMatrix(self, seqs):
        """
            Initialize matrix according to the Needleman-Wunch algorithm
            :param seqs: The sequences which have to be alligned
        """
        currentSequence = seqs[0]
        if len(seqs) == 1:
            # Base case in the recursion, only 1 sequence left
            return [None] * (len(currentSequence) + 1)

        else:
            return [self.initializeMatrix(seqs[1:]) for x in range(len(currentSequence) + 1)]


    def __str__(self):
        """
        Prints the solution to the alignment problem if the matrix has been solved
        :return:
        """
        origin = [len(u) for u in self.sequences]
        currentorigin = origin
        returnstring = "The score for this alignment is: " + str(self.retrievematrixelement(origin).score) + "\n\n"

        if self.retrievematrixelement(origin) == None:
            return "The matrix has not been solved yet. Call the solve() method to solve the matrix."

        else:
            result = []
            resultstrings = [""] * len(self.sequences)
            while currentorigin != [0] * len(self.sequences):
                result.insert(0, self.retrievematrixelement(currentorigin).coordinate)
                currentorigin = result[0]

            result.append(origin)

            for u in range(1, len(result)):
                origin = result[u - 1]
                destination = result[u]
                for v in range(len(resultstrings)):
                    if origin[v] == destination[v]:
                        resultstrings[v] += "."
                    else:
                        resultstrings[v] += self.sequences[v][destination[v] - 1]

            for value in resultstrings:
                returnstring += value + '\n'

            return returnstring


def main():
    sequences = [SeqIO.read(u, "fasta") for u in sys.argv[1:]]
    if len(sequences) <= 1:
        print("Please give at least 2 sequences")
        return

    x = NW(sequences)
    x.solve()

    print(x)

if __name__ == "__main__":
    main()