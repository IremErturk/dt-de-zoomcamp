# Stream Processing with Apache Kafka
## Intro 

Producer -> Kafka -> Consumer

Kafka is realtime pipeline, ,message broker between producer and consumers

**Kafka Broker:** Physical Machine on which Kafka Running 

**Kafka Cluster:** Multiple Kafka brokers, multiple machines working together

**Message:** (Key*, Value, Timestamp), Key does not have to be unique and will be covered a bit more with the partitions

**Logs:** Stores messages in order fashion, assigns sequece id to each message before storing it to logs (Data Segments present in your disk)

**Topic:** Abstraction of a concept, can be consider as folder such that all messages related to topic is kept there.

---

## Basic Workflow

Producer -> Kafka

1. Producer request/configure topic in Kafka .. -> Kafka alloacate physical hardware disk to store logs for the topic
2. Producer send messages .. -> Kafka writes messages to alllocated topic  storage as logs
3. Kafka send producer an acknowledgement message

Kafka -> Consumer
1. Consumer request to read from topic
2. Kafka checks the topic logs? (How to read in order, without missing or without dublicates) **
3. Kafka sends read messages to the consumer 
    - Kafka broker write internal logs/topics for storing, consumer 1 read 10 message from topic1 info (__consumer-offset)
    - What happens if multiple consumers read from one topic? Each consumer has its topic offset.
4. Consumer sends acknowledgement to the Kafka by saying I have read xth message.

---
## Consumer Groups
Kafka considers all consumers in a consumer group as one entity.
For instance C1 on consumer group receive 1-10 messages, 
all other consumers in the same group wont receive these messages.

Allows scaling horizontally within the consumer groups.

## Partitioning & Scalability(horizontal)

Partitioning can be considered to topic level and also the consumer group level. 
I found it is similiar to how Spark disributes the workload/partitioned files to different machines.

the best performance/speed achieved by having equal number for topic partitions and consumer number in the consumer group.

**How messages assigned in different partitions?** 
message(Key, Value, Timestamp), based on the key the partition of message is determined. For instance: HASH(key) % partition_number 
When you leave key null, then the messages distributed equally over the partitions in round-robin fashion.
If order is important within some group, keep in mind that the same hash(key) always go to same partition and ordered within the partition itself.
The same key goes to the same partition, therefore the messages with same key are handled with same consumer. Internal Key Table...

---
## Replication - Fault Tolerance

The messages are replicated to the other Kafka broker.(Leader, Replica)

## Configuration Terms

Topics:
- retension.ms - time that defines how long the logs stay
- cleanup.policy - [delete | compact] (compact is not real time and it works with batch jobs in background)
- partition - scalability count
- replication 

Consumer:
- offset - what has been alread read by the consumer
- consumer.group.id
-auto.offset.reset - [earliest | latest], when consumer connects for the first time to a topic (what to do with the previous messages created in topic, before consumer configured??)

Producer:
- acks: [0|1|all]
    - 0: does not wait for leader or replica broker
    - 1: waits leader to write message
    - all: waits leader and replica to write message


## Schema Registry -> Avro
Kafka also supports ProtoBuffers / Json

Avro is data serialization system as ProtoBuffer.
For Avro, schema stored seperately from record.
Therefore the file sizes are smaller compared to alternatives (similiar ideas as parquet)

---
### Kafka Streams
- Client Library for building stream application, (fault tolerant, scalable) (Alternatives: Spark Flink, Storm)
- ***Data from Kafka to Kafka (limitation no other sinks and sources than Kafka)
- Miliseconds latency
- Proide convenient DSL
- Stateful processing with KTable maintainance

---
#### Kafka Stream and State(KTable)

In Stream, we always see one message in time
In State, the state , KTable, state of a stream in particular frame

**Features**
- Aggregates:
    - Count
    - GroupBy
- Joins: 
    - KStream to KStream (always windowed)
    - KTable to KTable (never windowed)
    - KStream to KTable
    - ** KTable consider the latest state, where as KStream memorize over a time-window.
- Window:
    - Time based: fixed/timbling, sliding
    - Session based

**Global KTable**
- Act as broadcast variable..Data in all partitions in available to all instances.
- Benefits
    - More effective joins, no need to co-partition
- Drawbacks
    - Increase local storage, increase network load

---
** Both Kafka Connect and KSQL require seperate Kafka cluster
## Kafka Connect
---
## KSQL

---
## TODO: Kafka with Docker
- Zookeeper: Since version 2.8, Kafka cluster can be run without ZK
- Broker
- Kafka-Tools
- Schema-Registery
- Control-Center / enterprise