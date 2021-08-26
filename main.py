import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from time import perf_counter
from rtree import RTree
from rectangle import Rectangle
from point import Point
from entry import Entry
from pyspark import SparkConf, SparkContext


def main():
    r_seed = 1
    np.random.seed(seed=r_seed)

    rtree = RTree()
    conf = SparkConf().setMaster("local[*]").setAppName("RTreeSpark")
    sc = SparkContext(conf=conf)

    # VISUALIZATION SETTINGS
    printInConsole = False

    # CREATING POINTS RDD
    points = sc.textFile('data-sets\data100k.csv', minPartitions=8)
    header = points.first()
    points = points.filter(lambda row: row != header)
    points = points.map(lambda x: x.split(",")[0:2])
    points = points.map(lambda x: Rectangle(
        Point(int(x[0]), int(x[1])), Point(int(x[0]), int(x[1]))))

    # CREATING ENTRIES RDD
    points = points.zipWithIndex()
    entries = points.map(lambda x: Entry("E"+str(x[1]), x[0]))

    # CREATING RTREE
    tic = perf_counter()
    rtreeRDD = entries.mapPartitions(create_rtree)
    rtreeRDD.first()
    toc = perf_counter()
    time_treeCreation = toc - tic

    # PRINT RDD VALUES
    if printInConsole == True:
        rtreeRDD.foreach(lambda tree: print(repr(tree)))

    # RANGE QUERY
    range_rec = Rectangle(Point(400, 400), Point(6000, 6000))
    tic = perf_counter()
    resultRangeRDD = rtreeRDD.map(lambda tree: tree.range_query(range_rec))
    rangeRDD = resultRangeRDD.flatMap(lambda result: flatten_entries(result))
    toc = perf_counter()
    time_rangeQuery = toc - tic

    # PRINT RANGE ENTRIES
    if printInConsole == True:
        print("Range Entries")
        for value in rangeRDD.collect():
            print(value)

    # SKYLINE SEARCH
    resultSkylineRDD = rtreeRDD.map(lambda tree: tree.bbs_skyline())
    tic = perf_counter()
    skylineRDD = resultSkylineRDD.flatMap(
        lambda result: flatten_entries(result))
    # CREATING A LOCAL RTREE TO MERGE SKYLINE POINTS
    localRTree = RTree()
    skylineRDD.cache()
    for entry in skylineRDD.toLocalIterator():
        localRTree.insert(entry)
    if localRTree.root is not None:
        localSkylinePoints, _ = localRTree.bbs_skyline()
    toc = perf_counter()
    time_skylineSearch = toc - tic

    # PRINT SKYLINE POINTS IN CONSOLE
    if printInConsole == True:
        print("Skyline Points")
        for point in localSkylinePoints:
            print(point)

    # RANGE QUERY SKYLINE SEARCH
    resultQuerySkylineRDD = rtreeRDD.map(
        lambda tree: tree.bbs_skyline_range_query(range_rec))
    tic = perf_counter()
    querySkylineRDD = resultQuerySkylineRDD.flatMap(
        lambda result: flatten_entries(result))
    # CREATING A LOCAL RTREE TO MERGE SKYLINE POINTS FROM A RANGE QUERY
    querySkylineRDD.cache()
    localRTree = RTree()
    for entry in querySkylineRDD.toLocalIterator():
        localRTree.insert(entry)
    if localRTree.root is not None:
        localQuerySkylinePoints, _ = localRTree.bbs_skyline()
    toc = perf_counter()
    time_querySkylineSearch = toc - tic

    # PRINT SKYLINE POINTS GIVEN A RANGE QUERY IN CONSOLE
    if printInConsole == True:
        print("Skyline Points")
        for point in localQuerySkylinePoints:
            print(point)

    # PRINTING INFORMATION
    print("\nNumber of partitions: " + str(rtreeRDD.getNumPartitions()))
    print("Time elapsed creating the tree: {:0.3f}s".format(time_treeCreation))
    print("Time elapsed finding the Skyline points: {:0.3f}s".format(
        time_skylineSearch))
    print("Time elapsed finding the range query entries: {:0.3f}s".format(
        time_rangeQuery))
    print("Time elapsed finding the Skyline entries given a range: {:0.3f}s".format(
        time_querySkylineSearch))


def create_rtree(entries):
    rtree = RTree()
    for entry in entries:
        rtree.insert(entry)
    yield rtree


def flatten_entries(l):
    flat_list = []
    for sublist in l[0]:
        if isinstance(sublist, list):
            for item in sublist:
                flat_list.append(item)
        elif isinstance(sublist, Entry):
            flat_list.append(sublist)
    return flat_list


if __name__ == '__main__':
    main()
