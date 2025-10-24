codebase for RFS tool

steps for installing and setting up RFS

1). Creating and activating a virtual environment
python3 -m venv .venv
source .venv/bin/activate
python -V
pip -V

2). Clone the code
git clone https://github.com/SNF-Root/Realtime-Furnace-Monitor.git
cd Realtime-Furnace-Monitor

3). Install deps
pip install -r requirements.txt
pip install .

4). Verify cli installation
rfs --help

5).Calibrating and Running respectively
rfs --calibrate
#after that to run the software
rfs --run
