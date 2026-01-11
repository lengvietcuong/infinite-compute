# How NVIDIA Makes GPUs

## Introduction

NVIDIA manufactures its Graphics Processing Units (GPUs) through a sophisticated, multi-stage process that combines cutting-edge semiconductor design, advanced fabrication techniques, and complex assembly operations. Rather than operating its own fabrication facilities, NVIDIA operates as a fabless semiconductor company, partnering with world-leading manufacturers like TSMC (Taiwan Semiconductor Manufacturing Company) and various assembly partners globally. The process spans from initial architectural design through to final quality testing, involving some of the most complex manufacturing technologies in existence today.

## Phase 1: Design and Architecture Development

### GPU Architecture Conceptualization

The journey of creating a GPU begins with architectural planning and design. NVIDIA's engineering teams conceptualize the fundamental architecture of the GPU, establishing the core computational philosophy. Modern NVIDIA GPUs are organized hierarchically around several architectural levels:

**Graphics Processing Clusters (GPCs)**: The top-level organizational unit that manages workload distribution and contains multiple processing elements.

**Texture Processing Clusters (TPCs)**: Intermediate clusters that house Streaming Multiprocessors and texture units for specialized processing tasks.

**Streaming Multiprocessors (SMs)**: The computational engines of the GPU, each containing CUDA cores, registers, cache memories, and control logic. These are the fundamental building blocks of NVIDIA's parallel processing architecture.

**CUDA Cores**: The smallest processing units within an SM, each capable of performing integer operations, floating-point calculations (FP32, FP16, FP8), and memory access operations. Modern high-end GPUs can contain tens of thousands of these cores working in parallel.

### Design Specification and Simulation

After establishing the architecture, NVIDIA engineers create detailed design specifications and blueprints. This involves:

**Circuit design and optimization** to ensure proper electrical characteristics, timing, and power efficiency. Engineers use sophisticated Electronic Design Automation (EDA) tools to simulate and verify the design at multiple levels of abstraction.

**Functional verification and simulation** to confirm that the design operates correctly before committing to expensive fabrication. These simulations can consume enormous computational resources, and NVIDIA notably uses GPUs to accelerate its own design verification process—a process known as "eating its own dog food."

**Power analysis and thermal management planning** to ensure the GPU can dissipate heat effectively and operate within acceptable power budgets.

**Timing closure and signal integrity analysis** to verify that all signals arrive at their destinations within required time windows, critical for multi-gigahertz operation.

For recent architectures like Blackwell, this design phase involves creating specifications for GPUs with over 200 billion transistors—requiring meticulous attention to detail and extensive simulation to achieve first-silicon success.

### Tape-Out: Transition to Manufacturing

Once the design has been thoroughly tested and verified through simulation, engineers perform a critical milestone called **tape-out**. This process involves:

**CAD file generation**: Converting the verified design into a set of computer-aided design (CAD) files that specify the exact dimensions, materials, and structures of the chip.

**Design rule checking (DRC)**: Automated verification that the design adheres to all manufacturing constraints and design rules specified by the foundry.

**Layout and photomask generation**: Creating the precise photomasks that will be used in photolithography—one mask for each of the dozens or hundreds of layers in the final chip.

**Handoff to foundry**: Delivering the complete set of electronic files and specifications to the semiconductor manufacturing facility. In NVIDIA's case, this is primarily TSMC, which has foundries in Taiwan and, as of 2025, in Arizona.

This transition marks the end of the design phase and the beginning of actual physical manufacturing.

## Phase 2: Semiconductor Fabrication at TSMC

### Wafer Preparation

The fabrication process begins with silicon wafers. TSMC sources ultra-pure silicon (99.99% purity) and processes it into wafers that are:

**Sliced from ingots**: Long cylindrical bars of pure silicon are sliced into thin wafers approximately 300 mm (12 inches) in diameter for advanced logic chips.

**Polished to extreme smoothness**: The wafer surfaces are mechanically and chemically polished to achieve atomic-level flatness, required for subsequent processing steps.

**Prepared with initial materials**: Thin films of conducting, insulating, or semiconducting materials are deposited on the wafer to serve as the foundation for the first circuit patterns.

### Iterative Layer-by-Layer Construction

The core of semiconductor fabrication involves building the chip layer by layer, with modern advanced nodes containing over 100 precisely aligned layers. Each cycle through the layers repeats a sequence of critical process steps:

#### 1. Deposition

Materials are deposited onto the wafer surface using various techniques:

**Physical Vapor Deposition (PVD)**: Metals and other materials are vaporized and deposited atom-by-atom onto the wafer surface.

