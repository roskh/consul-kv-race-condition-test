# Consul race-conditions tests

Test setup for testing race conditions when updating a single consul KV key in parallel (using [create key endpoint](https://www.consul.io/api/kv#create-update-key)), using server replicas.

The test environment consists a of 3 consul instances (agent Server) running, with 2 followers and 1 leader. A request to update the KV can be made to any of these 3 servers.

The script makes 2 HTTP requests (A and B). The duration of these requests , the delay of B compared to A, and to which of the 3 nodes each A or B is sent can be modified in the script to achieve different tests.

## Instructions

```sh
# this will bot 3 consul servers with 2 followers and a leader, go to http://localhost:8500/ui to check if nodes loaded correctly
docker-compose up

# will run requests, modify the constants in 'main.py' to modify test timings or requested nodes
python3 main.py
```

## Conclusions

Given http requests A and B and values 'a' and 'b' as in the script.

- Only when a request sends it's final byte (ends) in the body is the request considered by consul for timestamps, when the first byte of the request arrives in consul doesn't seem to matter.
- The value cannot be corrupet, even if A and B are made at the same time, the value will take either 'a' or 'b' and not a corrupted mix.
- When A and B are made to the same master server: if a request ends slighly after the final value it is the final value.
- When A and B are made to different follower servers: if A and B end at the same time the final value can be either of 'a' or 'b'.

## Misc

- You can check that the script will actually stream the bytes by running `nc -k -l 4444` and sending a request there.