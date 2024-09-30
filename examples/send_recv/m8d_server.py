import argparse
import asyncio
import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from multiworld.manager import WorldManager

app = FastAPI()

device_no = None
world_manager_initialized = False
world_manager = None


def get_world_manager():
    global world_manager_initialized, world_manager
    if not world_manager_initialized:
        world_manager = WorldManager()
        world_manager_initialized = True
    return world_manager


class WorldInit(BaseModel):
    world_idx: int
    rank: int
    size: int
    backend: str = "nccl"
    addr: str = "127.0.0.1"


class TensorData(BaseModel):
    world_idx: int
    data: list


@app.post("/init_world")
async def init_world(world_init: WorldInit):
    world_manager = get_world_manager()
    world_name = f"world{world_init.world_idx}"
    port = 29500 + world_init.world_idx * 1000

    try:
        await world_manager.initialize_world(
            world_name,
            world_init.rank,
            world_init.size,
            backend=world_init.backend,
            addr=world_init.addr,
            port=port,
        )
        return {"message": f"World {world_name} initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/send")
async def send(tensor_data: TensorData):
    global device_no
    world_manager = get_world_manager()

    world_name = f"world{tensor_data.world_idx}"
    tensor = torch.tensor(tensor_data.data)

    # if world_manager.backend == "nccl":
    tensor = tensor.to(f"cuda:{device_no}")

    try:
        await world_manager.communicator.send(
            tensor, 1, world_name
        )  # Assuming sending to rank 1
        return {"message": "Data sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recv")
async def recv(tensor_data: TensorData):
    global device_no
    world_manager = get_world_manager()
    world_name = f"world{tensor_data.world_idx}"
    expected_tensor = torch.tensor(tensor_data.data)

    # if world_manager.backend == "nccl":
    expected_tensor = expected_tensor.to(f"cuda:{device_no}")

    received_tensor = torch.zeros_like(expected_tensor)

    try:
        await world_manager.communicator.recv(
            received_tensor, 0, world_name
        )  # Assuming receiving from rank 0
        await asyncio.sleep(0.5)  # make sure the data is sent
        if torch.all(received_tensor.eq(expected_tensor)):
            return {"message": "Data received successfully and matches expected tensor"}
        else:
            return {
                "message": "Data received but does not match expected tensor",
                "received": received_tensor.tolist(),
                "expected": expected_tensor.tolist(),
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def main(args):
    global device_no
    device_no = args.device_no
    uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--device_no", type=int, required=True)
    args = parser.parse_args()
    main(args)
