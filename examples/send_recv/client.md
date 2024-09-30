# Option1: Run with python client

```bash
python client.py
```
# Option2: Run with curl client

## Starting the Servers

Run the following commands in separate terminals:

```bash
# Terminal 1
python m8d_server.py --port 8200 --device_no 0

# Terminal 2
python m8d_server.py --port 8201 --device_no 1

# Terminal 3
python m8d_server.py --port 8202 --device_no 2
```

## Testing Communication

Use the following curl commands to test the communication between servers:

### Initialize Worlds

```bash
curl -X POST -H "Content-Type: application/json" -d '{"world_idx": 0, "rank": 0, "size": 2}' http://localhost:8200/init_world
curl -X POST -H "Content-Type: application/json" -d '{"world_idx": 0, "rank": 1, "size": 2}' http://localhost:8201/init_world
curl -X POST -H "Content-Type: application/json" -d '{"world_idx": 1, "rank": 0, "size": 2}' http://localhost:8200/init_world
curl -X POST -H "Content-Type: application/json" -d '{"world_idx": 1, "rank": 1, "size": 2}' http://localhost:8202/init_world
curl -X POST -H "Content-Type: application/json" -d '{"world_idx": 2, "rank": 0, "size": 2}' http://localhost:8201/init_world
curl -X POST -H "Content-Type: application/json" -d '{"world_idx": 2, "rank": 1, "size": 2}' http://localhost:8202/init_world
```

### Test Data Transfer

```bash
# Test 1: 8200 -> 8201 (World 0)
curl -X POST -H "Content-Type: application/json" -d '{"world_idx": 0, "data": [1, 2, 3, 4]}' http://localhost:8200/send
curl -X POST -H "Content-Type: application/json" -d '{"world_idx": 0, "data": [1, 2, 3, 4]}' http://localhost:8201/recv

# Test 2: 8201 -> 8202 (World 2)
curl -X POST -H "Content-Type: application/json" -d '{"world_idx": 2, "data": [1, 2, 3, 4]}' http://localhost:8201/send
curl -X POST -H "Content-Type: application/json" -d '{"world_idx": 2, "data": [1, 2, 3, 4]}' http://localhost:8202/recv

# Test 3: 8202 -> 8200 (World 1)
curl -X POST -H "Content-Type: application/json" -d '{"world_idx": 1, "data": [1, 2, 3, 4]}' http://localhost:8200/send
curl -X POST -H "Content-Type: application/json" -d '{"world_idx": 1, "data": [1, 2, 3, 4]}' http://localhost:8202/recv
```

### Test After Stopping a Server

1. Stop the server running on port 8201 (Ctrl+C in Terminal 2).
2. Test communication between the remaining servers:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"world_idx": 1, "data": [1, 2, 3, 4]}' http://localhost:8200/send
curl -X POST -H "Content-Type: application/json" -d '{"world_idx": 1, "data": [1, 2, 3, 4]}' http://localhost:8202/recv
```

### Restart Server and Test New Worlds

1. Restart the server on port 8201:

```bash
# Terminal 2
python m8d_server.py --port 8201 --device_no 1
```

2. Initialize new worlds:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"world_idx": 3, "rank": 0, "size": 2}' http://localhost:8200/init_world
curl -X POST -H "Content-Type: application/json" -d '{"world_idx": 3, "rank": 1, "size": 2}' http://localhost:8201/init_world
curl -X POST -H "Content-Type: application/json" -d '{"world_idx": 4, "rank": 0, "size": 2}' http://localhost:8201/init_world
curl -X POST -H "Content-Type: application/json" -d '{"world_idx": 4, "rank": 1, "size": 2}' http://localhost:8202/init_world
```

3. Test communication in new worlds:

```bash
# Test 1: 8200 -> 8201 (World 3)
curl -X POST -H "Content-Type: application/json" -d '{"world_idx": 3, "data": [1, 2, 3, 4]}' http://localhost:8200/send
curl -X POST -H "Content-Type: application/json" -d '{"world_idx": 3, "data": [1, 2, 3, 4]}' http://localhost:8201/recv

# Test 2: 8201 -> 8202 (World 4)
curl -X POST -H "Content-Type: application/json" -d '{"world_idx": 4, "data": [1, 2, 3, 4]}' http://localhost:8201/send
curl -X POST -H "Content-Type: application/json" -d '{"world_idx": 4, "data": [1, 2, 3, 4]}' http://localhost:8202/recv
```