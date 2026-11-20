"""What a run costs, from a dated price table.

Model prices change. The table carries the date it was read and its source, so a
figure on a board page can always be traced to a price that was true on a day. A
company that uses this repository puts its own contract prices in data/prices.json.

Costs are computed in USD, because that is how models are priced, and converted to
euro at a rate the company states. The rate is an assumption and is labelled as one
everywhere it appears.
"""
from . import load


class PriceError(ValueError):
    """A model with no price in the table. The ledger stops rather than guess a price."""


class Prices:
    def __init__(self, table: dict | None = None):
        self.table = table if table is not None else load("prices.json")
        self.models = self.table["models"]
        self.eur_per_usd = self.table["eur_per_usd"]
        self.as_read_on = self.table["as_read_on"]
        self.source = self.table["source"]

    def model_name(self, written: str) -> str:
        """Run records write the model as 'claude-fable-5-2, effort medium'. The price
        follows the model, not the effort, so the name is read up to the first comma."""
        name = (written or "").split(",")[0].strip()
        if name not in self.models:
            raise PriceError(f"No price for the model '{name}' in the table read on {self.as_read_on}. "
                             f"Priced models: {sorted(self.models)}.")
        return name

    def usd(self, tokens: dict, model: str) -> float:
        """List-price cost of one run, in USD."""
        price = self.models[self.model_name(model)]
        return tokens["input"] / 1e6 * price["input"] + tokens["output"] / 1e6 * price["output"]

    def eur(self, tokens: dict, model: str) -> float:
        """Full precision on purpose. A cheap model at high volume costs a fraction of a cent a
        run; rounding here and multiplying afterwards prices a whole year at zero. Rounding
        belongs to the yearly figure and to the page, not to the unit cost."""
        return self.usd(tokens, model) * self.eur_per_usd
