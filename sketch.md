## 1. The 20-port design’s correctness
Sophie mentioned the dimension of the SMA ports and the arrangement of the connector might cause an issue. **There is no issue here**, I got lucky with this design, it turned out the gaps between the connectors are big enough.


## 2. The primitivity of RO4350 in cryogenic temperature.
I mentioned RO4350B’s primitivity is 3.66 in room temperature and 3.45 in cryogenic temperature, which is not correct. This material has good thermal stability and the primitivity change caused by temperature is around **10ppm/K**, therefore primitivity remains approximately the same as temperature change. The numbers 3.66 and 3.45 are design value and process value respectively. The simulation is done using the latter, I’ll do simulation using both values and consult with the PCB fabrication people on which one is more representative.

## 3. The Q-factor mix up for candle qubits
There’s **no typo**. 
My theory is the first qubit’s simulation is done with SQuADDS’ workflow and the rest is done using my own, there exists difference in simulation setup that is adjusted in the **background program**. Judging by the metrics and their usual value, only the first qubit is simulated correctly, I’ll figure out what is done incorrectly with the rest of the qubits.