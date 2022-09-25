
## How to run

```bash
sudo apt-get install python3-pip
```

```py3
conda create -n wenet python=3.8
```

```py3
pip install -r requirement.txt
```

Pyaudio cho người trầm cảm
```
sudo apt install portaudio19-dev
```

### How to test?

> Idk :)

## TODO:

- [ ] Write .proto file to define the gRPC services and messages.
- [ ] Write a server to process the submitted chunks audio and returns back the response texts.
- [ ] Write a client to talk to the server.
- [ ] Write/use a scheduler/tools to perform stress test for connection.