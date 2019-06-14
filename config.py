class Config:
    """
    Config is used to store the scores in a central place
    """

    def __init__(self, match=5, mismatch=-2, gap=-4, twogaps=0):
        self.match = match
        self.mismatch = mismatch
        self.gap = gap
        self.twogaps = twogaps