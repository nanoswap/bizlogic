# IPFS Key Value Store 

[github.com/nanoswap/ipfsclient](https://github.com/nanoswap/ipfsclient)

# Installation

```
pip install ipfsclient
```

# Wrappers for IPFS RPC endpoints
```py
    from ipfsclient.ipfs import Ipfs

    client = ipfs.Ipfs()  # defaults to http://127.0.0.1:5001/api/v0
    client.mkdir("my_dir")
    client.add("my_dir/my_file", b"my_contents")
```
