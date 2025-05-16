## slide 5
we can now explore the controllability of the exchange interaction achieved through shuttling.

the paper explores how the strength and quality, i.e. the coherence time, is affected by how the interaction is performed. Namley the possition of the spins and the offset of electrodes (especially barrier gate B3) during interaction.

what the paper did to characterize such interaction was the decoupled controlled-phase sequence. what this sequence does is essentially bring the two spins togeter to interact for a while, then observe the parallel probability as a function of conveyer cycle, i.e. distance between spins, and interaction time.

subplot (a) present the results for employing DCphase sequence with $B_3$ set at 65mV. we can see the coupling strength increases as conveyor cycle progress, before plateauing and subsequently decreasing.

subplot (b) exhibits the coupling strength at different B_3 offset. the same increasing then decrease pattern maintains. 

this is counterintuitive in the picture where two potential minima progressively move towards each other. It results from the fact that the central barrier gate B3 receives half the conveyor amplitude. This keeps the minima from the two conveyor channels separated by a tunnel barrier, which is desireable because this preserves the identity of each spin qubit, while still allowing a controlled exchange coupling.

now back to the plot, the exchange energy increase exponentially with offset, which the paper claims is consistent with the Fermi_Hubbard model describing tunnel-coupled quantum dots. They measured exchange strength up to 90MHz, greater strength are possible, but difficult to measure because the decay is too rapid under those conditions.

the paper persented experimental results for dephasing times as a function of conveyoer cycle. based on these characterization the paper concluded an operation regime that balances coupling strength nad coherence time. this condition correspond to 0.9 conveyor cycles and max coupling strength of 33MHz.

## slide 6
now that we know a ideal regime to perform two-qubit operation on this shuttling device, we can take a look how well can CZ gates be implemented. The experiment is done by preparing a target qubit in |y-> state(by rotating pi/2 along x axis), and prepare control state in |0> and |1> states. the operation is conducted in a 6-stages fashion to ensure speed and adiabaticity.

To access the final state the paper did sort of a spectroscopy on the transvers plane of the bloch sphere. what it does is to do z rotation of theta for many different angles from 0 to 2pi, than pulse the spin to the longintudinal axis and check parity with a known spin (using a variant of pauli spin blockade).

what we expect to see is the spectra is the spectrum of target qubit correspond to different control qubit to exhibit symmetry along the axis of parallel spin probability being 0.5, which is the case here for all four scenario. 

if we look closely there is a shift in phase from a pi difference for both cases, the paper attribute this to crosstalk from preparing spins for PSB and claim the CZ gate is properly calibrated at this point.

The benchmarking is done using IRB(interleaved randomized benchmarking), first do RB, get a reference error rate for reference sequences. then sandwich CZ gates between reference sequences, assume the errors are markonian and the error rate of the target gate can be calculated by some simple algegra. 

their results are 85.18% fidelity from reference measurement and 98.86% fidelity for CZ gates. please note of the 800 shots taken for each sequence, only apprximately 250 shots on average are being post selected, the paper justify this by refering to a paper that points out in order to accurately measure the fidelity of a specific gate, discarding shots that contains external error such as SPAM errors are justified.

## slide 7
the paper demonstrate how can we take advantage of spatially seperated entangled spins created by the mobile spin qubit approach by implementing  a conditional post-selected quantum state teleportation protocol(the name will make sense in a bit).

The protocal has three stages, 

in state preperation we prepare teh bell pair and the quantum state we need to teleport. 

in the bell measurement state we map the bell basis to computational basis using a unitary then do two measurements seperated by a CNOT. here cnot can be decompsed into rotation y and cz. 

Please note here the readout only provide parity information and therefore can only distinguish Phi- and Psi+, hence the conditional post selection.

The varification is done by two steps, first the polarization. subplot c shows the measurement result for Q2 correspond to the microwave burst time on Q6 for both post-selected scenario. this is essentially saying the polarization information of Q6 is indeed teleported onto Q2.

(below two are all done on post selected psi+ state)

then the phase, the idea is to apply a phase on Q6 and observe the phase on Q2 and see the relation ship of these two. the periodic result confirm the phase information is indeed teleported.

now the fidelity. they did quantum process tomography and reconstruct observations using least-squares optimization with CPTP(Complete positive and trace preserving) into a Pauli Transfer Matrix. the paper determine the average fidelity of the operation is 86.7% which is very much beyound classical bound of 2/3, indicating genuine quantum state teleportation.
