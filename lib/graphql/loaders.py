import strawberry.dataloader


class DataLoader[K, T](strawberry.dataloader.DataLoader[K, T]):
    def __init__(self) -> None:
        super().__init__(
            load_fn=self.execute,
            max_batch_size=100,
            cache=False,
        )

    async def execute(self, keys: list[K]) -> list[T | None | Exception]:
        # Implement the logic to load data based on the keys
        raise NotImplementedError("Subclasses must implement this method.")
