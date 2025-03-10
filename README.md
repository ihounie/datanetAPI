# My Documentation
I have modified dataNet API class to download and extract the dataset whenever initialised with a path where no data is found.
I had to add `extract.py` in order to extract the nested tar files.
`download_and_extract.py` simply initialises the class with `./dataset` as path.

## To do
* add CLI (argparse) to download_and_extract in order to customise the dataset path.

# DataNet API Documentation

#### Contact mailing list: kdn-users@knowledgedefinednetworking.org
(You first need to subscribe at: https://mail.knowledgedefinednetworking.org/cgi-bin/mailman/listinfo/kdn-users).

## 1 Introduction
This Python API is intended to provide users with a simple and intuitive way to access the information contained in the associated datasets. Following a user-oriented approach, the API aims to abstract users from the internal details of our datasets, thus making much easier extracting the information.

## 2 How does it work?

Beyond the complex structure of the datasets, which include many files distributed in different directories, this API provides sequentially samples (one at a time) structured in a user-friendly way. 

Two main components can be distinguished to understand how to use this API: (i) the iterator, and (ii) a sample instance. The iterator is in charge of reading and processing a sample from the dataset, while a sample is an object produced by the iterator that contains all the information of a sample in a well-structured manner.

## 3 How to use the API

We provide below a simple code snippet to initialize the iterator object of the API and obtain sequentially samples from the dataset:

````python
import datanetAPI
reader = datanetAPI.DatanetAPI(<pathToDataset >,<IntensityRange>, [shuffle])
it = iter(reader)
for sample in it:
  <process sample code>
````

First of all, the user needs to download and import this Python library (line 1). Then, an instance of datanetAPI can be initialized (line 2), where pathToDataset should point to the root directory of the dataset to be processed. Note that this dataset should be uncompressed in advance. IntensityRange is a Python list of integers that enables to filter only samples within a traffic intensity range. Thus, the user can specify: (i) a single value, if a specific intensity is desired, or (ii) a list with two values, that will be considered respectively as the lower and upper bounds of a range of intensities desired (e.g., IntensityRange = [800 1200] will return only the samples with traffic intensity from 800 to 1200). In a typical case, IntensityRange should be an empty list (i.e., IntensityRange = [ ]), then the iterator object will return all the samples of the dataset. Finally, shuffle is a boolean that by default is 'false' and indicates if the sample files should be shuffled before being processed. Afterwards, the iterator object can be created (line 3).
Once the iterator object is created, samples can be sequentially extracted using a “for” loop (line 4). 

Alternatively, the next(it) method can be used to read only the next sample. This enables, for instance, read only “n” samples from the dataset using:

````python
for i in range(n):
    sample = next(it)
````
The DatanetAPI object also provides the following methods:
* reader.get_available_files(): Return a list of all the dataset files located in the <pathToDataset> directory which is specified in the initialization of the object and its subdirectories. Each element of the list is a tuple containing the path of the file and the file itself.
* reader.set_files_to_process(tuple_list): Specify a sublist of files to be processed by the iterator. The files should be a subset of the files obtained with get_available_files(). This function should always be used before creating the iterator.

The next section describes in detail all the information that a sample object contains and some methods to extract it.

## 4 Structure of a Sample object

This section describes how the data is structured within a sample object.

Every sample is a container including information about: (i) a network topology, (ii) parameters used to generate the traffic in our simulation tool, (iii) a routing configuration, (iv) some measurements (delay, jitter and loss) measured in our simulator resulting from the network configuration (i.e., topology + traffic distribution + routing) and (v) link performance metrics. All this information is provided for every source-destination pair of the network. Note that we consider only a path connecting every source-destination (src-dst) pair, however more than a src-dst flow can traverse the same path and performance measurements can be individually obtained for each flow. Also, note that our simulator implements a method that stops the simulation when it detects that the network reaches a stationary state. Consequently, the simulation time to generate each sample is different. This is why we provide measurements such as generated or dropped packets as numbers relative to time units (e.g., packets/time unit)


More in detail, every sample instance comprises the following attributes:
* *global_packets*: Number of packets transmitted in the network per time unit (packets/time unit).
* *global_losses*: Packets lost in the network per time unit (packets/time unit).
* *global_delay*: Average per-packet delay over all the packets transmitted in the network (time units).
* *maxAvgLambda*: This variable is used in our simulator to define the overall traffic intensity of the network scenario. Particularly, this is the maximum average traffic rate (bits/time unit) that a path can generate in the simulation scenario. Then, the average traffic rate of each src-dst path (lambda) is computed as 'maxAvgLambda' multiplied by a random value between 0 a 1. Note that, this traffic rate may be split into several flows sending traffic over the same src-dst path.
* *performance_matrix*: Matrix with aggregate src-dst and flow-level performance meaurements (delay, jitter and loss) measured on each src-dst pair (see more details below). 
* *traffic_matrix*: Matrix with the time and size distributions used to generate traffic for each src-dst pair (see more details below). 
* *routing_matrix*: Matrix with the paths to connect every src-dst pair (see more details below).
* *topology_object*: It uses a Graph object from the Networkx library including topology-related information at the node and link-level (see more details below).
* *links_performance*: list of dictionaries with the performance metrics associated with each link. (see more details below). Not all datasets contain this information. In that case, this object is None

**performance_matrix**: This is a matrix that indexes performance measurements at the level of src-dst pairs. Particularly, it considers that more than one flow can be exchanged on each src-dst pair. Hence, it provides performance measurements at two levels of granularity: (i) for all aggregate flows on each src-dst pair, and (ii) for every flow individually. Every element of this matrix (i.e., performance_matrix[src,dst]) contains a dictionary with the following keys: 
* ‘AggInfo’: dictionary with performance measurements for all aggregate flows between a specific [src,dst] pair. 
  * ‘PktsDrop’: packets dropped per time unit over the path [src,dst]. (packets/time unit)
  * ‘AvgDelay’: average per-packet delay over the packets transmitted on path [src,dst] (time units)
  * ‘AvgLnDelay’: average of the neperian logarithm of the per-packet delay over the all packets transmitted on path [src, dst]. This is “avg(ln(packet_delay))”
  * ‘p10’, ‘p20’, ‘p50’, ‘p80’, ‘p90’: percentiles (10, 20, 50, 80, and 90) of the per-packet delay distribution on path [src,dst]. (time units)
  * ‘Jitter’: Variance of the per-packet delay over the packets transmitted on path [src,dst]. This is var(packet_delay)
* ‘Flows’: List of dictionaries with performance measurements for each flow between node i and node j. Flows on each src-dst pair are indexed by a numerical ID (e.g., performance_matrix[0,1][‘Flows’][‘0’]). Note that all the flows of a src-dst pair follow the same path but may have different traffic distributions, thereby performance may vary between them. Each flow contains the following keys:
  * ‘PktsDrop’: packets dropped per time unit on the flow. (packets/time unit)
  * ‘AvgDelay’: average per-packet delay on the flow. (time units) 
  * ‘AvgLnDelay’: average of the neperian logarithm of the per-packet delay over the all packets transmitted on the flow. i.e., “avg(ln(packet_delay))”
  * ‘p10’, ‘p20’, ‘p50’, ‘p80’, ‘p90’: percentiles (10, 20, 50, 80, and 90) of the per-packet delay distribution on the flow. (time units)
  * ‘Jitter’: variance of the per-packet delay (i.e., jitter) on the flow. i.e., var(packet_delay)

Thus, assuming perf is the performance_matrix of a sample, we may access to the information as follows:
* *perf[src,dst]*: dictionary with the performance measurements for the communication between node src and node dst. 
* *perf[src,dst][′AggInfo′]*: dictionary with performance metrics on aggregate traffic between node src and node dst. Use *perf[src,dst][′AggInfo′][′\<nameparam\>′]*, where \<nameparam\> can be replaced by any of the keys described previously to obtain a specific performance metric (e.g., perf[0,1][′AggInfo′][′AvgDelay′]).
* *perf[src,dst][′Flows′]*: flow-level performance metrics on traffic between node src and node dst. Use *perf[src,dst][′ Flows′][′\<numflow\>′]* and replace \<numflow\> by the number ID of the desired flow to obtain its information. Extend to *perf[src,dst][′Flows′][′\<numflow\>′][′\<nameparam\>′]* and replace \<nameparam\> by any of the keys described previously to obtain a specific performance measurement for a specific flow (e.g., perf[0,1][′Flows′][′0′][′ PktsDrop′]).


**traffic_matrix:** This matrix indexes traffic-related information at the level of src-dst pairs. Similarly to performance_matrix, it provides traffic information at two levels of granularity: (i) for all aggregate flows on each src-dst pair, and (ii) for every flow individually. Every element of this matrix (i.e., traffic_matrix[src,dst]) contains a dictionary with the following keys:
* ‘AggInfo’: dictionary with traffic measurements for all aggregate flows between a specific [src,dst] pair. 
  * ‘AvgBw’: average bandwidth from node src to node dst (bits/time unit).
  * ‘PktsGen’: packets generated from node src to node dst per time unit (packets/time unit).
* ‘Flows’: List of dictionaries with flow-level traffic information for each flow between node src and node dst. It includes the traffic measurements for each flow and the parameters used to generate the traffic flow in our network simulator (see the different inter-packet arrival time and packet size distributions considered, and a list of parameters used in each of these distributions in Sections 4.1 and 4.2).
  * ‘TimeDis’: inter-packet arrival time distribution used to generate the traffic of the flow (see possible time distributions in Section 4.1).
  * ‘TimeDistParams’: dictionary with the parameters of the specific inter-packet arrival time distribution (see the parameters of each time distribution in Section 4.1). 
    * ‘EqLambda’: average bitrate per time unit (bits/time unit). 
    * ‘AvgPktsLambda’: average number of packets of average size generated per time unit (packets/time unit).
    * ‘MinPktLambda’: minimum number of packets generated per time unit (packets/time unit). 
    * ‘MaxPktLambda’: maximum number of packets generated per time unit (packets/time unit). 
    * ‘StdDev’: Standard deviation of the interarrival time (used in the normal distribution). 
    * ‘PktsLambdaOn’: Average packets per time unit generated during the ON period (packets/time unit).
    * ‘AvgTOff’: Average duration of the OFF period. The duration of every OFF period is modeled with an exponential distribution of average = ‘AvgTOff’. (time units)
    * ‘AvgTOn’: Average duration of the ON period. The duration of every ON period is modeled with an exponential distribution of average = ‘AvgTOn’. (time units)
    * ‘ExpMaxFactor’: Factor used to define an upper bound for exponential distributions. The upper bound is defined as: ‘ExpMaxFactor’* lambda of the exponentil
    * ‘BurstGenLambda’: Burst generation rate of the flow (bursts/time unit). 
    * ‘Bitrate’: Bitrate during a burst: (bits/time unit). 
    * ‘ParetoMinSize’: Minimum number of bits in the burst (bits). 
    * ‘ParetoMaxSize’: Maximum number of bits in the burst (bits).
    * ‘ParetoAlfa’: Shape parameter (α) used in the Pareto distribution. 
  * ‘SizeDist’: packet size distribution used for the flow (see possible packet size distributions in Section 4.2).
  * ‘SizeDistParams’: dictionary with the parameters of the specific size distribution (see the parameters of each packet size distribution in Section 4.2). 
    * ‘AvgPktSize’: Average packet size (bits). 
    * ‘MinSize’: Minimum packet size (bits). 
    * ‘MaxSize’: Maximum packet size (bits). 
    * ‘PktSize1’: First packet size option (bits). 
    * ‘PktSize2’: Second packet size option (bits).
    * ‘NumCandidates’: Number of different packets size considered. 
    * ‘Size_i’: Size of the candidate packet i (bits).
    * ‘Prob_i’: Probability to select candidate packet i (bits). 
  * ‘AvgBw’: average bandwidth for this flow (bits/time unit).
  * ‘PktsGen’: packets generated by this flow per time unit (packets/time unit).
  * ‘ToS’: Type of Service associated to this flow defined as an integer. 

Data within traffic_matrix is structured in a similar way as in performance_matrix. The information is indexed by every src-dst pair. However, in this case the possible parameters of the inter-packet arrival time and packet size distributions depend on the types of distribution used. For instance, in case of an exponential inter-packet time distribution, the parameters of the first flow can be accessed using the following lines of code:

```
traffic_matrix[src,dst][′Flows′][′0′][‘TimeDistParams’][′EqLambda’]
traffic_matrix[src,dst][′Flows′][′0′][‘TimeDistParams’][′AvgPktsLambda’]
traffic_matrix[src,dst][′Flows′][′0′][‘TimeDistParams’][′ExpMaxFactor’]
```

Note: If the dataset only has one flow per path, then traffic and performance measurements over the aggregate traffic on a src-dst pair are the same as flow-level measurements on the only flow in that src-dst pair. This applies to performance_matrix and traffic_matrix. For instance:
performance _matrix[0,1][′AggInfo′][′AvgDelay′]) = performance _matrix[0,1][′Flows′][′0′][′AvgDelay′]). In the case of traffic_matrix, using information at the flow-level is recommended (e.g., traffic_matrix[0,1][′Flows′][′0′]), since it includes additional information not considered at the level of aggregate traffic.

