import subprocess
import asyncio
import aiohttp
import subprocess
import random

BASE_URL = "http://localhost:{}"


def start_server(port, device_no):

    process = subprocess.Popen(
        ["python", "m8d_server.py", "--port", str(port), "--device_no", str(device_no)],
    )
    return process


def stop_server(process):
    process.terminate()
    process.wait()


async def init_world(session, port, world_idx, rank, size):
    url = f"{BASE_URL.format(port)}/init_world"
    data = {"world_idx": world_idx, "rank": rank, "size": size}
    async with session.post(url, json=data) as response:
        result = await response.json()
        print(f"Init world {world_idx} on port {port}: {result}")


async def send_data(session, port, world_idx, data):
    url = f"{BASE_URL.format(port)}/send"
    payload = {"world_idx": world_idx, "data": data}
    async with session.post(url, json=payload) as response:
        result = await response.json()
        print(f"Send data on port {port}, world {world_idx}: {result}")


async def recv_data(session, port, world_idx, expected_data):
    url = f"{BASE_URL.format(port)}/recv"
    payload = {"world_idx": world_idx, "data": expected_data}
    async with session.post(url, json=payload) as response:
        result = await response.json()
        print(f"Receive data on port {port}, world {world_idx}: {result}")


async def test_communication(session, port1, port2, world_idx1, world_idx2):
    data = [random.randint(1, 100) for _ in range(4)]

    await asyncio.gather(
        send_data(session, port1, world_idx1, data),
        recv_data(session, port2, world_idx2, data),
    )


async def main():
    ports = [8200, 8201, 8202]
    processes = [start_server(port, i) for i, port in enumerate(ports)]
    await asyncio.sleep(5)

    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            init_world(session, 8200, 0, 0, 2),
            init_world(session, 8201, 0, 1, 2),
            init_world(session, 8200, 1, 0, 2),
            init_world(session, 8202, 1, 1, 2),
            init_world(session, 8201, 2, 0, 2),
            init_world(session, 8202, 2, 1, 2),
        )

        print("Finish world initialization")
        await asyncio.sleep(5)

        await asyncio.gather(
            test_communication(session, 8200, 8201, 0, 0),
            test_communication(session, 8200, 8202, 1, 1),
            test_communication(session, 8201, 8202, 2, 2),
        )

        print("Finsh first stage communication test")

        stop_server(processes[1])
        print("Stopped server on port 8201")

        await test_communication(session, 8200, 8202, 1, 1)

        await asyncio.sleep(1)
        processes[1] = start_server(8201, 1)
        await asyncio.sleep(5)

        await asyncio.gather(
            init_world(session, 8200, 3, 0, 2),
            init_world(session, 8201, 3, 1, 2),
            init_world(session, 8201, 4, 0, 2),
            init_world(session, 8202, 4, 1, 2),
        )

        await asyncio.sleep(5)

        await asyncio.gather(
            test_communication(session, 8200, 8202, 1, 1),
            test_communication(session, 8200, 8201, 3, 3),
            test_communication(session, 8201, 8202, 4, 4),
        )

    for process in processes:
        stop_server(process)
    print("All servers stopped")


if __name__ == "__main__":
    asyncio.run(main())
