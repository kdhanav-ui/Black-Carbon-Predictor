import sys; sys.path.insert(0, ".")
from src.demo import make_demo
make_demo("data/demo_synthetic.csv", years=2.0)
print("wrote data/demo_synthetic.csv (SYNTHETIC)")