**routing_matrix**: This matrix describes the routing configuration. Particularly, it includes all the paths connecting every src-dst pair. Assuming route is a routing_matrix, “route[src,dst]” returns a list  describing the path from node src to node dst. Particularly, this list includes the IDs of the nodes that the path traverses. Note that all the flows of a src-dst pair follow the same path. 

**topology_object**: This is a Graph object form the Networkx library that provides information about the network topology. Particularly, this object encodes information on nodes and links (i.e., edges). Assuming g is a graph object of a sample instance, we can access the data as follows:
* g.nodes: Returns a list with all the node IDs. 
* g.nodes[id]: Returns a dictionary with all the information parameters of the selected node (see more details of the node parameters Section 4.3).
* g.edges: Returns a list of tuples describing the topology edges. Each tuple is described as (src node ID, dst node ID, link ID). The link ID is always ‘0’ as only one link for the same src-dst pair is supported at this moment.
* g[src][dst][0]: Dictionary with the information parameters of the (directed) link between node src and node dst (see more details of the link parameters in Section 4.4).

**links_performance**: This object is structured as a list of dictionaries of dictionaries object and contains the performance metrics of the links. The outer list contains a dictionary of dictionaries for each node. The first dictionary contains the list of adjacents nodes and the last dictionary contain the performance metrics of the link. The performance dictionary contains the following keys:
* ‘utilization’: Tan per one of the average utilization of the link.
* ‘loses’: Tan per one of the average packets lost in the link.

