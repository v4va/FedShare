# FedShare
This repository contains the official implementation of FedShare. 
The implementation is based on `Python 3.8.8` and `tensorflow 2.9.1`.

There are a couple of different files named '*common.py' like 'mnistcommon.py'. These files will be used for all three algorithms, 
including FedShare, SCOTCH, and FedAvg. The default is 'mnist' dataset. But if you are interested in running the experiments on other datasets, you should replace 'import mnistcommon' with 'import emnistcommon' for example. 

For a quick start you can use:
```
git clone https://github.com/v4va/FedShare.git
```

```
chmod +x start-fedshare.sh
chmod +x start-fedavg.sh
chmod +x start-scotch.sh
```

For FedShare:
```
./start-fedshare.sh
```
For FedAvg:
```
./start-fedavg.sh
```
For SCOTCH:
```
./start-scotch.sh
```

By default `m=5` and `n=2`. If you are interested in changing these values, first change `config.py` and then change `start-*.sh` file.
For checking results and training process, check `logs` folder.

Please feel free to contact us if you are facing any difficulty or have any questions regarding this project.

