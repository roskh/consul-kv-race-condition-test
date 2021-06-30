# Consul race-conditions tests

## Instructions

```sh
# this will bot 3 consul servers with 2 followers and a leader, go to http://localhost:8500/ui to check if nodes loaded correctly
docker-compose up

# will run requests, modify the constants in 'main.py' to modify test timings or requested nodes
python3 main.py
```

## Conclusions