Thus, assuming lperf is the links performance object of a sample, we may access the information as follows:
* lperf[src][dst]: dictionary with the performance measurements of the link [src][dst]. If the dst node is not adjacent to src node. A KeyError exception will be produced.
* lperf[src][dst][<nameparam>]: Read the <nameparam> parameter of the link.

### 4.1 Parameters of time distributions
Our simulator considers the following inter-packet arrival time distributions for different flows in the network:

* TimeDist.EXPONENTIAL_T: EqLambda, AvgPktsLambda, ExpMaxFactor 
* TimeDist.DETERMINISTIC_T: EqLambda, AvgPktsLambda 
* TimeDist.UNIFORM_T: EqLambda, MinPktLambda, MaxPktLambda
* TimeDist.NORMAL_T: EqLambda, AvgPktsLambda, StdDev
* TimeDist.ONOFF_T: EqLambda, PktsLambdaOn, AvgTOff, AvgTOn, ExpMaxFactor
* TimeDist.PPBP_T: EqLambda, BurstGenLambda, Bitrate, ParetoMinSize, ParetoMaxSize, ParetoAlfa, ExpMaxFactor

### 4.2 Parameters of packet size distributions

Our simulator considers the following packet size distributions for different flows generated in the network:

* SizeDist.DETERMINISTIC_S: AvgPktSize 
* SizeDist.UNIFORM_S: AvgPktSize, MinSize, MaxSize 
* SizeDist.BINOMIAL_S: AvgPktSize, PktSize1, PktSize2 
* SizeDist.GENERIC_S: AvgPktSize, NumCandidates, Size_i, Prob_i

