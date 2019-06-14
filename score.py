class Score:
    """
        Datastructure representing a score in a matrix
        x, y: the coordinates of the originating cell
        score: The score for this cell
        move: The move that lead to this cell (d = diagonal, g1 = gap in seq 1, g2 = gap in seq2, u = undefined: used for (0,0))
    """

    def __init__(self, coordinate, score, move=None):
        self.coordinate = coordinate
        self.score = score
        self.move = move

    def __str__(self):
        return str(self.score)
