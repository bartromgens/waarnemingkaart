# compile
TARGET = density
 
$(TARGET).so: $(TARGET).cpp
	g++ -O3 -Wall -shared -std=c++11 -fPIC `python -m pybind11 --includes` $(TARGET).cpp -o $(TARGET)`python-config --extension-suffix`
