import asyncio
import random
class queue:

    def __init__(self):
        self.queue = []

    async def enqueue(self, item = None): #Blocks thread until item gets to the front of the list
        if item == None:
            item = random.randint(0,100000000)
        self.queue.append(item)
        while not self.queue[0] == item:
            await asyncio.sleep(0.05)

    async def dequeue(self):
        self.queue = self.queue[1:]