### 4.3 List of node parameters

All the possible node parameters are listed below:

* ‘levelsQoS’: Number of supported QoS classes
* ‘queueSizes’: queue sizes (in number of packets) for each output queue of the node. Values are separated by commas. Each value is associated with a QoS queue.
* ‘schedulingPolicy’: Policy used to serve the QoS queues. It may be one of the following ones: ‘FIFO’ (First-In, First-Out), ‘SP’ (Strict Priority), ‘WFQ’ (Weighted Fair Queuing), ‘DRR’ (Deficit Round Robin). If not specified, a ‘FIFO’ policy is considered by default. 
* ‘schedulingWeights’: List of weights separated by commas associated to each QoS queue. Used only in the WFQ and DRR scheduling policies.

### 4.4 List of link parameters

All the possible node parameters are listed below:

* ‘port’: Port number of the source node that links with destination node.
* ‘bandwidth’: Link bandwidth (bits/time unit) 
* ‘weight’: Not used yet

## 5 API methods to read information from a Sample object

The API includes methods to obtain more easily some information from a sample object. This includes different matrices and dictionaries described above. Thus, the user can use the following methods (hereafter, we assume that s is a sample object obtained from the iterator):

* *s.get_global_packets()*: Returns the number of packets transmitted in the network per time unit of the sample.
* *s.get_global_losses()*: Returns the number of packets dropped in the network per time unit of the sample.
* *s.get_global_delay()*: Returns the average per-packet delay over all the packets transmitted in the network in time units of the sample.
* *s.get_maxAvgLambda()*: Returns the maximum average lambda selected to generate the traffic matrix of the sample.
* *s.get_performance_matrix()*: Returns the performance_matrix. Assuming this matrix is denoted by m, performance measurements of a specific src-dst pair can be accessed using m[src,dst]. See more details about the performance_matrix in the previous section.
* *s.get_srcdst_performance(src,dst)*: Directly returns a dictionary with the performance measurements (e.g., delay, jitter, loss) stored in performance_matrix for a particular src-dst pair. See more details about the performance_matrix in the previous section.
* *s.get_traffic_matrix()*: Returns the traffic_matrix. Assuming this matrix is denoted by m,  the information that traffic_matrix stores for a specific src-dst pair can be accessed using m[src,dst] . See more details about the traffic_matrix in the previous section.
* s.get_srcdst_traffic(src,dst): Directly returns a dictionary with information that the traffic_matrix stores for a particular src-dst pair. See more details about the traffic_matrix in the previous section.
* s.get_routing_matrix(): Returns the routing_matrix. Assuming this matrix is denoted by m, we can retrieve the path that connects the node src with node dst using m[src,dst]. See more details about the routing_matrix in the previous section.
* s.get_srcdst_routing(src,dst): Returns a list with the routing path that connects node src with node dst. 
* s.get_topology_object(): Returns a Networkx Graph object with nodes and links parameters 
* s.get_network_size(): Returns the number of nodes in the topology. 
* s.get_srcdst_link_bandwidth(src,dst): Returns the bandwidth in bits/time unit of the link between node src and node dst in case there is a link between both nodes, otherwise it returns -1.
* s.get_node_properties(node_id): Returns a dictionary with the parameters of the node identified by node_id if it exists. Otherwise it returns ‘None’. 
* s.get_link_properties(src,dst): Returns a dictionary with the parameters of the link between node src and node dst if they are connected by a link. Otherwise it returns ‘None’.
* s.get_links_performance(): Returns the links performance object. Assuming the object is denoted by lp, the performance metrics stored for a specific link can be accessed using lp[src][dst] . See more details about the link_performance in the previous section.
* s.get_srcdst_link_performance(src,dst): Directly returns a dictionary with the link performance metrics of the src-dst link or None if the link doesn’t exist. See more details about the link_performance in the previous section.

## Credits
This project would not have been possible without the contribution of:
* [Arnau Badia](https://github.com/arnaubadia) - Barcelona Neural Networking center, Universitat Politècnica de Catalunya
* [Albert López](https://github.com/albert-lopez) - Barcelona Neural Networking center, Universitat Politècnica de Catalunya
* [Jose Suárez-Varela](https://github.com/jsuarezv) - Barcelona Neural Networking center, Universitat Politècnica de Catalunya
* Adrián Manco Sánchez - Barcelona Neural Networking center, Universitat Politècnica de Catalunya
* Víctor Sendino Garcia - Barcelona Neural Networking center, Universitat Politècnica de Catalunya
* [Pere Barlet Ros](https://github.com/pbarlet) - Barcelona Neural Networking center, Universitat Politècnica de Catalunya
* Albert Cabellos Aparicio - Barcelona Neural Networking center, Universitat Politècnica de Catalunya
