from enum import Enum


class TokenType(Enum):
    WORD = 0
    TAG = 1
    CHANNEL = 2


class Token:
    def __init__(self, value: str):
        self.value: str = value
        # TODO: deduire le reste
        '''
        self.ttype: TokenType = ttype
        self.did: Optional[int] = discord_id
        self.text: str = text if text is not None else self.value
        '''