**Chemical Vapor Deposition (CVD)**: Precursor chemicals are decomposed or react to deposit thin films of specific materials.

**Atomic Layer Deposition (ALD)**: Extremely thin films (down to a few atoms thick) are deposited with precise thickness control, essential for advanced nodes.

These deposited layers form the conducting paths, insulators, and other structural elements of the circuit.

#### 2. Photolithography: The Critical Patterning Step

Photolithography is arguably the most critical step in semiconductor manufacturing, as it determines how small the transistors can be. The process works as follows:

**Photoresist coating**: A light-sensitive organic polymer (photoresist) is spun onto the wafer at high speeds, creating a uniform layer a few hundred nanometers thick.

**Exposure**: The wafer is exposed to ultraviolet (UV) or extreme ultraviolet (EUV) light through a photomask—a specially prepared template containing the desired circuit pattern. For the most advanced nodes, TSMC uses EUV lithography with a wavelength of just 13.5 nanometers, allowing features to be printed thousands of times smaller than a grain of sand.

**Development**: After exposure, the photoresist is developed (dissolved selectively), removing either the exposed or unexposed areas depending on the type of resist. This creates a polymer stencil that matches the circuit pattern.

**Transfer**: The photoresist pattern serves as a mask for subsequent etching or deposition steps, transferring the pattern into the underlying material.

For NVIDIA's most advanced chips like Blackwell, manufactured on TSMC's 4-nanometer-class node, photolithography must print features with dimensions comparable to a few dozen atoms, representing the pinnacle of human manufacturing capability.

#### 3. Etching

Etching removes material from the wafer, creating the three-dimensional structures of the circuit:

**Reactive Ion Etching (RIE)**: Uses chemically reactive plasma to etch patterns into the silicon with extreme precision. The plasma is created by applying high-frequency electromagnetic energy to a gas, causing it to become ionized and chemically reactive.

**Dry etching**: Uses gases or plasmas rather than liquid chemicals, offering superior precision and control over wet etching methods and creating the high-aspect-ratio features required for advanced nodes.

**Selective etching**: Modern processes can etch some materials while leaving others intact, crucial for creating the complex three-dimensional structures in modern chips.

#### 4. Ion Implantation

To create transistors and other semiconductor structures, NVIDIA's designs require controlled doping—the addition of specific impurities to alter electrical properties:

**Ion implantation machines**: Bombard the silicon wafer with ions of dopant elements (phosphorus, boron, arsenic) at high energies (typically tens of keV to hundreds of keV), driving them into the silicon to precise depths.

**Annealing**: After implantation, the wafer is heated to activate the implanted ions and repair crystal damage caused by the bombardment.

This process is performed hundreds of times during manufacturing to create the precise regions of different conductivity that form the transistors and other circuit elements.

#### 5. Chemical Mechanical Planarization (CMP)

After material is added or removed, the wafer surface may become rough and uneven:

**CMP polishing**: The wafer is polished using a combination of chemical reactions and mechanical abrasion, removing high spots and achieving a smooth, flat surface ready for the next layer.

**Precision control**: CMP must be controlled to within nanometer tolerances to ensure subsequent layers align properly.

This step is critical for enabling the stacking of over 100 layers, as any non-uniformity would compound and eventually prevent proper alignment of upper layers.

### Extreme Precision and Quality Control

Throughout the fabrication process, precision is maintained at extraordinary levels:

**Nanometer-scale features**: Modern NVIDIA chips contain transistors measured in nanometers (billionths of a meter), with features smaller than the wavelength of visible light, requiring advanced lithography techniques.

**Layer alignment**: Each layer must be aligned to previous layers with accuracy better than 10 nanometers despite the wafer surface potentially moving due to thermal expansion and vibration.

**Process monitoring**: Advanced metrology tools continuously monitor the process, measuring film thickness, layer alignment, pattern dimensions, and other critical parameters in real-time. Deviations trigger process corrections before defects can accumulate.

**Defect detection**: AI-driven inspection systems using ultra-high-resolution imaging scan wafers for potential defects, with automated systems analyzing images and correcting problems before they propagate to other dies on the wafer.

**Cleanroom environment**: TSMC's manufacturing facilities are among the cleanest human-made environments, with strict controls on dust particles, temperature, humidity, and vibration. Even a single speck of dust can derail production of advanced chips.

### Fab Location and Capacity

NVIDIA has historically relied on TSMC's fabrication plants in Taiwan, where decades of expertise and infrastructure enable the most advanced manufacturing. However, as of late 2025, this has changed:

