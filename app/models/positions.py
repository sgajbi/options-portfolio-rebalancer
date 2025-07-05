from pydantic import Field
from typing import Union, Annotated
from .equity_position import EquityPosition
from .option_position import OptionPosition
from .bond_position import BondPosition
from .fx_spot_position import FXSpotPosition
from .fx_forward_position import FXForwardPosition
from .fx_swap_position import FXSwapPosition
from .time_deposit_position import TimeDepositPosition
from .fund_position import FundPosition


Position = Annotated[
    Union[
        EquityPosition,
        OptionPosition,
        BondPosition,
        FXSpotPosition,
        FXForwardPosition,
        FXSwapPosition,
        TimeDepositPosition,
        FundPosition
    ],
    Field(discriminator='type')
]