**TSMC Arizona Fab (Fab 21)**: In October 2025, NVIDIA announced that its flagship Blackwell chips have begun volume production at TSMC's Fab 21 near Phoenix, Arizona. This facility manufactures chips using TSMC's 4-nanometer-class process node, representing the first time a leading-edge NVIDIA GPU has been manufactured in the United States. This strategic move helps NVIDIA diversify its manufacturing footprint away from Taiwan, mitigating geopolitical risks while strengthening the US semiconductor supply chain.

## Phase 3: Wafer Testing and Sorting

### In-Wafer Testing

Before chips can be separated from the wafer, they undergo rigorous testing while still on the wafer:

**Functional testing**: Each die (individual chip) is tested for basic functionality—ensuring it can execute instructions and perform calculations correctly.

**Electrical parametric testing**: Voltage, current, clock speeds, and power consumption are measured to verify they meet specifications.

**Heat tolerance testing**: Dies are tested at various temperatures and voltages to understand their thermal characteristics and performance margins.

**AI-driven defect detection**: Advanced inspection systems use high-resolution imaging and AI algorithms to identify defects at the wafer level before further processing.

### Binning and Yield Management

Not all chips meet the highest performance specifications:

**Performance binning**: NVIDIA tests and sorts chips into different performance categories based on measured characteristics. Chips that operate at lower clock speeds or consume slightly more power are classified separately from premium bins.

**Yield optimization**: NVIDIA's strategy is to maximize overall yield by finding productive uses for almost every functional chip. Rather than discarding chips that fall slightly short of premium specifications, the company sorts them into different product lines:
- Chips meeting the highest specifications become flagship products (like H100 or B200)
- Chips with slightly lower performance become mid-range products
- Even partially functional chips are evaluated for alternative applications

This yield optimization strategy ensures that the enormous cost of semiconductor fabrication is amortized across as many functional products as possible.

## Phase 4: Chip Packaging and Assembly

### Die Separation

Once testing is complete, individual dies are separated from the wafer:

**Wafer dicing**: A specialized wafer saw cuts the wafer into individual dies, each containing a complete GPU chip.

**Individual die inspection**: Each separated die is inspected to verify the cutting process did not damage the circuitry.

### Advanced Chip Packaging: CoWoS Technology

For modern high-performance GPUs like Hopper and Blackwell, the packaging process is extremely complex:

**Chip-on-Wafer-on-Substrate (CoWoS)**: NVIDIA uses TSMC's proprietary CoWoS technology to package its most advanced GPUs. This represents one of the most sophisticated packaging technologies in semiconductor manufacturing:

- **Multiple dies on a single package**: For chips like the Blackwell B300, two separate compute dies (each manufactured at TSMC's fab) are packaged together with additional components into a single GPU unit.
- **High-bandwidth memory integration**: High-bandwidth memory (HBM) modules are stacked alongside the compute dies, connected with through-silicon vias (TSVs)—tiny vertical electrical connections that allow extremely high-speed communication between components.
- **Extreme interconnect density**: The packaging must accommodate thousands of electrical connections between components at nanometer-scale pitches.

### High-Bandwidth Memory (HBM) Integration

Modern GPUs require incredibly fast access to large amounts of memory:

**HBM memory modules**: NVIDIA's flagship GPUs use stacked High-Bandwidth Memory (HBM3 or HBM3e for Blackwell). These memory modules contain multiple layers of DRAM stacked vertically.

**Memory bandwidth**: HBM technology enables bandwidth exceeding 800 GB/s between the GPU and memory—orders of magnitude faster than conventional memory interfaces.

**Memory capacity**: Modern GPUs can include hundreds of gigabytes of HBM (up to 288 GB for Blackwell), enabling processing of enormous datasets.

### Advanced Packaging Facilities

While the actual chip manufacturing (wafer fabrication) has shifted somewhat to US facilities like TSMC Arizona, advanced packaging remains a critical bottleneck:

**TSMC packaging facilities in Taiwan**: Currently, NVIDIA's most advanced Blackwell GPUs undergo final CoWoS packaging at TSMC facilities in Taiwan, which have decades of expertise in this specialized technology.

**Future US packaging capacity**: Companies like Amkor Technology and SPIL are building advanced packaging facilities in the United States to support NVIDIA's long-term strategy of relocating more of the supply chain domestically. These facilities are expected to be operational by 2027-2028.

## Phase 5: Printed Circuit Board Assembly

### PCB Manufacturing

For consumer graphics cards and complete GPU systems, the packaged chip must be integrated onto a printed circuit board:

**Multi-layer circuit boards**: Modern GPU circuit boards contain 12 or more layers of copper traces, each layer serving different electrical purposes (power distribution, signal routing, ground planes).

**Board fabrication**: Each layer requires precise manufacturing, with production taking days for a single board before any components are mounted.

### Component Placement and Soldering

Once the PCB is complete, thousands of electronic components are attached:

**Surface Mount Technology (SMT) machines**: Sophisticated automation places components—memory chips, voltage regulators, capacitors, and thousands of passive components—onto the board. Modern machines can place thousands of components per hour with sub-millimeter accuracy.

**Thermal paste application**: Before the GPU die itself is mounted, microscopically thin thermal paste is applied to fill atomic-scale gaps between the chip and heat dissipation components. This critical step ensures efficient heat transfer despite the surface irregularities at the nanometer scale.

**Reflow soldering**: The entire board is heated in a specialized oven to melt solder paste, creating permanent electrical connections between components and the PCB. Temperature profiles must be carefully controlled to avoid damaging components while ensuring reliable solder joints.

**Quality inspection**: After soldering, boards undergo automated visual inspection using high-resolution cameras and AI analysis to detect solder bridges, missing connections, or misaligned components.

### Heat Management Assembly

Modern high-performance GPUs generate significant heat:

**Heat sink design**: Aluminum or copper heat sinks with numerous fins are mechanically or thermally bonded to the chip to dissipate heat.

**Fan integration**: For consumer cards, cooling fans are integrated into the shroud. For data center GPUs, advanced liquid cooling systems may be used instead.

**Thermal testing**: Each assembled card undergoes thermal testing to verify proper heat dissipation.

## Phase 6: System-Level Assembly and Testing

### Supercomputer Manufacturing

For NVIDIA's AI supercomputers (the DGX series and newer systems), assembly extends beyond individual cards:

**Rack assembly**: Multiple GPUs, networking equipment, power supplies, and interconnect hardware are assembled into standard data center racks.

**Complexity at scale**: A fully assembled NVIDIA AI supercomputer might contain:
- 8 or more GPUs per node
- Hundreds of GPUs in a complete system
- 130 trillion transistors across all chips
- 1.2 million individual components
- 2 miles of copper cabling
- Sophisticated liquid cooling systems

### Extreme Stress Testing

Before any GPU reaches a customer, it undergoes extreme validation:

**Extended burn-in testing**: Each GPU is subjected to hundreds of hours of continuous operation at maximum load, stressing all execution units, memory systems, and power delivery circuits.

**Thermal cycling**: Temperature is cycled between extremes to ensure reliability across operating conditions.

**Performance validation**: Custom test software exercises all GPU capabilities:
- Parallel computation workloads
- Memory bandwidth utilization
- AI inference and training scenarios
- Graphics rendering tasks
- Physics simulations

**Defect escape prevention**: These rigorous tests identify any chips that slipped through earlier testing, preventing failures in the field.

### Testing Facilities

NVIDIA partners with specialized testing companies like KYEC (King Yuan Electronics) that maintain sophisticated testing facilities:

**Advanced Test Equipment (ATE)**: High-speed automated test equipment measures electrical characteristics, executes test patterns, and identifies any performance issues.

**Real-world scenario simulation**: Tests simulate actual GPU usage patterns—gaming, AI training, scientific computing—to verify performance under realistic conditions.

## Phase 7: Manufacturing Innovation and Optimization

### AI-Driven Manufacturing

NVIDIA leverages its own GPU technology to optimize manufacturing:

**Digital twins**: NVIDIA uses NVIDIA Omniverse to create digital twins of manufacturing facilities. These virtual replicas allow engineers to simulate manufacturing processes, optimize workflows, and train robots before implementing changes on actual production equipment.

**Robot automation**: NVIDIA is deploying Isaac GR00T (General Robotic Operating System) robots in its US manufacturing facilities to automate assembly and testing processes, reducing labor costs and improving consistency.

**Predictive analytics**: Machine learning models analyze manufacturing data to predict equipment failures, optimize process parameters, and improve yield before problems occur.

### Yield Management

Semiconductor manufacturing is inherently yield-limited:

**Yield optimization as a core strategy**: NVIDIA continuously works to improve manufacturing yield—the percentage of chips that meet specifications. Even 1-2% improvements in yield can represent millions of dollars in value given the scale of production.

**Root cause analysis**: When defects are detected, sophisticated analysis identifies the root cause, enabling process corrections before the next batch.

**Continuous improvement**: Manufacturing processes are continuously refined, with data from millions of chips analyzed to identify optimization opportunities.

## Supply Chain and Manufacturing Partners

### Design Phase Partners
- **NVIDIA**: Architecture design, EDA, verification

### Fabrication Partners
- **TSMC (Taiwan and Arizona)**: Wafer fabrication
- **Samsung**: Historical fabrication for earlier generation GPUs

### Packaging and Assembly Partners
- **TSMC**: Advanced CoWoS packaging (current, Taiwan-based)
- **Amkor Technology**: Packaging, test, assembly (expanding to US)
- **SPIL (Siliconware)**: Packaging and testing
- **Foxconn**: System assembly (Houston, Texas)
- **Wistron**: System assembly (Dallas, Texas)

### Final Assembly and Test
- **Foxconn, Wistron, Quanta Computer**: Global assembly partners

## Geographic Distribution and Recent Shifts

### Traditionally Taiwan-Centric

For decades, NVIDIA's GPU manufacturing was almost entirely concentrated in Taiwan, with TSMC providing wafer fabrication and advanced packaging.

### Recent US Manufacturing Expansion

Beginning in 2025, NVIDIA is executing a major manufacturing shift:

**Blackwell production in Arizona**: October 2025 marked the beginning of volume production of Blackwell chips at TSMC's Arizona facility (Fab 21), representing the first time a flagship NVIDIA AI GPU is manufactured in the United States.

**Supercomputer manufacturing in Texas**: NVIDIA is building manufacturing facilities in Texas (Houston with Foxconn, Dallas with Wistron) specifically for assembling and testing complete AI supercomputer systems. These facilities are expected to reach full mass production capacity within 12-15 months.

**Packaging capacity development**: While advanced packaging is still done in Taiwan, NVIDIA is working with partners like Amkor to develop US-based advanced packaging capacity.

### Strategic Rationale

This manufacturing shift serves multiple purposes:

**Supply chain resilience**: Reducing dependence on Taiwan mitigates geopolitical risks, particularly given tensions around Taiwan's future.

**Tariff avoidance**: US manufacturing allows NVIDIA to avoid potential tariffs on Taiwan-made goods.

**Capacity expansion**: The shift provides additional manufacturing capacity to meet exploding AI demand.

**Workforce development**: Building domestic manufacturing supports job creation in the US semiconductor industry.

**Political alignment**: The shift aligns with US government industrial policy under the CHIPS Act, supporting domestic semiconductor manufacturing.

## Remarkable Statistics of Modern GPU Manufacturing

The scale and complexity of modern GPU manufacturing is staggering:

- **Transistor count**: Modern Blackwell GPUs contain over 200 billion transistors on the compute dies alone, plus billions more in memory components.
- **Feature size**: The smallest features on these chips are just a few nanometers across—about 1/25,000th the width of a human hair.
- **Process complexity**: Manufacturing involves over 1,000 individual process steps spread across 100+ layers.
- **Manufacturing time**: From bare silicon wafer to completed chip requires approximately three months.
- **Cost**: The tape-out and manufacturing setup costs for advanced chips can reach tens to hundreds of millions of dollars.
- **Yield challenges**: Despite near-perfect individual process steps, the enormous number of layers and transistors means that achieving high manufacturing yields is a constant challenge requiring continuous optimization.
- **Precision requirements**: Layer-to-layer alignment must be maintained to within nanometers across an entire 300 mm wafer despite thermal expansion and vibration.
- **Component density**: A completed GPU system might contain 1.2 million individual components.
- **Cooling requirements**: High-end GPUs can dissipate 700 watts to 1 kilowatt of power, requiring sophisticated thermal management.

## Conclusion

NVIDIA's GPU manufacturing represents the confluence of decades of semiconductor industry expertise, cutting-edge physics, and extraordinary precision engineering. The process transforms abstract designs into physical silicon containing hundreds of billions of transistors, requiring collaboration across multiple countries and dozens of specialized companies. 

Recent developments show NVIDIA shifting toward more geographically distributed manufacturing, with significant expansion of US manufacturing capacity while maintaining reliance on Taiwan's expertise for advanced packaging and some fabrication. This evolution reflects both the company's desire for supply chain resilience and the broader trend of reshoring advanced semiconductor manufacturing to the United States.

The remarkable fact is not just that GPUs can be manufactured at all at these scales and complexities, but that they can be produced in volume at competitive costs, enabling the AI revolution that is reshaping industries and society. Every GPU represents an extraordinary achievement in human engineering and manufacturing excellence.